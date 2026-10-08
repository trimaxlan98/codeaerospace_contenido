"""Escena: cámara, Tierra, atmósfera, estrellas, líneas, destellos, haces y mallas cercanas.

Dos escalas en el mismo cuadro:
* MUNDO en radios terrestres (TEME): Tierra, órbitas, haces, estaciones, Sol.
* LOCAL en metros alrededor de un ANCLA del mundo (el satélite): se dibuja después de
  borrar la profundidad, con su propia proyección, así un CubeSat de 34 cm y un planeta de
  12 742 km conviven sin pelear por la precisión del búfer de profundidad.
"""
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import moderngl
from PIL import Image

from . import mallas as Ma
from . import sombreadores as S
from .astro import R_TIERRA_KM, rz

TEXTURAS = Path(__file__).resolve().parents[1] / "assets" / "tierra"
M_POR_RT = R_TIERRA_KM * 1000.0


def perspectiva(fov_deg, aspecto, cerca, lejos):
    f = 1.0 / math.tan(math.radians(fov_deg) / 2)
    return np.array([[f / aspecto, 0, 0, 0], [0, f, 0, 0],
                     [0, 0, (lejos + cerca) / (cerca - lejos), 2 * lejos * cerca / (cerca - lejos)],
                     [0, 0, -1, 0]], "f4")


def mirar(ojo, objetivo, arriba):
    z = np.asarray(ojo, float) - np.asarray(objetivo, float)
    z /= np.linalg.norm(z)
    x = np.cross(arriba, z)
    if np.linalg.norm(x) < 1e-9:
        x = np.cross([0, 0, 1] if abs(z[2]) < 0.9 else [1, 0, 0], z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    R = np.stack([x, y, z])            # filas = ejes de la cámara
    return R


def _gl(m):
    """numpy (fila mayor) -> bytes columna mayor para GLSL."""
    return np.ascontiguousarray(np.asarray(m, "f4").T).tobytes()


@dataclass
class Camara:
    ojo: np.ndarray                     # radios terrestres, TEME
    objetivo: np.ndarray
    arriba: np.ndarray = field(default_factory=lambda: np.array([0, 0, 1.0]))
    fov: float = 40.0

    def rot(self):
        return mirar(self.ojo, self.objetivo, self.arriba)

    def vista_mundo(self):
        R = self.rot()
        V = np.eye(4)
        V[:3, :3] = R
        V[:3, 3] = -R @ np.asarray(self.ojo, float)
        return V

    def vista_local(self, ancla):
        """Vista para objetos en metros centrados en `ancla` (radios terrestres)."""
        R = self.rot()
        V = np.eye(4)
        V[:3, :3] = R
        V[:3, 3] = -R @ ((np.asarray(self.ojo, float) - np.asarray(ancla, float)) * M_POR_RT)
        return V


class Escena:
    def __init__(self, gpu, texturas=TEXTURAS, n_estrellas=9000):
        self.gpu, ctx = gpu, gpu.ctx
        self.ctx = ctx
        self.aspecto = gpu.W / gpu.H
        self.p_tierra = ctx.program(vertex_shader=S.VERT_TIERRA, fragment_shader=S.FRAG_TIERRA)
        self.p_atm = ctx.program(vertex_shader=S.VERT_TIERRA, fragment_shader=S.FRAG_ATMOSFERA)
        self.p_mat = ctx.program(vertex_shader=S.VERT_MALLA, fragment_shader=S.FRAG_MATERIAL)
        self.p_pts = ctx.program(vertex_shader=S.VERT_PUNTOS, fragment_shader=S.FRAG_PUNTOS)
        self.p_spr = ctx.program(vertex_shader=S.VERT_SPRITE, fragment_shader=S.FRAG_SPRITE)
        self.p_lin = ctx.program(vertex_shader=S.VERT_LINEA, geometry_shader=S.GEOM_LINEA,
                                 fragment_shader=S.FRAG_LINEA)
        self.p_haz = ctx.program(vertex_shader=S.VERT_TIERRA, fragment_shader=S.FRAG_HAZ)
        esf = Ma.esfera()
        self.vao_tierra = ctx.vertex_array(self.p_tierra, [(ctx.buffer(esf), "3f 3f 2f", "in_pos", "in_nrm", "in_uv")])
        atm = Ma.esfera(128, 64, 1.0)
        self.vao_atm = ctx.vertex_array(self.p_atm, [(ctx.buffer(atm), "3f 3f 2f", "in_pos", "in_nrm", "in_uv")])
        self.tex = {}
        for k, nombre in (("tdia", "world.topo.bathy.200412.3x5400x2700.jpg"),
                          ("tnoche", "BlackMarble_2016_01deg.jpg"), ("tnubes", "cloud_combined_2048.jpg")):
            im = Image.open(Path(texturas) / nombre).convert("RGB")
            t = ctx.texture(im.size, 3, im.tobytes())
            t.build_mipmaps()
            t.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
            t.anisotropy = 8.0
            self.tex[k] = t
        d, b, c = Ma.estrellas(n_estrellas)
        self.vao_pts = ctx.vertex_array(self.p_pts, [(ctx.buffer(np.concatenate([d, b[:, None], c], 1).astype("f4")),
                                                      "3f 1f 3f", "in_dir", "in_b", "in_col")])
        self.locales = {}
        self.cerca_mundo, self.lejos_mundo = 1e-4, 60.0

    # ---------- utilidades ----------
    def registrar_malla(self, nombre, verts):
        buf = self.ctx.buffer(verts)
        self.locales[nombre] = self.ctx.vertex_array(self.p_mat, [(buf, Ma.CAMPOS, *Ma.ATRIBUTOS)])

    def _P(self, cam, cerca, lejos):
        return perspectiva(cam.fov, self.aspecto, cerca, lejos)

    def proyectar(self, cam, p_mundo):
        """Coordenadas de pantalla (px, py) de un punto del mundo, o None si está detrás."""
        v = self._P(cam, self.cerca_mundo, self.lejos_mundo) @ cam.vista_mundo() @ np.append(p_mundo, 1.0)
        if v[3] <= 0:
            return None
        x, y = v[0] / v[3], v[1] / v[3]
        return ((x * 0.5 + 0.5) * self.gpu.W, (0.5 - y * 0.5) * self.gpu.H)

    # ---------- capas del mundo ----------
    def estrellas(self, cam, brillo=1.0):
        ctx = self.ctx
        ctx.disable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        V = cam.vista_mundo()
        V[:3, 3] = 0
        p = self.p_pts
        p["V"].write(_gl(V))
        p["P"].write(_gl(self._P(cam, 0.1, 100.0)))
        p["escala"] = self.gpu.H / 1080.0
        p["brillo"] = brillo
        self.vao_pts.render(moderngl.POINTS)

    def tierra(self, cam, gmst_rad, sol, sol_i=6.0, noche_i=1.0, nubes_du=0.0):
        ctx = self.ctx
        ctx.disable(moderngl.BLEND)
        ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        ctx.depth_func = "<"
        M = np.eye(4)
        M[:3, :3] = rz(gmst_rad)                                  # ECEF -> TEME
        p = self.p_tierra
        p["M"].write(_gl(M))
        p["V"].write(_gl(cam.vista_mundo()))
        p["P"].write(_gl(self._P(cam, self.cerca_mundo, self.lejos_mundo)))
        p["sol"] = tuple(sol)
        p["cam"] = tuple(cam.ojo)
        p["sol_i"], p["noche_i"], p["nubes_du"] = sol_i, noche_i, nubes_du
        for i, k in enumerate(("tdia", "tnoche", "tnubes")):
            self.tex[k].use(i)
            p[k] = i
        self.vao_tierra.render()

    def atmosfera(self, cam, sol, sol_i=22.0, alto_km=100.0, Hr_km=8.0, Hm_km=1.2):
        """Rayleigh (β del aire a nivel del mar, por radio terrestre) + Mie; escalas reales."""
        ctx = self.ctx
        ctx.disable(moderngl.DEPTH_TEST)
        ctx.enable(moderngl.BLEND | moderngl.CULL_FACE)
        ctx.front_face = "ccw"
        ctx.cull_face = "front"                                   # cara trasera: cubre disco y limbo
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        Ra = 1.0 + alto_km / R_TIERRA_KM
        M = np.diag([Ra, Ra, Ra, 1.0])
        p = self.p_atm
        p["M"].write(_gl(M))
        p["V"].write(_gl(cam.vista_mundo()))
        p["P"].write(_gl(self._P(cam, self.cerca_mundo, self.lejos_mundo)))
        p["cam"], p["sol"], p["sol_i"] = tuple(cam.ojo), tuple(sol), sol_i
        p["Ra"], p["Hr"], p["Hm"] = Ra, Hr_km / R_TIERRA_KM, Hm_km / R_TIERRA_KM
        p["bR"] = tuple(np.array([5.8e-6, 13.5e-6, 33.1e-6]) * M_POR_RT)
        p["bM"] = 21e-6 * M_POR_RT
        self.vao_atm.render()
        ctx.cull_face = "back"

    def lineas(self, cam, puntos, colores, grosor_px=2.0, oclusion=True):
        """Polilínea en el mundo: `puntos` Nx3, `colores` Nx4 (rgb HDR, alfa)."""
        if len(puntos) < 2:
            return
        ctx = self.ctx
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        ctx.disable(moderngl.CULL_FACE)
        if oclusion:
            ctx.enable(moderngl.DEPTH_TEST)
        else:
            ctx.disable(moderngl.DEPTH_TEST)
        self.gpu.fbo_ms.depth_mask = False
        pts = np.asarray(puntos, "f4")
        col = np.asarray(colores, "f4")
        seg = np.empty((2 * (len(pts) - 1), 7), "f4")
        seg[0::2, :3], seg[1::2, :3] = pts[:-1], pts[1:]
        seg[0::2, 3:], seg[1::2, 3:] = col[:-1], col[1:]
        buf = ctx.buffer(seg.tobytes())
        vao = ctx.vertex_array(self.p_lin, [(buf, "3f 4f", "in_pos", "in_col")])
        p = self.p_lin
        p["V"].write(_gl(cam.vista_mundo()))
        p["P"].write(_gl(self._P(cam, self.cerca_mundo, self.lejos_mundo)))
        p["pantalla"] = (self.gpu.W / 2, self.gpu.H / 2)
        p["grosor"] = grosor_px * self.gpu.H / 1080.0
        vao.render(moderngl.LINES)
        vao.release()
        buf.release()
        self.gpu.fbo_ms.depth_mask = True

    def destellos(self, cam, posiciones, tam_px, colores, oclusion=True):
        ctx = self.ctx
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        if oclusion:
            ctx.enable(moderngl.DEPTH_TEST)
        else:
            ctx.disable(moderngl.DEPTH_TEST)
        n = len(posiciones)
        datos = np.concatenate([np.asarray(posiciones, "f4").reshape(n, 3),
                                (np.asarray(tam_px, "f4").reshape(n, 1) * self.gpu.H / 1080.0),
                                np.asarray(colores, "f4").reshape(n, 3)], 1).astype("f4")
        buf = ctx.buffer(datos.tobytes())
        vao = ctx.vertex_array(self.p_spr, [(buf, "3f 1f 3f", "in_pos", "in_tam", "in_col")])
        self.p_spr["V"].write(_gl(cam.vista_mundo()))
        self.p_spr["P"].write(_gl(self._P(cam, self.cerca_mundo, self.lejos_mundo)))
        vao.render(moderngl.POINTS)
        vao.release()
        buf.release()

    def sol_disco(self, cam, sol, tam_px=90.0, intensidad=40.0):
        """El Sol como destello lejano (lo tapa la Tierra por profundidad)."""
        p = np.asarray(cam.ojo) + np.asarray(sol) * (self.lejos_mundo * 0.8)
        self.destellos(cam, [p], [tam_px], [np.array([1.0, 0.95, 0.88]) * intensidad])

    def haz(self, cam, apice, eje, largo, semiangulo_rad, color, intensidad=1.0):
        ctx = self.ctx
        v = Ma.cono(apice, eje, largo, semiangulo_rad)
        buf = ctx.buffer(v.tobytes())
        vao = ctx.vertex_array(self.p_haz, [(buf, "3f 3f 2f", "in_pos", "in_nrm", "in_uv")])
        ctx.enable(moderngl.BLEND | moderngl.DEPTH_TEST)
        ctx.disable(moderngl.CULL_FACE)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        p = self.p_haz
        p["M"].write(_gl(np.eye(4)))
        p["V"].write(_gl(cam.vista_mundo()))
        p["P"].write(_gl(self._P(cam, self.cerca_mundo, self.lejos_mundo)))
        p["color"], p["cam"], p["intensidad"] = tuple(color), tuple(cam.ojo), intensidad
        vao.render()
        vao.release()
        buf.release()

    # ---------- objetos cercanos (metros) ----------
    def malla(self, cam, nombre, R, ancla, sol, sol_i=3.0, tierra_luz=0.0, amb=0.004,
              cerca=0.02, lejos=5e4, escala=1.0):
        ctx = self.ctx
        ctx.disable(moderngl.BLEND)
        ctx.enable(moderngl.DEPTH_TEST)
        ctx.disable(moderngl.CULL_FACE)
        M = np.eye(4)
        M[:3, :3] = np.asarray(R) * escala
        V = cam.vista_local(ancla)
        p = self.p_mat
        p["M"].write(_gl(M))
        p["V"].write(_gl(V))
        p["P"].write(_gl(self._P(cam, cerca, lejos)))
        p["sol"] = tuple(sol)
        p["cam"] = tuple((np.asarray(cam.ojo) - np.asarray(ancla)) * M_POR_RT)
        p["sol_i"] = sol_i
        p["amb"] = (amb, amb * 1.1, amb * 1.3)
        td = -np.asarray(ancla, float)
        p["tierra_dir"] = tuple(td / np.linalg.norm(td))
        p["tierra_luz"] = (0.55 * tierra_luz, 0.7 * tierra_luz, 1.0 * tierra_luz)
        self.locales[nombre].render()
