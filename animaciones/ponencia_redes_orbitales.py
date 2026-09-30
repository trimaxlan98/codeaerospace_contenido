"""Ponencia «Redes orbitales: el siguiente paso, el siguiente salto de la economía».

Reutiliza los videos y stickers ya renderizados (no renderiza ni borra nada) y arma
exports/presentaciones/redes_orbitales_{oscuro,claro}.pptx con un hilo económico:
la infraestructura, la red, la integración, la autonomía, la confianza, la construcción,
la operación, los servicios y los límites.

Las diapositivas de video llevan un título-afirmación (las piezas no tienen títulos propios).
Sin cifras de mercado: cualquier número económico se añade a mano y con fuente.
Uso: python3 ponencia_redes_orbitales.py
"""
import sys
from pathlib import Path

from pptx.util import Inches, Pt

sys.path.insert(0, str(Path(__file__).parent))
from empaquetar_ponencia import (ACENTO, EXP, FONDO, H, TINTA, W, diapositiva, nombre_legible,  # noqa: E402
                                 nueva, poster, texto)
from catalogo import BLOQUES  # noqa: E402
from PIL import Image  # noqa: E402
import io  # noqa: E402

CARPETA = {p[0]: c for _, c, ps in BLOQUES for p in ps}
MUESTRA = {p[0]: p[1] for _, _, ps in BLOQUES for p in ps}

TITULO = "Redes orbitales"
LEMA = "El siguiente paso, el siguiente salto de la economía"

# (número, nombre del acto, idea del acto, [ (pieza, título de la diapositiva, nota para quien presenta) ])
ACTOS = [
    ("El espacio ya es infraestructura",
     "Como las carreteras o los puertos: algo que la economía da por hecho hasta que falta.",
     [("CaidaLibreNewton", "Un satélite no flota: cae y sigue cayendo",
       "Abrir con la intuición física. Todo lo que sigue descansa en esto."),
      ("OrbitasLEOMEOGEO", "Cada altura es un mercado distinto",
       "LEO, MEO y GEO: la altura decide cobertura, retardo y coste del servicio."),
      ("HuellaCobertura", "Más bajo, más cerca, pero se ve menos suelo",
       "Por eso LEO exige muchos satélites: el precio de la cercanía es la cantidad.")]),
    ("De un satélite a una red",
     "El salto económico no es el satélite: es que muchos satélites funcionen como un solo servicio.",
     [("WalkerDelta3D", "Una constelación es un sistema, no una flota",
       "Geometría pensada para cubrir. Ilustra el concepto, no una constelación concreta."),
      ("PlanosOrbitales", "La cobertura se compra satélite a satélite",
       "Cada satélite añade cobertura: base para hablar de inversión y escala."),
      ("ComparaLatencia", "La distancia es un costo que se paga en tiempo",
       "Solo propagación (física). Aplicaciones sensibles al retardo explican por qué LEO."),
      ("HandoverSatelital", "El usuario no ve satélites: ve continuidad",
       "El valor comercial es la continuidad del servicio, no el hardware."),
      ("MallaISL", "Los enlaces entre satélites son una red en el vacío",
       "Sin depender de estaciones en tierra en cada salto: nueva topología, nuevos modelos de negocio.")]),
    ("Tierra, aire y espacio: una sola red",
     "La visión 6G: la conectividad deja de ser territorial.",
     [("ZoologicoOrbital", "Cada plataforma cubre un hueco distinto",
       "HAPS, LEO, MEO y GEO como capas complementarias, no competidoras."),
      ("EspacioAireTierra", "La red integrada en tres niveles",
       "Un usuario, varias capas, un servicio."),
      ("ArquitecturaNTN", "El satélite entra al estándar móvil",
       "Redes no terrestres (NTN) en el marco 3GPP: interoperabilidad como palanca de mercado.")]),
    ("Redes que se gobiernan solas",
     "Con miles de nodos que cambian de posición, operar a mano no escala. La autonomía es un requisito económico.",
     [("TopologiaRespira", "La red cambia todo el tiempo",
       "Enlaces que aparecen y desaparecen: la operación manual no da abasto."),
      ("CicloPADA", "Percibir, analizar, decidir, actuar",
       "Arquitectura PADA de la tesis, mismo orden y nombres."),
      ("MuchosAgentesCTDE", "Se entrena en conjunto, se decide en cada nodo",
       "MARL con entrenamiento centralizado y ejecución descentralizada. En las pruebas: 3 agentes."),
      ("PoliticaEnrutaTrafico", "Una política que se adapta evita el cuello de botella",
       "Ilustrativo: sin cifras. Los resultados numéricos vienen de las compuertas, no de esta pieza."),
      ("IAaBordo", "Procesar en órbita es enviar menos a tierra",
       "Sin cifra: cada dato procesado a bordo es ancho de banda de bajada que se ahorra.")]),
    ("Confianza: validar antes de creer",
     "Una economía sobre redes autónomas necesita evidencia, no promesas.",
     [("SateliteMiente", "¿Y si un nodo miente?",
       "Consenso tolerante a fallos bizantinos: n ≥ 3f+1, quórum 2f+1. Caso ilustrativo (n=7, f=2)."),
      ("MargenAdaptativo", "Antes de evaluar la IA, evaluar si el banco puede distinguirla",
       "MA es propiedad del banco: 1.7 % en G0 → 31.8 % en G1. El umbral de 25 % es un criterio de diseño."),
      ("CompuertasValidacion", "Cada compuerta se gana",
       "G0, G1, G2a, G2b superadas; G3 pendiente. Decir que G3 está pendiente."),
      ("PipelineCompuertas", "Solo lo validado pasa a evaluación",
       "Ilustrativo. La filosofía: el banco se valida primero.")]),
    ("Construir y probar en tierra",
     "Cada hora de prueba en tierra es un riesgo menos en órbita, y una misión que sale más barata.",
     [("CubeSatDespiece", "El satélite bajo prueba",
       "CubeSat 3U como ejemplo de plataforma accesible."),
      ("BancoHardwareEnLaLazo", "El hardware real, en un cielo simulado",
       "Hardware-in-the-loop: hardware bajo prueba con simulador y canal."),
      ("EmuladorCanal", "El canal espacial, en la mesa del laboratorio",
       "Retardo, Doppler, atenuación y ruido. Valores estándar del ejemplo, no mediciones del banco."),
      ("GemeloDigitalSync", "El gemelo se corrige con lo que dice el satélite",
       "Gemelo digital sincronizado con telemetría.")]),
    ("Operar: apuntar, seguir, no perder el enlace",
     "La otra mitad del negocio es la estación en tierra.",
     [("CadenaTLEaAntena", "Del dato orbital al movimiento de la antena",
       "TLE → SGP4 → Az/El → controlador → motores."),
      ("AntenaSiguiendo", "La antena sigue al satélite",
       "Seguimiento sobre máscara de elevación (10° de ejemplo)."),
      ("GemeloDigitalATP", "Antena real y gemelo, sincronizados",
       "Puente entre operación y banco de pruebas.")]),
    ("Servicios en órbita y límites del crecimiento",
     "Nuevos mercados, y el costo de no cuidar el recurso.",
     [("ServicioEnOrbita", "Reparar, reabastecer, extender vida útil",
       "El satélite deja de ser desechable: nueva línea de servicios."),
      ("EnjambreRobots", "Coordinación autónoma también en órbita",
       "Robots cooperando: continuación natural de la autonomía."),
      ("BasuraEspacial", "El crecimiento tiene un límite físico",
       "Efecto Kessler. Sin esto no hay economía orbital sostenible.")]),
]

# Diapositivas de texto entre actos: (título, [viñetas], sticker opcional (pieza))
ECONOMIA = [
    ("De dónde sale el valor",
     ["Conectividad donde no llega la fibra: agro, minería, logística, mar y aire",
      "Servicios sensibles al tiempo: sincronía, trazabilidad, respuesta a emergencias",
      "Datos desde el espacio, procesados en el borde, entregados como decisión",
      "Costos que bajan cuando la red se opera y se valida en automático"],
     "Tierra3DSatelites"),
    ("Qué necesita para ocurrir",
     ["Estándares abiertos que permitan integrar tierra y espacio",
      "Espectro coordinado y órbitas sostenibles",
      "Autonomía verificable: validar antes de desplegar",
      "Talento y bancos de prueba locales"],
     "PlanosOrbitales"),
    ("Dónde entra Co.De Aerospace",
     ["Banco de pruebas y gemelo digital",
      "Seguimiento satelital (ATP)",
      "IA para gobernar redes NTN, con evidencia",
      "Una cadena completa: del modelo al hardware"],
     "CubeSatDespiece"),
]


def sticker(tema, clase):
    src = EXP / "png" / "stickers" / tema / CARPETA[clase] / f"{clase}.png"
    im = Image.open(src).convert("RGBA")
    im.thumbnail((1800, 1800), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "PNG", compress_level=6)
    b.seek(0)
    return b, im.size


def portada(prs, tema):
    s = diapositiva(prs, tema)
    texto(s, TITULO, Inches(0.9), Inches(2.2), Inches(11.5), Inches(1.6), 72, TINTA[tema], True)
    texto(s, LEMA, Inches(0.9), Inches(3.8), Inches(11.5), Inches(1.4), 34, ACENTO[tema])
    texto(s, "Co.De Aerospace", Inches(0.9), Inches(6.4), Inches(6), Inches(0.6), 20, TINTA[tema])
    return s


def seccion(prs, tema, n, nombre, idea):
    s = diapositiva(prs, tema)
    texto(s, f"{n:02d}", Inches(0.9), Inches(2.2), Inches(4), Inches(1.2), 54, ACENTO[tema], True)
    texto(s, nombre, Inches(0.9), Inches(3.3), Inches(11.5), Inches(1.4), 42, TINTA[tema], True)
    texto(s, idea, Inches(0.9), Inches(4.9), Inches(11), Inches(1.4), 24, TINTA[tema])
    return s


def con_video(prs, tema, clase, titulo, nota):
    mp4 = EXP / CARPETA[clase] / tema / f"{clase}.mp4"
    if not mp4.exists():
        print("falta", mp4)
        return
    s = diapositiva(prs, tema)
    texto(s, titulo, Inches(0.6), Inches(0.25), Inches(12.1), Inches(0.8), 30, TINTA[tema], True)
    vh = Inches(6.2)
    vw = int(vh * 16 / 9)
    s.shapes.add_movie(str(mp4), int((W - vw) / 2), Inches(1.1), vw, vh,
                       poster_frame_image=poster(tema, CARPETA[clase], clase), mime_type="video/mp4")
    s.notes_slide.notes_text_frame.text = f"{nota}\n\n[{nombre_legible(clase)}] {MUESTRA[clase]}."


def con_texto(prs, tema, titulo, puntos, clase):
    s = diapositiva(prs, tema)
    texto(s, titulo, Inches(0.7), Inches(0.5), Inches(12), Inches(1), 38, TINTA[tema], True)
    tb = s.shapes.add_textbox(Inches(0.7), Inches(1.9), Inches(6.6), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, t in enumerate(puntos):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(16)
        r = p.add_run()
        r.text = "▪ " + t
        r.font.size, r.font.name = Pt(24), "Carlito"
        r.font.color.rgb = TINTA[tema]
    buf, (iw, ih) = sticker(tema, clase)
    esc = min(Inches(5.4) / iw, Inches(5.2) / ih)
    w, h = int(iw * esc), int(ih * esc)
    pic = s.shapes.add_picture(buf, Inches(7.6) + int((Inches(5.4) - w) / 2), int((H - h) / 2) + Inches(0.3), w, h)
    pic._element.nvPicPr.cNvPr.set("descr", f"{nombre_legible(clase)}: {MUESTRA[clase]}")
    s.notes_slide.notes_text_frame.text = (
        "Diapositiva de argumento. Sin cifras de mercado: si se cita una, poner fuente y fecha en pantalla.")


def construir(tema):
    prs = nueva(tema)
    portada(prs, tema)
    for i, (nombre, idea, piezas) in enumerate(ACTOS, 1):
        seccion(prs, tema, i, nombre, idea)
        for clase, titulo, nota in piezas:
            con_video(prs, tema, clase, titulo, nota)
        if i == 3:
            con_texto(prs, tema, *ECONOMIA[0])
        if i == 5:
            con_texto(prs, tema, *ECONOMIA[1])
    con_texto(prs, tema, *ECONOMIA[2])
    s = diapositiva(prs, tema)
    texto(s, "El siguiente salto empieza en órbita", Inches(0.9), Inches(2.6), Inches(11.5), Inches(1.4), 48,
          TINTA[tema], True)
    texto(s, "Gracias · Preguntas", Inches(0.9), Inches(4.2), Inches(11.5), Inches(1), 30, ACENTO[tema])
    destino = EXP / "presentaciones" / f"redes_orbitales_{tema}.pptx"
    prs.save(destino)
    print(destino.name, len(prs.slides), "diapositivas", f"{destino.stat().st_size / 1e6:.0f} MB")


if __name__ == "__main__":
    for t in ("oscuro", "claro"):
        construir(t)
