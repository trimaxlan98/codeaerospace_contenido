"""Comité tutorial · protocolo de tesis «Gobernanza autónoma de redes programables».

~20 min, una sola voz, lectura hostil y metodológica. Piezas nuevas (tesis_com_1_problema.py, tesis_com_2_marco.py,
tesis_com_3_evidencia.py, tesis_com_4_cierre.py); no se renderiza nada aquí. El guion sigue GUION_COMITE_TUTORIAL_PROTOCOLO.md
(repo de la tesis) y respeta su lista de «lo que NO se puede afirmar»: esas advertencias van en las notas de cada diapositiva
(⚠️ CUIDADO) y nunca en la diapositiva. Las diapositivas de respaldo (fuera de tiempo) preparan las preguntas P1, P2, P5, P6, P11, P12, P13.
Salidas: exports/presentaciones/comite_tutorial_protocolo_{oscuro,claro}.pptx y exports/GUION_COMITE_TUTORIAL_PROTOCOLO.md
Uso: python3 tesis_comite.py [--solo-guion]
"""
from tesis_decks import main

CFG = dict(
    ritmo=140, prefijo="tesis_com", archivo="comite_tutorial_protocolo",
    guion="GUION_COMITE_TUTORIAL_PROTOCOLO.md",
    kicker="PROTOCOLO DE TESIS DOCTORAL · COMITÉ TUTORIAL", titulo="Gobernanza autónoma de redes programables", tam_titulo=50,
    lema="Instanciada en redes no terrestres 6G",
    autor="Alan Rosas Palacios", instit="Doctorado · Instituto Politécnico Nacional · Asesor: Dr. Víctor Barrera Figueroa",
    pie="Protocolo de tesis · Alan Rosas Palacios", cierre_titulo="Un resultado negativo también es un producto",
    titulo_plano="Comité tutorial: protocolo de tesis «Gobernanza autónoma de redes programables»",
    nota_md=("Audiencia: comité revisor (asesor y sinodales), lectura hostil y metodológica. Semestre 2026-S2. **Fecha por confirmar con coordinación**; "
             "los 20 minutos son dato del doctorando, no del comité. El contrato es defender el método: cada afirmación tiene su fila en la lista de "
             "«lo que NO se puede afirmar». La estructura, las cifras y las advertencias vienen del guion del repo de la tesis; **no se añadió ninguna cifra nueva**."),
)

DIAPOS = [
    ("portada",
     "Buenos días. Voy a presentar el protocolo de mi tesis doctoral, cuyo título es «Gobernanza autónoma de redes programables», instanciada en redes no terrestres 6G. "
     "Antes de empezar, una advertencia de método: voy a decir con claridad qué está demostrado, qué es propuesta y qué no puedo afirmar. "
     "Prefiero que sea este comité quien pruebe mis afirmaciones y no una búsqueda cualquiera después. Mi asesor es el doctor Víctor Barrera Figueroa. "
     "Y empiezo, deliberadamente, no con redes satelitales, sino con un problema de medición que afecta a todo el campo."),

    ("video", "LazoAbiertoGana", "Una política que no mira nada gana escenarios del banco canónico",
     "Ellis et al., SMACv2 (NeurIPS 2023) · resultado de terceros",
     "Abro con un resultado que no es mío. Ellis y colaboradores, en SMACv2, NeurIPS 2023, mostraron que una política de lazo abierto, condicionada únicamente al paso del tiempo, "
     "sin observar el estado, gana escenarios de SMAC, el banco de pruebas canónico del aprendizaje por refuerzo multiagente cooperativo. "
     "En términos de mi tesis: el margen adaptativo es aproximadamente cero en el banco sobre el que el subcampo llevaba años publicando comparaciones. "
     "Insisto en que es un hallazgo de terceros. Si este comité percibiera que me lo atribuyo, perdería la credibilidad de golpe, y con razón.",
     "Preséntalo como de terceros. Ellis et al.: las páginas de actas de NeurIPS no están verificadas."),

    ("video", "SignoQueInvierte", "Con diez semillas el signo se invierte",
     "Yılmaz y Çelikcan (2026) · otro dominio, el mismo problema de medición",
     "Como refuerzo, Yılmaz y Çelikcan, en Applied Sciences, agosto de 2026. Con QMIX, entre cuatro arquitecturas base, las diferencias observadas con cinco semillas invierten el signo con diez. "
     "Una política aleatoria puntúa dentro del rango de las entrenadas. Y ninguna comparación sobrevive a la corrección por comparaciones múltiples. "
     "Declaro el alcance: el estudio es sobre Google Research Football, no sobre redes no terrestres. Lo traigo porque la patología es de medición, no de dominio.",
     "El estudio es sobre Google Research Football, no NTN: dilo si preguntan. Applied Sciences 16(15):7650, DOI 10.3390/app16157650."),

    ("cita", "Si el entorno no premia adaptarse, comparar algoritmos sobre él no significa nada.",
     "Y eso no se sabe hasta que se mide.",
     "Esa es la tesis en una frase. Si el entorno no premia adaptarse, comparar algoritmos sobre él no significa nada. "
     "Y eso no se sabe hasta que se mide. El resto de la presentación sirve a esa frase."),

    ("video", "EscalaEnCien", "Por qué NTN, y por qué ahora",
     "El sistema es dinámico por construcción, no por perturbación",
     "Por qué redes no terrestres y por qué ahora. Cifras verificadas en fuente primaria: dieciséis mil doscientos setenta y nueve satélites activos, con corte del 13 de agosto de 2026, "
     "según McDowell, de los cuales Starlink, diez mil setecientos cuarenta y dos, el sesenta y seis por ciento. "
     "Y el ochenta y seis punto ocho por ciento de las cargas activas son maniobrables: el sistema es dinámico por construcción, no por perturbación. "
     "La escala y el dinamismo hacen inviable la gestión manual y atractiva la inteligencia artificial. El problema es que la atracción llegó antes que el instrumento para evaluarla.",
     "Cifras con reserva de corte (13-ago-2026; verificadas el 28-ago, no re-verificadas el 2-sep). No usar ninguna otra."),

    ("cita", "¿Cómo gobernar de forma autónoma y resiliente un sistema de comunicaciones complejo, dinámico, distribuido y programable, cuyas propiedades emergen de la interacción de múltiples capas y dominios?",
     "La pregunta de investigación registrada, literal",
     "Esta es la pregunta registrada, sin adornos. La leo tal cual: cómo gobernar de forma autónoma y resiliente un sistema de comunicaciones complejo, dinámico, distribuido "
     "y programable, cuyas propiedades emergen de la interacción de múltiples capas y dominios."),

    ("video", "CapasYDominios", "Las propiedades emergen de varias capas y dominios",
     "Por eso la gobernanza no puede ser una sola capa",
     "La figura muestra por qué la pregunta está planteada así. Capas, radio, red, núcleo y aplicación, cruzadas con dominios, tierra, aire y espacio. "
     "Cada acoplamiento que se enciende es una vía por la que una decisión en una celda altera otra. Las propiedades relevantes emergen de esas interacciones, "
     "y por eso un controlador por capa no basta. Esta es la formulación registrada y es invariante."),

    ("texto", "Objetivo general y OE1′–OE5′: lo registrado", "Invariante: todo lo que sigue es desarrollo, no cambio de rumbo",
     ["Objetivo general: principios, arquitectura formal y enfoque metodológico para la gobernanza autónoma, instanciado en NTN/6G y demostrado frente a gestión estática",
      "OE1′ Principios y arquitectura · OE2′ Modelo formal · OE3′ Gemelo digital válido",
      "OE4′ Programabilidad medida · OE5′ Validación cuantitativa con jerarquía de evidencia",
      "El objetivo promete un marco y una demostración frente a la gestión estática; no promete que el aprendizaje por refuerzo gane"],
     "Lo registrado ante el comité es el título, el objetivo general y los objetivos específicos OE1 a OE5 primas. Es invariante, y lo digo explícitamente porque enmarca todo lo demás como desarrollo y no como cambio de rumbo. "
     "El objetivo general promete un marco, principios, arquitectura y enfoque metodológico, y una demostración frente a la gestión estática. "
     "No promete que el aprendizaje por refuerzo gane. Esa distinción va a ser importante en toda la sesión."),

    ("video", "HipotesisYFalsadores", "Una hipótesis central con tres falsadores",
     "HC ratificada el 2026-07-01 · SH1–SH3 subordinadas",
     "La hipótesis central, única, ratificada el primero de julio de 2026, con tres condiciones de falsación. F1: instrumento inválido. F2: ninguna política adaptativa del marco supera a la estática. "
     "F3: incompatibilidad con protocolos 3GPP y O-RAN. Las subhipótesis SH1 a SH3 están subordinadas: pueden fallar sin refutar la hipótesis central. "
     "El estado hoy: F1 superada en la primera iteración, con la circularidad que declaro más adelante; F2 con una demostración favorable en G2b, a la espera de G3 para el análisis completo; y F3 no se dispara. "
     "No entro en las magnitudes de las subhipótesis. Solo preciso el estatus: SH2 quedó sin magnitud pre-registrada desde la Enmienda 1, ratificada el 5 de julio. "
     "SH3 conserva sus predicciones puntuales pre-registradas, y lo que cambió en agosto es la confianza declarada en su anclaje, no su estatus.",
     "No llamar a SH2 «umbral de trabajo»: está RETIRADO (Enmienda 1, ratificada 2026-07-05); reabrirlo viola R6. La reclasificación del ancla de E1 y la banda «−8 % / +14 %» son la Enmienda 3, PENDIENTE de ratificación: no presentarla como hecho. No mostrar +20 %/+30 %."),

    ("video", "VacioPorEscrito", "Los organismos declaran el vacío por escrito",
     "Texto normativo primario: O-RAN y ETSI",
     "Tres citas verificadas en texto normativo primario. Una: el informe técnico de O-RAN sobre NTN dice, literalmente, que, hasta donde el grupo sabe, no existen contribuciones aprobadas "
     "ni trabajo normativo sobre NTN en O-RAN. Es el propio organismo declarando el vacío. Dos: para la interfaz Este-Oeste entre RICs, O-RAN escribe que está identificada como un hueco, con veintiún requisitos. "
     "Es exactamente donde encaja el marco. Tres: ETSI ZSM 021, mayo de 2026, muestra que los organismos se limitan a un solo objetivo y no saben balancear ni ponderar objetivos que compiten. "
     "Y un hallazgo que convierte una decisión de diseño en requisito externo: UCDS versión 20 exige, como capacidad del Near-RT RIC, un gemelo digital de la constelación NTN. "
     "El banco de pruebas deja de ser una elección mía y pasa a ser algo que el estándar pide.",
     "Citas: O-RAN TR RIC4NTN §4.2.1; O-RAN §5.1.5.2; ETSI GR ZSM 021 (2026-05) §4.4.3; UCDS v20.00. No afirmar «no existe métrica de fidelidad de gemelo digital»: ISO/IEC CD TR 30138 está en borrador, sin publicar."),

    ("video", "ArquitecturaOcupada", "2026: la arquitectura de agentes ya está ocupada",
     "Lo que no localicé: NTN ni validación del instrumento",
     "Ahora hay que ser honesto sobre el argumento de oportunidad: la arquitectura de agentes de red ya está ocupada, y decirlo primero es lo que da autoridad. "
     "El IETF tiene un borrador que define tres capas de agentes hasta un agente en el elemento de red, con lenguaje normativo; otro, con Huawei, Telefónica, Deutsche Telekom, Orange y Nokia, "
     "expone la red como herramientas MCP. En 3GPP, el TR 22.870 de la versión 20 concluyó con requisitos de agentes de red y el freeze de la primera versión 6G se sitúa potencialmente a inicios de 2029. "
     "ETSI ZSM pasó de estudiar agentes a especificarlos. Mi lectura: la arquitectura de agentes no es mi contribución y no la reclamo. "
     "Lo que no encontré en ninguno de esos documentos es su instanciación en redes no terrestres, ni ningún mecanismo que valide el instrumento antes de evaluar al agente. "
     "En el primer borrador, busqué «satellite» y «NTN»: cero ocurrencias.",
     "Es un «no localicé», no un «no existe»."),

    ("video", "CuadranteVacio", "El hueco, en una figura",
     "Cuadrante vacío: no localicé trabajo aquí",
     "El hueco en una figura. Dos ejes: dominio, terrestre o no terrestre, y objeto de validación, si se valida el algoritmo o el instrumento. "
     "Tres cuadrantes están poblados con literatura. El cuarto, validar el instrumento en un dominio no terrestre, lo rotulé «no localicé trabajo aquí». "
     "No digo que no exista. Digo que lo busqué y no lo encontré, y dejo las búsquedas a disposición del comité.",
     "Rotular el cuadrante «no localicé trabajo aquí», no «no existe»."),

    ("video", "PadaYOran", "Componente (i): arquitectura desacoplada, PADA",
     "La partición CTDE coincide con la que O-RAN induce",
     "Primer componente del marco: una arquitectura desacoplada, PADA, Percepción, Análisis, Decisión, Acción, con interfaces programables. "
     "El argumento fuerte y poco explotado es que la partición de aprendizaje centralizado en entrenamiento y descentralizado en ejecución, CTDE, coincide con la que O-RAN induce: "
     "el entrenamiento en el Non-RT RIC y el SMO, por la interfaz R1, y la inferencia en xApps del Near-RT RIC, por A1-ML. "
     "CTDE deja de ser una elección arbitraria y pasa a ser la partición que la arquitectura de referencia induce. El marco no la fuerza: la aprovecha. "
     "Y no digo «arquitectura original»: PADA mapea limpiamente a ETSI ZSM 002 y 009 y a TM Forum IG1230. Lo defendible es el posicionamiento situado sobre huecos que los organismos declaran por escrito.",
     "No decir «arquitectura original»."),

    ("video", "DecPomdpUnificado", "Componente (ii): modelo formal Dec-POMDP cross-layer",
     "Desigualdad de base: Oliehoek, Spaan y Vlassis (JAIR, 2008)",
     "Segundo componente: el modelo formal, un Dec-POMDP cross-layer unificado. Tres agentes, satélite A, satélite B y gateway, cada uno con observación parcial, acción conjunta y una recompensa común. "
     "Me adelanto a la pregunta del teorema: la desigualdad de base es el Teorema 5.1 de Oliehoek, Spaan y Vlassis, JAIR 32, páginas 289 a 353, de 2008. "
     "No es un teorema mío. Lo que aporto es el uso que hago de esa jerarquía, y lo desarrollo en la siguiente diapositiva.",
     "No decir «Teorema del Margen Adaptativo» como resultado propio: es una proposición instrumental derivada de Oliehoek et al.; su holgura no está acotada."),

    ("video", "ProtocoloCompuertas", "Componente (iii): protocolo de validación del instrumento",
     "Aquí está la aportación: compuertas G0–G4 con umbral pre-registrado",
     "Tercer componente, y aquí está la aportación. El margen adaptativo mide cuánta ganancia admite el entorno frente a la mejor política estática. "
     "El umbral, cero punto veinticinco, se fija antes de correr, pre-registrado. Las compuertas G0 a G4 condicionan qué inferencias son legítimas: si el entorno no pasa, la comparación de algoritmos sobre él no se reporta. "
     "Hoy, G0, G1, G2a y G2b están superadas, G3 y G4 están pendientes. "
     "Y hay un corolario propio y decisivo: si el margen adaptativo es cero, la subhipótesis no es ni falsable ni confirmable. "
     "De ahí que validar el instrumento sea condición necesaria de la inferencia, no una buena práctica.",
     "G3 y G4 pendientes; nunca decir «completado»."),

    ("video", "ReclamoEstrecho", "El reclamo, con precisión quirúrgica",
     "El estrecho se defiende; el ancho se cae en una búsqueda",
     "Esta es la diapositiva más importante del protocolo. Lo que puedo decir: el margen frente a la mejor política estática, con umbral pre-registrado, usado como compuerta que condiciona la falsabilidad de la hipótesis. "
     "Busqué precedentes y no los encontré; los trabajos afines son diagnósticos descriptivos, auditorías posteriores o pre-filtros de eficiencia. "
     "Lo que no puedo decir: que nadie haya propuesto validar el entorno antes del algoritmo. Es falso: Xu y Chen, 2021; Furuta y colaboradores, ICML 2021; Oller y colaboradores, AAMAS 2020; y Tao, Xu y You, 2026, "
     "publican evaluación centrada en la tarea del gemelo digital para pre-filtrar gemelos antes de entrenar al agente. Tampoco puedo decir que nadie haya llevado rigor experimental a un dominio aplicado: "
     "McFadden y colaboradores lo hicieron en ciberseguridad, en USENIX Security 2026. El reclamo estrecho se defiende. El ancho se cae en una búsqueda, y un comité premia a quien acota su propia contribución.",
     "Citar el preprint arXiv:2511.19961 de Tao, Xu y You; el DOI de IEEE WCM no está re-verificado. No decir «primer marco» ni «nadie certifica autonomía de red» (TM Forum ANLAV existe desde jun-2025; sin citar sus cifras)."),

    ("video", "ParMargenAdaptativo", "G1: el instrumento es válido, y se establece en dos tramos",
     "MA ∈ [0.095, 0.318] · umbral pre-registrado 0.25",
     "Evidencia. G1: el margen adaptativo sobre NTNEnv-v2 es cero punto trescientos dieciocho, sobre un umbral pre-registrado de cero punto veinticinco. F1 se supera en la primera iteración. "
     "El estimador es una cota inferior, luego un margen medido de cero punto trescientos dieciocho certifica un margen real de al menos ese valor: G1 no admite falsos positivos por esa vía. "
     "Pero no reporto el número suelto, reporto el par: el margen está entre cero punto cero noventa y cinco y cero punto trescientos dieciocho. "
     "La holgura del Lema 4.7 no está acotada: un margen mayor que cero no implica por sí solo que exista una política descentralizada que supere a la estática. "
     "El cero punto cero noventa y cinco es el margen decisional alcanzable medido constructivamente en G2b; el trescientos dieciocho es la envolvente. Por eso la validez se establece en dos tramos, G1 y G2b. "
     "Esto responde de antemano la pregunta más peligrosa, la de si mi compuerta es vacua.",
     "Reportar el par, no el número suelto. La enmienda del par está PENDIENTE de ratificación. Esta respuesta debe estar en la diapositiva, no solo en el guion (P11). Es el estado de TEOREMA_MARGEN_ADAPTATIVO.md §2.2."),

    ("video", "SensibilidadEpisodios", "La sensibilidad del margen ya está convergida",
     "1 / 5 / 10 / 30 episodios → 0.199 / 0.288 / 0.307 / 0.318",
     "Sensibilidad medida. Con uno, cinco, diez y treinta episodios de evaluación, el margen es cero punto uno noventa y nueve, cero punto doscientos ochenta y ocho, cero punto trescientos siete y cero punto trescientos dieciocho. "
     "El umbral se cruza entre uno y cinco episodios y la curva se estabiliza: G1 está en zona convergida, no en el filo del umbral. "
     "No es una medición que dependa de haber corrido justo el número de episodios que convenía."),

    ("video", "G2bTresSemillas", "G2b: la política aprendida supera a la mejor estática",
     "+9.5 % a +16.3 % en 3/3 semillas · 84–87 % del oráculo",
     "G2b. QMIX supera a best_static en tres de tres semillas, con mejoras de nueve punto cinco a dieciséis punto tres por ciento, y alcanza entre el ochenta y cuatro y el ochenta y siete por ciento del rendimiento de una política con información privilegiada. "
     "Esa política es a su vez una cota inferior del óptimo, proposición 4.8. No es el máximo teórico y no debe llamarse así. "
     "Es evidencia de que, en un entorno certificado, existe una política descentralizada aprendible que supera a la mejor estática, con la escala mínima de tres agentes y tres semillas."),

    ("video", "DescriptoresNoCompuertas", "Lo que se reporta como descriptor, no como compuerta",
     "c2 modal y c3 información mutua: no se cumplen globalmente",
     "Y lo digo exactamente así, porque un sinodal puede abrir el archivo que esta diapositiva cita. La información mutua entre acción y visibilidad es significativa, p aproximadamente cero punto cero cero cinco, "
     "en dos de tres canales en dos semillas y en uno de tres en la tercera. El criterio c3 no se cumple globalmente, y por eso se reporta en vez de bloquear. Lo mismo con el descriptor modal, c2. "
     "Así lo ratificó el doctor Barrera el 23 de julio de 2026. La compuerta es c1: la política supera a best_static en tres de tres semillas.",
     "El JSON G2B_RECUALIFICACION_v7.json registra c2_modal: false y c3_mi: false. Decir «MI significativa 3/3» es la refutación más barata que existe."),

    ("video", "NegativosComoProducto", "Dos resultados negativos, presentados como producto",
     "Diagnóstico con n = 3 · el banco mock, anulado por el protocolo",
     "Dos resultados negativos, que presento como producto. Uno: la ablación del mixer. Quitar la mezcla no lineal, la variante VDN, no arregla el colapso modal ni daña el rendimiento; "
     "es indicio de que la no linealidad del mixer no gana su complejidad en este régimen. Lo presento como diagnóstico con tres semillas, sin potencia estadística para un reclamo de equivalencia. "
     "Dos: el episodio del banco mock. Un banco de pruebas inválido produjo resultados espectaculares, y el propio protocolo los detectó y los anuló. "
     "Es evidencia, no accidente: un marco de validación que nunca invalida nada no está midiendo.",
     "No decir «resultado negativo demostrado»: es diagnóstico (el informe al asesor dice que la diferencia «está dentro del ruido»)."),

    ("video", "PuntosDeExtension", "F3 no se dispara",
     "Existe un mapeo documentable a los puntos de extensión que los estándares ya prevén",
     "F3, incompatibilidad con protocolos 3GPP y O-RAN, no se dispara. Existe un mapa documentado entre PADA y los puntos de extensión de 3GPP y O-RAN, con citas primarias, y el propio documento declara verificaciones pendientes. "
     "No digo que PADA sea compatible con 3GPP y O-RAN, porque eso es una afirmación sobre el contenido de especificaciones. Digo que existe un mapeo documentable, y que los huecos que quedan están verificados con cita literal. "
     "Un ajuste de precisión: el hueco «menos de diez milisegundos» estaba mal formulado en documentos internos. Lo correcto es que no hay un lazo programable por aplicación por debajo de diez milisegundos.",
     "No decir «PADA es compatible con 3GPP/O-RAN»: «F3 no se dispara; existe un mapeo documentable»."),

    ("video", "CircularidadDeF1", "Limitación 1: la circularidad de F1, declarada",
     "Calibración, no falsación · remedio propuesto: F1′",
     "Ahora, las limitaciones, y las digo yo antes que ustedes. El umbral de cero punto veinticinco aparece como objetivo de diseño en la configuración del entorno. "
     "En la primera iteración, G1 certifica una condición necesaria sobre un entorno que yo construí. Eso es calibración, no falsación, y no debo presentarlo como otra cosa. "
     "El remedio, propuesto y pendiente de ratificación del asesor: la prueba decisiva es si el margen sobrevive cuando la fidelidad no la controlo yo. "
     "De ahí NTNEnv-v3 sobre un emulador con órbitas reales, enlaces inter-satelitales y latencias medidas, con el umbral intacto y un nuevo falsador, F1 prima.",
     "El remedio está PENDIENTE de ratificación del asesor. El CLAUDE.md de la tesis (2026-09-17) registra que el Dr. Barrera aprobó el memo consolidado; confirma qué se ratificó antes de decir «pendiente»."),

    ("video", "AlcanceDelBanco", "Limitación 2: alcance del banco y el comparador que falta",
     "Instancia mínima con margen cualificado · falta IPPO/MAPPO",
     "Segunda limitación. NTNEnv-v2 es una instancia mínima, no un gemelo digital de alta fidelidad: dos satélites, un gateway, tres acciones por agente. "
     "Su virtud es exhibir los tres mecanismos, ventanas de visibilidad, congestión del gateway y canal rotante, con un margen cuantificado, y haber servido para demostrar que el protocolo detecta bancos inválidos. "
     "Lo hizo con v1, con margen de uno punto siete por ciento, y con el piloto sobre el banco mock. Y el comparador que falta: propongo añadir IPPO y MAPPO al brazo de G3, con el mismo presupuesto de episodios. "
     "Es una omisión de alcance que reconozco y corrijo; sería regalar la pregunta no incluirlo.",
     "No llamar a NTNEnv-v2 «Digital Twin de alta fidelidad»: «instancia mínima con margen adaptativo cualificado»; el término se reserva para v3."),

    ("video", "SupuestoA0", "Supuesto A0: una sola autoridad de gobernanza",
     "Levantarlo cambia la clase de problema: Dec-POMDP → POSG",
     "Tercera limitación: el supuesto A0. El marco supone autoridad de gobernanza única. Levantarlo cambia la clase de problema, de Dec-POMDP con recompensa conjunta a POSG con equilibrios. "
     "Y el regulador no supone objetivo conjunto: el 47 CFR 25.261 obliga a coordinar de buena fe e impone un reparto cuando la degradación supera un umbral. Supone rivales. "
     "Separar las dos capas no es evasión: es la estructura que la propia literatura adopta. Es un problema real y mal resuelto hoy, de naturaleza distinta al problema intra-dominio que ataca este trabajo.",
     "No decir «primer marco de coordinación multi-operador NGSO»: es un campo activo."),

    ("video", "MargenVsFidelidad", "La prueba decisiva: ¿sobrevive el margen a la fidelidad?",
     "Experimento pre-registrado F1′ · propuesto",
     "Y la prueba decisiva, que es propuesta: ¿sobrevive el margen adaptativo al aumento de fidelidad? Umbral cero punto veinticinco intacto, experimento pre-registrado, falsador nuevo F1 prima. "
     "Dibujé tres trayectorias posibles y no elegí ninguna como la buena. Si el margen prima cae por debajo de cero punto veinticinco, F1 prima se dispara, y eso es un resultado doctoral, no un fracaso: "
     "es precisamente lo que significa hacer una tesis que pone la validez primero. Y no es una idea suelta: O-RAN ya exige un gemelo de constelación en el RIC, de modo que la versión 3 responde a un requisito de estándar y no a un capricho de alcance.",
     "Propuesto, pendiente de ratificación. Las curvas son ilustrativas: no prometer cuál se cumple."),

    ("video", "PlanG3Reforzada", "Plan de trabajo propuesto, sujeto a ratificación del asesor",
     "G3 reforzada y NTNEnv-v3 · reunión pendiente",
     "Plan de trabajo, y lo rotulo así: propuesto, sujeto a ratificación del asesor. Nada de lo que sigue está ratificado. G3, en versión reforzada: treinta mil pasos por diez semillas, brazo IPPO y MAPPO, heurística afinada por búsqueda en malla, "
     "y métricas de red como primarias, throughput, p99, SLA e índice de Jain, con la recompensa como secundaria. Pre-registro fechado antes de correr, regla R6. "
     "Después, NTNEnv-v3 y el experimento de margen frente a fidelidad en la primera mitad de 2027, con F1 prima como falsador vivo. "
     "El riesgo de cómputo, con la estimación corregida: unas ciento veinte horas-núcleo, de cincuenta y cinco a ciento diez horas de cómputo según GATES. Son el mismo dato dicho de dos maneras.",
     "Rotular «plan propuesto, sujeto a ratificación». GATES.md registra G3 como «Desbloqueado · decidir secuenciación». Las 55–110 h de reloj sustituyen a las «10–15 h» de documentos previos. Confirma con la reunión con el Dr. Barrera (CLAUDE.md 2026-09-17: aprobó el memo; falta el detalle)."),

    ("video", "CronogramaDoctoral", "Cronograma: febrero de 2026 a febrero de 2030",
     "Semestre 2 de 8 · MVP1 y MVP2 completados, MVP3 en curso",
     "El cronograma, sobre el horizonte único, febrero de 2026 a febrero de 2030: cuarenta y ocho meses, voy en el segundo semestre de ocho. "
     "MVP1 completado, con WITCOM 2026 aceptado, ponencia del 2 al 6 de noviembre en Huatulco. MVP2 completado, tesina predoctoral defendida en junio. "
     "MVP3 en curso: G0, G1, G2a y G2b superadas, G3 pendiente. MVP4 y MVP5 planeados, sin ratificar. Redacción y defensa entre 2029 y febrero de 2030. "
     "Esta diapositiva no se elimina por tiempo.",
     "MVP4-MVP5: la reorientación está propuesta, sin ratificar. La diapositiva de cronograma no se elimina por tiempo."),

    ("video", "CuatroContribuciones", "Contribuciones comprometidas",
     "Cuatro entregables, no cuatro promesas de resultado",
     "Comprometo cuatro contribuciones. Una: un marco metodológico de gobernanza autónoma para NTN, situado sobre huecos que los organismos declaran por escrito. "
     "Dos: un protocolo de validación del instrumento, con margen, umbral pre-registrado y compuertas, con su formalización y su corolario de falsabilidad. "
     "Tres: evidencia experimental bajo ese protocolo, incluidos los resultados negativos. Cuatro: un mapeo documentado del marco a puntos de extensión de 3GPP y O-RAN, con sus verificaciones pendientes declaradas. "
     "Fíjense que son entregables, no promesas de que un algoritmo gane."),

    ("video", "CierreMedicionSignifica", "El marco no promete que el aprendizaje por refuerzo gane",
     "Promete que, gane o pierda, sabremos que la medición significaba algo",
     "Vuelvo al gancho. El marco no promete que el aprendizaje por refuerzo gane. Promete que, cuando gane o pierda, se sabrá que la medición significa algo. "
     "Un resultado negativo deja de ser un fracaso y pasa a ser un producto. Si el algoritmo pierde, el instrumento certificado permite decirlo con la misma validez con la que se habría dicho una victoria."),

    ("cierre",
     "Gracias. Quedo atento a sus preguntas. Tengo preparadas las que espero con más probabilidad: operadores distintos, novedad del teorema, MAPPO, modelos de lenguaje, la holgura no acotada, cuántos entornos construí y qué queda de SH3 si el mixer no hace falta."),

    ("respaldo", "P1 · ¿Y si los satélites son de operadores distintos?", "Supuesto A0 declarado",
     ["El marco supone autoridad de gobernanza única (A0)", "Levantarlo cambia la clase de problema: Dec-POMDP → POSG",
      "47 CFR 25.261: coordinar de buena fe; reparto punitivo; supone rivales", "Separar las capas es la estructura que la literatura adopta"],
     "El marco supone autoridad de gobernanza única, el supuesto A0, declarado. Levantarlo no es un ajuste: cambia la clase de problema, de Dec-POMDP con recompensa conjunta a POSG con equilibrios. "
     "La frontera es formalmente exacta. Además, el regulador no supone objetivo conjunto: el 47 CFR 25.261 obliga a coordinar de buena fe e impone un reparto punitivo cuando la degradación supera un umbral. "
     "Supone rivales, y por eso necesita un castigo por defecto. Es un problema real, mal resuelto hoy y de naturaleza distinta al problema intra-dominio. Separar las dos capas no es evasión: es la estructura que la propia literatura adopta."),

    ("respaldo", "P2 · ¿Su teorema es nuevo?", "No, y lo digo antes de que lo pregunten",
     ["La desigualdad es el Teorema 5.1 de Oliehoek, Spaan y Vlassis (JAIR 32:289-353, 2008)",
      "La aportación es metodológica: el margen como compuerta pre-registrada",
      "Corolario propio: si MA = 0, la subhipótesis no es falsable ni confirmable"],
     "No, y conviene decirlo antes de que lo pregunten. La desigualdad es de Oliehoek, Spaan y Vlassis, 2008. La aportación es metodológica: usar el margen como compuerta pre-registrada que condiciona qué inferencias son legítimas. "
     "Y hay un corolario propio que sí importa: si el margen es cero, la subhipótesis no es falsable ni confirmable."),

    ("respaldo", "P5 · ¿Por qué no está MAPPO en su comparación?", "Omisión de alcance, reconocida",
     ["Decisión de alcance de julio de 2026: cerrar la cadena de compuertas con la configuración presupuestada",
      "Se corrige: IPPO/MAPPO en el brazo de G3 con el mismo presupuesto de episodios",
      "«Beyond Monotonicity» (AAAI 2026): la comparación correcta es monotonicidad vs. su ausencia, no VDN vs. QMIX"],
     "Por una decisión de alcance de julio de 2026 que priorizó cerrar la cadena de compuertas con la configuración presupuestada. Es una omisión que reconozco; se corrige añadiendo IPPO y MAPPO al brazo de G3, con el mismo presupuesto de episodios. "
     "Si mencionan Beyond Monotonicity, de AAAI 2026, reencuadro la comparación correcta como restricción de monotonicidad frente a su ausencia, no VDN frente a QMIX, porque ambos son monotónicos. Es una observación de diseño experimental válida y hay que concederla."),

    ("respaldo", "P6 · ¿Por qué QMIX y no un agente basado en modelos de lenguaje?", "Lenguaje arriba, refuerzo abajo",
     ["Clemm y Eckert (IETF 2026): la telemetría cruda excede la capacidad de tokens «salvo que se reduzca el volumen en varios órdenes de magnitud»",
      "Primer banco de agentes de telecom (2026): corrección de procedimiento < 0.01 en 4 de 8 modelos (inglés) y 6 de 8 (árabe)",
      "ASTREA: con ventana de 15 min empeoró; alineado a 90 min mejoró",
      "PADA ya es la mitad de abajo; el punto de extensión hacia arriba está declarado"],
     "Porque la industria misma acota dónde sirve cada capa. Clemm y Eckert, autor principal del RFC 9315, escriben en un borrador del IETF de 2026 que la telemetría cruda excede la capacidad de tokens de los modelos de lenguaje "
     "en el futuro previsible, salvo que se tomen otras medidas para reducir el volumen de datos en varios órdenes de magnitud. La coda importa y hay que decirla completa. "
     "En el primer banco de agentes de telecom, la métrica de corrección del procedimiento cae por debajo de cero punto cero uno en cuatro de ocho modelos en inglés y en seis de ocho en árabe. "
     "El patrón dominante es modelo de lenguaje arriba y aprendizaje por refuerzo abajo. PADA ya es la mitad de abajo. Y ASTREA, con ventana de quince minutos, empeoró, y alineado al periodo orbital mejoró: "
     "es evidencia empírica de que la capa semántica lenta va fuera del lazo rápido.",
     "ASTREA es un preprint de autor único, n pequeño, sin IC: decláralo."),

    ("respaldo", "P11 · ¿Su compuerta no es vacua, si la holgura es no acotada?", "La pregunta más peligrosa",
     ["Premisa correcta y documentada en TEOREMA_MARGEN_ADAPTATIVO.md §2.2",
      "La compuerta es de dos tramos: G1 acota la envolvente; G2b es constructiva",
      "Reporto el par [0.095, 0.318], no el 0.318 suelto",
      "Una compuerta que solo mirara la envolvente sí sería vacua: la mía no pasa hasta que alguien construye la política"],
     "Tiene razón en la premisa, y está escrito en mi documento teórico, no lo descubrió usted ahora. Por eso la compuerta no es un solo número: es de dos tramos. "
     "G1 acota la envolvente: el margen de cero punto trescientos dieciocho dice cuánto margen podría haber, y como el estimador es cota inferior no produce falsos positivos por esa vía. "
     "Pero la envolvente no basta, exactamente por la holgura no acotada. Por eso G2b es constructiva: exhibe una política descentralizada real que supera a la mejor estática, "
     "lo que establece un margen decisional alcanzable de al menos nueve punto cinco por ciento. Ese es el número que gobierna lo que SH3 puede demostrar. "
     "Una compuerta que solo mirara la envolvente sí sería vacua; la mía no pasa hasta que alguien construye la política.",
     "Esta respuesta tiene que estar en la diapositiva de G1, no solo aquí. Si llega sin preparar, destruye el bloque 5 completo."),

    ("respaldo", "P12 · ¿Cuántos entornos construyó hasta que uno pasó?", "Registro completo de la búsqueda",
     ["v1: margen 1.7 % (G0, 2026-06-10) — invalidado",
      "v2: margen 31.8 % (G1, 2026-06-10) — pasa; el umbral nunca se movió",
      "Piloto sobre banco mock: resultados espectaculares — anulado el 2026-07-01 (R5)",
      "Sin corrección por multiplicidad sobre el espacio de instrumentos: se concede"],
     "Es la objeción correcta y no tengo una corrección por multiplicidad sobre el espacio de instrumentos; se lo concedo. "
     "Lo que sí tengo es el registro completo de la búsqueda, en orden cronológico: v1 con margen de uno punto siete por ciento, v2 con treinta y uno punto ocho por ciento, "
     "y el piloto sobre el banco mock, que anulé el primero de julio, todos documentados con su evidencia y su fecha, no seleccionados a posteriori. Y tengo la salida honesta: el umbral no se movió nunca. "
     "Si hubiera bajado el umbral hasta que un entorno pasara, la crítica sería letal. Lo que hice fue lo contrario: cambié el instrumento hasta que exhibió el mecanismo que dice medir, con el criterio fijo. "
     "Aun así, esa búsqueda es la razón por la que la prueba decisiva es sobre un entorno cuya fidelidad no controlo yo.",
     "Llevar impreso el registro fechado de instrumentos construidos con su margen. Fechas según GATES.md y CHECKLIST.md de la tesis (piloto mock invalidado el 2026-07-01); confírmalas en el expediente."),

    ("respaldo", "P13 · Si el mixer no hace falta, ¿qué queda de SH3?", "Queda la pregunta bien planteada",
     ["SH3 no dice «QMIX es superior»: dice que una política CTDE supera a la estática, a DTDE con igual presupuesto y a la heurística afinada",
      "El mixer es evidencia sobre qué parte de la arquitectura paga",
      "Si la heurística afinada empata en G3, SH3 falla; la HC sigue por F2; se publica"],
     "Queda la pregunta bien planteada, que es lo que SH3 debía aportar. SH3 no dice que QMIX sea superior: dice que una política CTDE supera a la mejor estática, a DTDE con igual presupuesto y a la heurística afinada, "
     "en un entorno con margen certificado. El resultado del mixer es evidencia sobre qué parte de la arquitectura paga, no sobre si la clase de métodos funciona. "
     "Si en G3 la heurística afinada empata con QMIX, la subhipótesis falla, la hipótesis central sigue en pie por F2, y publico eso. Es el diseño, no un accidente.",
     "No prometer que SH3 se sostendrá."),
]


if __name__ == "__main__":
    main(CFG, DIAPOS)
