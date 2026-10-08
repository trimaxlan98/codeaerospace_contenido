"""Contexto GPU sin pantalla (EGL), búfer HDR con MSAA y posproceso (bloom + ACES)."""
import numpy as np
import moderngl

from . import sombreadores as S


class GPU:
    def __init__(self, ancho=1920, alto=1080, muestras=4):
        self.ctx = ctx = moderngl.create_standalone_context(backend="egl", require=430)
        self.W, self.H = ancho, alto
        self.render = ctx.info["GL_RENDERER"]
        self._color = ctx.renderbuffer((ancho, alto), 4, samples=muestras, dtype="f2")
        self._prof = ctx.depth_renderbuffer((ancho, alto), samples=muestras)
        self.fbo_ms = ctx.framebuffer([self._color], self._prof)
        self.hdr = ctx.texture((ancho, alto), 4, dtype="f2")
        self.hdr.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.fbo_hdr = ctx.framebuffer([self.hdr])
        # cadena de bloom: 1/2, 1/4, 1/8, 1/16 (dos texturas por nivel para el desenfoque separable)
        self.niveles = []
        w, h = ancho // 2, alto // 2
        for _ in range(4):
            a = ctx.texture((w, h), 4, dtype="f2")
            b = ctx.texture((w, h), 4, dtype="f2")
            for t in (a, b):
                t.filter = (moderngl.LINEAR, moderngl.LINEAR)
                t.repeat_x = t.repeat_y = False
            self.niveles.append((a, ctx.framebuffer([a]), b, ctx.framebuffer([b]), (w, h)))
            w, h = max(1, w // 2), max(1, h // 2)
        self.ldr = ctx.texture((ancho, alto), 3)
        self.fbo_ldr = ctx.framebuffer([self.ldr])
        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4"))
        self.p_brillo = ctx.program(vertex_shader=S.VERT_PANTALLA, fragment_shader=S.FRAG_BRILLO)
        self.p_blur = ctx.program(vertex_shader=S.VERT_PANTALLA, fragment_shader=S.FRAG_BLUR)
        self.p_final = ctx.program(vertex_shader=S.VERT_PANTALLA, fragment_shader=S.FRAG_FINAL)
        self.q_brillo = ctx.vertex_array(self.p_brillo, [(quad, "2f", "in_pos")])
        self.q_blur = ctx.vertex_array(self.p_blur, [(quad, "2f", "in_pos")])
        self.q_final = ctx.vertex_array(self.p_final, [(quad, "2f", "in_pos")])
        ctx.enable(moderngl.PROGRAM_POINT_SIZE)

    def empezar(self, fondo=(0.0, 0.0, 0.0)):
        self.fbo_ms.use()
        self.ctx.viewport = (0, 0, self.W, self.H)
        self.fbo_ms.clear(*fondo, 1.0, depth=1.0)

    def limpiar_profundidad(self):
        """Borra solo la profundidad (glClear respeta la máscara de color): entre la pasada del
        mundo (radios terrestres) y la de los objetos cercanos (metros)."""
        self.fbo_ms.use()
        self.fbo_ms.depth_mask = True
        self.fbo_ms.color_mask = (False, False, False, False)
        self.fbo_ms.clear(depth=1.0)
        self.fbo_ms.color_mask = (True, True, True, True)

    def terminar(self, exposicion=1.0, bloom=0.6, umbral=1.0, vineta=0.35, fundido=1.0) -> np.ndarray:
        ctx = self.ctx
        ctx.disable(moderngl.DEPTH_TEST | moderngl.BLEND | moderngl.CULL_FACE)
        ctx.copy_framebuffer(self.fbo_hdr, self.fbo_ms)           # resolver MSAA
        src = self.hdr
        for i, (a, fa, b, fb, (w, h)) in enumerate(self.niveles):
            ctx.viewport = (0, 0, w, h)
            fa.use()
            if i == 0:
                src.use(0)
                self.p_brillo["src"] = 0
                self.p_brillo["umbral"] = umbral
                self.q_brillo.render(moderngl.TRIANGLE_STRIP)
            else:
                src.use(0)                                       # reducir el nivel anterior
                self.p_brillo["src"] = 0
                self.p_brillo["umbral"] = 0.0
                self.q_brillo.render(moderngl.TRIANGLE_STRIP)
            for direc, (lee, escribe) in (((1.0 / w, 0.0), (a, fb)), ((0.0, 1.0 / h), (b, fa))):
                escribe.use()
                lee.use(0)
                self.p_blur["src"] = 0
                self.p_blur["dir"] = direc
                self.q_blur.render(moderngl.TRIANGLE_STRIP)
            src = a
        ctx.viewport = (0, 0, self.W, self.H)
        self.fbo_ldr.use()
        self.hdr.use(0)
        for k, (a, *_r) in enumerate(self.niveles):
            a.use(k + 1)
        p = self.p_final
        p["hdr"], p["b1"], p["b2"], p["b3"], p["b4"] = 0, 1, 2, 3, 4
        p["exposicion"], p["bloom"], p["vineta"], p["fundido"] = exposicion, bloom, vineta, fundido
        self.q_final.render(moderngl.TRIANGLE_STRIP)
        datos = self.fbo_ldr.read(components=3, alignment=1)
        return np.frombuffer(datos, np.uint8).reshape(self.H, self.W, 3)[::-1].copy()
