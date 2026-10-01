"""Español → inglés de los textos que hay DENTRO de los videos Manim y de la interfaz de las diapositivas.

Uso en los videos: `CODE_IDIOMA=en` (ver code_lib.py) llama a `traducir(texto, clase)` por cada Text().
Es ESTRICTO: una cadena con letras que no esté aquí aborta el render con el texto que falta, para que nada
quede a medias en español. Las cifras sin letras ("16,279", "86.8") no pasan por aquí.
Terminología de la tesis (borrador en inglés PAPER_v1_DRAFT.md): Adaptive Margin (MA), best fixed policy,
validity gate, pre-registered, testbed, oracle, seeds, Dec-POMDP. Etiquetas ≤ 3 palabras, como en español.
Para registrar una pieza nueva: `CODE_LOG_TEXTOS=/tmp/t.jsonl manim render -ql --dry_run ... Clase` lista sus textos.
"""

# cadenas que se conservan tal cual (siglas, nombres propios, cifras con unidad, símbolos)
IGUAL = {
    "ASTREA 2025", "1.54 B", "90 min", "15 min", "NASA 2023-24", "4 CubeSats", "Starlink", "ECSS-E-ST-70-11C", "Rev.1",
    "IETF, 3GPP, ETSI", "IETF", "3GPP", "ETSI", "6G", "IETF 2026", "NTN", "A", "B", "Ellis 2023", "Yılmaz 2026", "QMIX",
    "n = 3", "G0", "G1", "G2a", "G2b", "G3", "G4", "MA 0.318", "v1", "v2", "Mock", "π(t)", "π(o)", "A − B", "p", "MVP1",
    "MVP2", "MVP3", "MVP4", "MVP5", "G0–G2b", "WITCOM", "Feb 2026", "Feb 2030",
}

TRAD = {
    # ASTREA
    "Controlador": "Controller", "Térmico": "Thermal", "Decide": "Decides", "Modelo pequeño": "Small model",
    "Aconseja": "Advises", "Preprint, n pequeño": "Preprint, small n", "Temperatura": "Temperature",
    "Referencia": "Reference",
    # Starling y escala
    "Reglas": "Rules", "Solo simulación": "Simulation only", "60 naves": "60 spacecraft",
    "McDowell ago-2026": "McDowell Aug 2026", "Activos": "Active", "Maniobrables": "Maneuverable",
    "Un operador": "One operator",
    # norma y estándares
    "ECSS oct-2025": "ECSS Oct 2025", "Autonomía": "Autonomy", "Inteligencia artificial": "Artificial intelligence",
    "Aprendizaje automático": "Machine learning", "Constelación": "Constellation", "Agentes de red": "Network agents",
    "Ahora": "Now", "Borradores": "Drafts", "Estudios": "Studies", "Especificaciones": "Specifications",
    "Borrador IETF": "IETF draft", "DEBE": "MUST", "NO DEBE": "MUST NOT", "satélite": "satellite",
    # termómetro, política, semillas
    "Médico A": "Doctor A", "Médico B": "Doctor B", "Ilustrativo": "Illustrative", "Gana B": "B wins", "Gana": "Wins",
    "Observa": "Observes", "Sin observar": "No observation", "Reloj": "Clock", "5 semillas": "5 seeds",
    "10 semillas": "10 seeds", "Fútbol, no NTN": "Soccer, not NTN", "Aleatoria": "Random",
    # PADA, modelo, agente
    "Telemetría": "Telemetry", "Ventana limitada": "Limited window", "Traduce intención": "Translates intent",
    "Decide rápido": "Decides fast", "Percepción": "Perception", "Análisis": "Analysis", "Decisión": "Decision",
    "Acción": "Action", "Lento": "Slow", "Rápido": "Fast", "En desarrollo": "In development", "Núcleo": "Core",
    "Transporte": "Transport", "Capa radio": "Radio layer", "Recompensa común": "Shared reward",
    "Energía finita": "Finite energy", "Contacto intermitente": "Intermittent contact",
    "Límites regulatorios": "Regulatory limits", "Hueco abierto": "Open gap",
    # margen y compuertas
    "Mejor fija": "Best fixed", "Mejor adaptable": "Best adaptive", "Margen grande": "Large margin",
    "Margen cero": "Zero margin", "Umbral 25 %": "Threshold 25%", "Pre-registrado": "Pre-registered",
    "Pasa": "Passes", "No se reportan": "Not reported", "No se reporta": "Not reported",
    "Alcanzable 9.5 %": "Achievable 9.5%", "Anulado": "Voided", "Mejor estática": "Best fixed",
    "Información privilegiada": "Privileged information", "Semilla 42": "Seed 42", "Semilla 43": "Seed 43",
    "Semilla 44": "Seed 44", "Mezcla no lineal": "Nonlinear mixing", "Suma simple": "Simple sum",
    "Diagnóstico": "Diagnostic", "Propuesto": "Proposed", "2 satélites": "2 satellites",
    "Órbitas reales": "Real orbits", "¿Sobrevive?": "Survives?", "Hoy": "Today", "Vocabulario se fija": "Vocabulary is set",
    "Freeze 6G": "6G freeze", "Defensa": "Defense",
    # piezas del comité usadas como sticker
    "Entrenadas": "Trained", "Sin corrección": "No correction", "Con corrección": "With correction",
    "Margen ≈ 0": "Margin ≈ 0", "Solo el tiempo": "Time only", "Observa estado": "Observes state", "Pendiente": "Pending",
    "Umbral 0.25": "Threshold 0.25", "Holgura no acotada": "Unbounded slack", "Pierde": "Loses", "Mide": "Measures",
    "Significa algo": "Means something", "Plan propuesto": "Proposed plan", "G3 pendiente": "G3 pending",
    "Semestre 2/8": "Semester 2/8", "Agente": "Agent", "Entorno": "Environment", "acción": "action", "estado": "state",
    "recompensa": "reward", "Episodios": "Episodes", "Recompensa": "Reward",
}

# excepciones por pieza (clase → {español: inglés}); úsalo solo si una misma cadena necesita otra traducción según el contexto
POR_CLASE = {}


def traducir(texto, clase=""):
    if texto in POR_CLASE.get(clase, {}):
        return POR_CLASE[clase][texto]
    if texto in TRAD:
        return TRAD[texto]
    if texto in IGUAL:
        return texto
    raise KeyError(f"[{clase}] sin traducción al inglés: {texto!r} (agrégala a traducciones_en.py)")


# piezas sin texto con letras: el video en español sirve tal cual en el deck en inglés
SIN_TEXTO = {"Tierra3DSatelites", "CoberturaHexagonal"}

# nombre legible en inglés (pie de los stickers «FIG · …», canal del monitor, texto alternativo)
NOMBRES = {
    "AstreaAconseja": "ASTREA advises", "AstreaRitmoOrbita": "ASTREA orbital pace", "StarlingCuatroNaves": "Starling, four craft",
    "AritmeticaDeLaEscala": "The arithmetic of scale", "NormaSinIA": "Standard without AI",
    "EstandaresEscribenAhora": "Standards written now", "BuscarSatelite": "Searching “satellite”",
    "TermometroRoto": "Broken thermometer", "PoliticaQueNoMira": "Policy that doesn't look",
    "SemillasQueInvierten": "Seeds that flip", "ModeloArribaRLAbajo": "Language on top, RL below",
    "PadaCuatroCajas": "PADA, four boxes", "DecisionConjunta": "Joint decision", "SateliteDeviceAgent": "Satellite device agent",
    "MargenAdaptativoIdea": "Adaptive Margin idea", "CompuertaAntesDeCorrer": "Gate before running",
    "RecorridoDelMargen": "The margin's path", "AlgoritmoVsEstatica": "Algorithm vs fixed policy",
    "VarianteSimpleNoEmpeora": "Simple variant holds up", "SimuladorMasReal": "A more realistic simulator",
    "PrisaDosMilVeintinueve": "The 2029 rush", "SignoQueInvierte": "The sign flips", "LazoAbiertoGana": "Open loop wins",
    "ProtocoloCompuertas": "Gate protocol", "ParMargenAdaptativo": "Adaptive Margin pair",
    "CierreMedicionSignifica": "Measurement means something", "CronogramaDoctoral": "Doctoral timeline",
    "AgenteAprende": "Agent learns", "Tierra3DSatelites": "Earth and satellites, 3D", "CoberturaHexagonal": "Hexagonal coverage",
}

BLOQUES = {
    "Órbita, escala y estándares": "Orbit, scale and standards", "El examen y la arquitectura": "The exam and the architecture",
    "Resultados y prisa": "Results and urgency", "Problema y estado del arte": "Problem and state of the art",
    "El marco propuesto": "The proposed framework", "Evidencia y limitaciones": "Evidence and limitations",
    "Alcance, plan y cierre": "Scope, plan and close",
}

# textos de interfaz de las diapositivas (decks_espaciales.py): clave española → inglés
UI = {
    "SECCIÓN": "SECTION", "PIEZAS EN ESTA SECCIÓN": "CLIPS IN THIS SECTION", "RESPALDO  ·  PREGUNTAS": "BACKUP  ·  Q&A",
    "RESPALDO": "BACKUP", "VOZ": "VOICE", "GRACIAS  ·  PREGUNTAS": "THANK YOU  ·  QUESTIONS", "CANAL": "CHANNEL",
    "CUIDADO": "CAUTION", "LAT_LON": "LAT 19.43° N   LON 99.13° W   ·   MEXICO CITY",
    "video_nota": "Click to play; it holds on the last frame when it ends.",
}
