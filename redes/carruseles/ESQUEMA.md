# Carruseles de Instagram — esquema y reglas de contenido

El motor (`motor_carrusel.py`) pone el diseño. Tú pones el contenido en un JSON por carrusel, en
`redes/carruseles/specs/<serie>/<id>.json`. Formato 1080×1350 (4:5), de 3 a 10 láminas.

```
python3 motor_carrusel.py --validar specs/<serie>/<id>.json   # valida
python3 motor_carrusel.py specs/<serie>/<id>.json             # renderiza → exports/estudio/carruseles/<serie>/<id>/
```
Salida: `<id>_01.png …`, `<id>_hoja.jpg` (hoja de contacto: MÍRALA), `<id>_pie.txt` (texto de la publicación) y,
si hay advertencias, `<id>_CUIDADO.txt`.

## JSON

```json
{
  "id": "kebab-case-unico",
  "serie": "nombre-de-la-serie",
  "fondo": {"tema": "orbita", "tipo": "portada", "var": 0},
  "laminas": [ {"tipo": "portada", ...}, ..., {"tipo": "cierre", ...} ],
  "fuentes": ["codeaerospace.com/plataformas (consultado 2026-10-01)"],
  "pie_texto": "Texto de la publicación (gancho + 2–4 frases + llamada a guardar/compartir) y 3–6 hashtags.",
  "cuidado": ["Lo que hay que confirmar antes de publicar (opcional)"]
}
```

`fondo.tema`: entorno espacial (solo OSCUROS): `orbita` (oficial), `mision`, `nebulosa`, `lunar`, `marte`, `solar`,
`fisica`, `espectro`, `electromagnetismo`, `lanzamiento`, `robotica`, `electronica`, `neuronal`, `caos`,
`aerodinamica`, `calculo`. `tipo`: `portada` (paisaje con horizonte planetario que cruza las láminas: el más vistoso),
`seccion`, `contenido` (sobrio), `cierre`. `var`: 0–3 cambia la semilla. El fondo es UNA panorámica de todo el
carrusel cortada en láminas: el horizonte continúa al deslizar.

Sello de rigor (cualquier lámina): `"sello": "ilustracion" | "simulacion" | "grabacion" | "beta" | "meta" | "dato"` («dato» = calculado con datos reales y su época) pone una
etiqueta ámbar abajo a la derecha. Úsalo SIEMPRE que la lámina muestre algo ilustrativo, simulado, una grabación
(no en vivo), una beta o una meta (no un hecho).

Énfasis dentro de cualquier texto: `[[palabra]]` sale en cian (1–3 por lámina, no más); `**palabra**` en negrita.

Variantes A/B (opcional, para medir qué funciona): `"variantes": [{"sufijo": "b", "portada": {"titulo": "otro gancho"},
"fondo": {"tema": "nebulosa"}}]` renderiza además `<id>-b` con la portada/fondo/cierre/pie cambiados. Cambia UNA
variable por variante (solo el gancho, o solo el fondo) para que la comparación diga algo.

## Tipos de lámina (campos; * = obligatorio)

| tipo | campos | límites recomendados |
|---|---|---|
| `portada` | titulo*, kicker, subtitulo, imagen, logo (bool, por defecto true si no hay imagen) | título ≤ 55 car. (gancho), subtítulo ≤ 80 |
| `texto` | titulo*, numero ("01"), kicker, cuerpo, imagen | título ≤ 50, cuerpo ≤ 240 (con imagen ≤ 160) |
| `dato` | cifra*, titulo*, unidad, kicker, nota | cifra ≤ 7 car.; nota = de dónde sale la cifra |
| `lista` | titulo*, items* (2–5), kicker | cada ítem ≤ 60 |
| `pasos` | titulo*, pasos* [{t, d}] (3–5), kicker | t ≤ 22, d ≤ 60 |
| `comparacion` | titulo*, izq* {t, items}, der* {t, items}, kicker | 2–4 ítems por lado, ≤ 40 car. |
| `termino` | termino*, definicion*, nombre (expansión de la sigla), ejemplo, kicker, imagen | término ≤ 12 car.; definición ≤ 160 — para GLOSARIOS |
| `formula` | formula*, titulo, kicker, pasos (lista de sustituciones), resultado, nota | fórmula ≤ 24 car. (admite λ Δ μ √ ≈ subíndices); muestra el cálculo, no solo la cifra |
| `grafica` | titulo*, x*, y* (listas ≥ 10 puntos), y_escala, y_unidad, y_etiqueta, x_etiqueta, x_modo ("mmss"), marcas [{x, texto, lado}], nota | UNA serie; el título dice qué se grafica (sin leyenda); etiqueta solo 2–3 puntos; la procedencia de los datos va en `nota`. Se genera desde datos con `generar_desde_datos.py` |
| `cita` | frase*, autor | frase ≤ 110 |
| `imagen` | imagen*, titulo, kicker, pie | pie ≤ 150 |
| `cierre` | titulo*, texto, cta (lista de 2–3 palabras) | título ≤ 45 |

`imagen`: `sticker:<carpeta>/<Clase>` (ilustraciones Manim con el estilo de la marca, fondo transparente),
`logo`, `marca:emblema-plata`, `marca:simbolo-plata`, `marca:logo-cian`.

Stickers publicables (`exports/png/stickers_finales/t_orbita/`), MÍRALOS antes de usarlos:
- espacio_orbitas: BasuraEspacial, CaidaLibreNewton, HuellaCobertura, OrbitasLEOMEOGEO, Tierra3DSatelites, TransferenciaHohmann, TrazaTerrestre
- constelaciones: CoberturaHexagonal, ComparaLatencia, EnjambreDespliegue, HandoverSatelital, MallaISL, PlanosOrbitales, TopologiaRespira, WalkerDelta3D
- ntn_6g: ArquitecturaNTN, EspacioAireTierra, Interferencia, ZoologicoOrbital
- seguidor_satelital: AntenaSiguiendo, CadenaTLEaAntena, DopplerEnS, GemeloDigitalATP, Keyhole, LazoPID, MontajeAzEl, NochePases, VistaPolarPase
- ia_satelites: AgenteAprende, GrafoGNN, IAaBordo, MuchosAgentesCTDE, PoliticaEnrutaTrafico, SateliteMiente
- banco_pruebas: BancoHardwareEnLaLazo, CubeSatDespiece, EmuladorCanal, GemeloDigitalSync, TelemetriaEnVivo
- antenas_robots: EspectroFourier, SDRAntenaANumero, ServicioEnOrbita
- plataformas (NUEVOS, propios de Co.De): BusNexus (CODE-Nexus y sus 6 servicios), TriageCascadas (CNN que separa pases con/sin señal), RielTelemetria (PiStation: Raspberry Pi + telemetría con banda ±3σ y una anomalía), UnPaseCincoPlataformas (un pase → rastreo, recepción, clasificación, bus, gemelo)

PROHIBIDO: cualquier `tesis_*` y CicloPADA, CompuertasValidacion, MargenAdaptativo, PipelineCompuertas (son de una
tesis doctoral privada; el motor los rechaza). Las cifras DENTRO de los stickers son ilustrativas: nunca las cites
como dato.

## Diseño: lo que funciona mejor (aprendido en la ronda 1)

- La PORTADA sin `imagen` pone el logo grande: si todas las portadas son así, el feed se ve repetido. Usa un sticker en
  la portada cuando el tema tenga uno bueno (se amplía a lo ancho).
- Las láminas de contenido se centran solas en vertical; un `texto` corto con `imagen` da el sticker GRANDE.
- `comparacion` apila dos tarjetas a todo el ancho (ideal mito/realidad; usa `sello: "mito"` / `"realidad"` si sirve).
- Fondos con decoración fuerte (`solar`, `fisica`, `caos`, `calculo`, `neuronal`): si cruza el texto, cambia `var`,
  usa `tipo: "contenido"` o sube `"atenuar"` (0–0.6; por defecto 0.22) en `fondo`.
- Las cifras de `dato` llevan fecha o fuente en `nota` (si no, el validador avisa).

## Reglas de contenido (no negociables)

1. **Solo hechos con fuente.** Lo de Co.De sale de `redes/fuentes/` (textos de codeaerospace.com/plataformas y
   /services, 2026-10-01) y de `animaciones/presentaciones/que_es_code.json`. La ciencia general (órbitas, Doppler,
   espectro) debe ser correcta de libro; usa valores estándar (GEO 35 786 km, ISS ~400 km y ~92 min). Si no estás
   seguro de una cifra, no la pongas.
2. **Respeta las advertencias de la fuente**, al pie de la letra:
   - Orbit Eye: obra derivada de ground-station (GPL-3.0, Stratos Goudelis); este despliegue NO tiene receptor de
     radio conectado: la recepción se demuestra con grabaciones IQ.
   - SAT-DT: TLE reales, telemetría SIMULADA; QMIX es un piloto sin validar (no lo vendas como logro).
   - PADA NTN Testbed: los 5.5 s son UNA observación; no es mediana.
   - PiStation: modo por defecto = simulador; watchdog, GNSS, Sense HAT y SDR solo simulados; los APT decodificados son
     grabaciones históricas de SatNOGS.
   - ATP-DT: beta, banco de pruebas de diseño (presupuesto de apuntamiento de 0.1°).
   - CO.DE Triage: el CLASIFICADOR (CNN) tiene AUC 0.949 en un test intacto de 731 observaciones. El 0.806 es del
     PRONÓSTICO de calidad (página pública Score Your Pass, estudio caso-control de 7 499 observaciones) en estaciones no
     vistas: NO es del clasificador. Nunca los compares como si fueran el mismo modelo.
   - Matriz de capacidad de /services = autoevaluación interna: no la publiques como dato.
   - Cifras de la página verificadas el 2026-07-30 (las de eventos/observaciones envejecen).
   - WRC-27: lo que diga la fuente; sede y fecha exactas → `cuidado`.
3. **Sin nombres de clientes** ni proyectos de clientes (consultorio, despacho, gimnasio…). Habla de tecnología.
4. **Nada de la tesis doctoral** (PADA, Margen Adaptativo, compuertas G0–G4, QMIX como resultado).
5. **Voz**: español latinoamericano, tuteo, claro y entusiasta sin exagerar; cero «revolucionario», «el mejor»,
   «líder». Precisión antes que épica (es el tono de la marca: «lo que no se pudo comprobar no está en esta página»).
6. **Estructura**: lámina 1 = gancho (pregunta, dato sorprendente o promesa concreta); una idea por lámina; ritmo
   variado (alterna tipos); penúltima o última = resumen/valor; cierre con llamada a guardar/compartir/seguir.
   6–8 láminas es lo ideal.
7. Si algo depende de confirmar, ponlo en `cuidado`.
8. **Los stickers no deben contradecir el texto vecino**: si el sticker muestra otra cifra (p. ej. ComparaLatencia da
   ida y vuelta completa 4·d/c; OrbitasLEOMEOGEO dibuja LEO a 550 km), o cambias de sticker o lo aclaras en la lámina.
9. **No generalices un principio más allá de su fuente**: «la IA explica y redacta; no decide ni actúa» es de los
   COPILOTOS (y PiStation es la excepción); Co.De también tiene un clasificador que emite veredictos.
10. Un carrusel puede llevar `"estado": "no_publicar"` (borrador o descartado): el índice lo marca ⛔.
