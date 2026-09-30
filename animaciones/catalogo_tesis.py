"""Catálogo de las piezas de la tesis doctoral (seminario de divulgación y comité tutorial).

(clase, qué muestra, cuándo usarla)  — la carpeta de video es el nombre del archivo .py.
Fuente única para tesis_decks.py y sus dos presentaciones. Las piezas de la ponencia Co.De
siguen en catalogo.py; estas son específicas de la tesis «Gobernanza autónoma de redes programables».
"""

SEMINARIO = [
    ("Órbita, escala y estándares", "tesis_sem_1_orbita", [
        ("AstreaAconseja", "Un modelo pequeño aconseja y un controlador decide sobre el sistema térmico", "Abrir: qué hizo ASTREA en la ISS"),
        ("AstreaRitmoOrbita", "Consejos cada 15 min empeoran; alineados al periodo orbital (90 min) mejoran", "La lección: el ritmo equivocado"),
        ("StarlingCuatroNaves", "Cuatro CubeSats se coordinan con reglas; 60 naves solo en simulación", "La coordinación autónoma ya voló"),
        ("AritmeticaDeLaEscala", "16,279 satélites, 10,742 de Starlink, 86.8 % maniobrables, un operador", "Por qué automatizar es aritmética"),
        ("NormaSinIA", "La norma ECSS: 81 veces «autonomía», cero veces IA o constelación", "El marco normativo aún no existe"),
        ("EstandaresEscribenAhora", "IETF, 3GPP y ETSI escriben las reglas de agentes de red rumbo al freeze 2029", "El vocabulario se fija ahora"),
        ("BuscarSatelite", "Una lupa busca «satélite» en un borrador del IETF: cero coincidencias", "Dónde encaja el trabajo de un doctorando"),
    ]),
    ("El examen y la arquitectura", "tesis_sem_2_examen", [
        ("TermometroRoto", "Dos médicos con un termómetro que marca 37° siempre", "El giro: la analogía del instrumento roto"),
        ("PoliticaQueNoMira", "Una política que solo cuenta el reloj gana escenarios del banco", "Resultado incómodo de terceros"),
        ("SemillasQueInvierten", "Con 10 semillas el ganador de 5 se invierte", "Segundo golpe: la estadística de las comparaciones"),
        ("ModeloArribaRLAbajo", "Lenguaje arriba, aprendizaje por refuerzo abajo; la telemetría desborda la capa lenta", "Por qué PADA separa lo lento de lo rápido"),
        ("PadaCuatroCajas", "Percepción, Análisis, Decisión y Acción con ritmos distintos", "Pieza 1: la arquitectura"),
        ("DecisionConjunta", "Tres capas de red que deciden juntas con una recompensa común", "Pieza 2: el modelo formal"),
        ("SateliteDeviceAgent", "Un agente en órbita: contacto intermitente, energía finita, límites regulatorios", "El hueco que queda libre"),
    ]),
    ("Resultados y prisa", "tesis_sem_3_resultados", [
        ("MargenAdaptativoIdea", "Terreno con relieve frente a terreno llano: margen grande o cero", "Pieza 3: el margen adaptativo"),
        ("CompuertaAntesDeCorrer", "El umbral se clava antes de correr; lo que no pasa no se reporta", "Pieza 3: el compromiso por escrito"),
        ("RecorridoDelMargen", "Banco v1 1.7 %, banco v2 31.8 % y piloto mock anulado (orden cronológico)", "Lo que salió mal (la figura central)"),
        ("AlgoritmoVsEstatica", "QMIX supera a la mejor estática en las tres semillas", "Lo que salió bien"),
        ("VarianteSimpleNoEmpeora", "El mezclador simple rinde igual: diagnóstico con n = 3", "Un resultado negativo"),
        ("SimuladorMasReal", "Del banco mínimo a órbitas reales: ¿sobrevive el margen?", "Lo que viene"),
        ("PrisaDosMilVeintinueve", "El doctorado corre feb-2026 → feb-2030; el freeze 6G cae antes de la defensa", "Por qué corre prisa"),
    ]),
]

COMITE = [
    ("Problema y estado del arte", "tesis_com_1_problema", [
        ("LazoAbiertoGana", "Una política de lazo abierto gana escenarios del banco canónico", "Gancho: el campo mide mal"),
        ("SignoQueInvierte", "Con 10 semillas el signo se invierte; ninguna comparación sobrevive a la corrección", "Refuerzo del gancho (de terceros)"),
        ("EscalaEnCien", "16,279 satélites, 66 % Starlink, 86.8 % maniobrables", "Por qué NTN y por qué ahora"),
        ("CapasYDominios", "Matriz capas × dominios con acoplamientos emergentes", "La pregunta registrada"),
        ("HipotesisYFalsadores", "Hipótesis central, tres falsadores y tres subhipótesis subordinadas", "Hipótesis registrada"),
        ("VacioPorEscrito", "Tres huecos que O-RAN y ETSI declaran por escrito y el gemelo que UCDS exige", "Estado del arte: vacíos normativos"),
        ("ArquitecturaOcupada", "Pila de agentes de red ya normalizándose, con NTN y validación vacíos", "Estado del arte: oportunidad temporal"),
    ]),
    ("El marco propuesto", "tesis_com_2_marco", [
        ("CuadranteVacio", "Dominio × objeto de validación: el cuarto cuadrante, sin trabajo localizado", "El hueco en una figura"),
        ("PadaYOran", "PADA sobre O-RAN: entrenar en Non-RT RIC, inferir en xApps", "Componente (i): arquitectura"),
        ("DecPomdpUnificado", "Tres agentes con observación parcial y una recompensa común", "Componente (ii): modelo formal"),
        ("ProtocoloCompuertas", "G0 a G4 sobre rieles; lo que no pasa no se reporta", "Componente (iii): protocolo de validación"),
        ("ReclamoEstrecho", "El reclamo ancho cae ante cuatro precedentes; el estrecho permanece", "La diapositiva más importante"),
        ("ParMargenAdaptativo", "MA como par [0.095, 0.318] frente al umbral 0.25", "Evidencia G1 en dos tramos"),
        ("SensibilidadEpisodios", "MA converge con los episodios: 0.199 → 0.318", "Sensibilidad del estimador"),
    ]),
    ("Evidencia y limitaciones", "tesis_com_3_evidencia", [
        ("G2bTresSemillas", "QMIX, best_static y oráculo en tres semillas", "Evidencia G2b"),
        ("DescriptoresNoCompuertas", "Compuerta c1 frente a descriptores c2 y c3", "Lo que se reporta y cómo"),
        ("NegativosComoProducto", "Ablación VDN (n = 3) y banco mock anulado", "Resultados negativos como producto"),
        ("PuntosDeExtension", "PADA hacia puntos de extensión de 3GPP/O-RAN: mapeo documentado", "F3 no se dispara"),
        ("CircularidadDeF1", "El bucle «construyo y mido» y el emulador externo que lo rompe", "Limitación 1"),
        ("MargenVsFidelidad", "Experimento F1′: margen frente a fidelidad con umbral intacto", "La prueba decisiva (propuesta)"),
    ]),
    ("Alcance, plan y cierre", "tesis_com_4_cierre", [
        ("AlcanceDelBanco", "NTNEnv-v2 instancia mínima y el comparador que falta", "Limitación 2"),
        ("SupuestoA0", "Una autoridad (Dec-POMDP) frente a dos operadores (POSG)", "Supuesto A0"),
        ("PlanG3Reforzada", "G3 reforzada y NTNEnv-v3: plan propuesto", "Plan de trabajo"),
        ("CronogramaDoctoral", "Gantt feb-2026 a feb-2030 con MVP1 a MVP5", "Cronograma"),
        ("CuatroContribuciones", "Marco, protocolo, evidencia y mapeo encajan en la tesis", "Contribuciones"),
        ("CierreMedicionSignifica", "Gane o pierda el algoritmo, el instrumento certificado da significado", "Cierre"),
    ]),
]

BLOQUES = SEMINARIO + COMITE
