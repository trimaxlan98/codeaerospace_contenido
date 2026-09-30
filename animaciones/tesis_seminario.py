"""Seminario de divulgación «Agentes de inteligencia artificial en órbita — y el problema de saber si funcionan».

Tesis doctoral de Alan Rosas Palacios (IPN): «Gobernanza autónoma de redes programables», instanciada en 6G/NTN.
~30 min, una sola voz. Cada diapositiva de video lleva título-afirmación, subtítulo y el guion en las notas;
las piezas son nuevas (tesis_sem_1_orbita.py, tesis_sem_2_examen.py, tesis_sem_3_resultados.py) y NO se
renderizan aquí. Mensaje, cifras y advertencias salen de GUION_SEMINARIO_DIVULGACION.md (repo de la tesis).
Salidas: exports/presentaciones/seminario_agentes_ia_orbita_{oscuro,claro}.pptx y exports/GUION_SEMINARIO_AGENTES_IA_ORBITA.md
Uso: python3 tesis_seminario.py [--solo-guion]
"""
from tesis_decks import main

CFG = dict(
    ritmo=140, prefijo="tesis_sem", archivo="seminario_agentes_ia_orbita",
    guion="GUION_SEMINARIO_AGENTES_IA_ORBITA.md",
    kicker="SEMINARIO DE DIVULGACIÓN", titulo="Agentes de inteligencia artificial en órbita", tam_titulo=54,
    lema="…y el problema de saber si funcionan",
    autor="Alan Rosas Palacios", instit="Doctorado · Instituto Politécnico Nacional",
    pie="Agentes de IA en órbita · Alan Rosas Palacios", cierre_titulo="Sepamos que la medición significaba algo",
    titulo_plano="Seminario de divulgación: Agentes de inteligencia artificial en órbita — y el problema de saber si funcionan",
    nota_md=("Audiencia: comunidad del posgrado (técnica, pero no de esta especialidad). Contrato: aquí se **explica**, no se defiende. "
             "Fecha por confirmar. Las cifras salen todas de la lista verificada del guion del comité; no improvisar otras en vivo. "
             "Nunca decir «el primero del mundo»."),
)

DIAPOS = [
    ("portada",
     "Buenas tardes. Voy a empezar con una historia, no con una definición. Una historia que ya ocurrió sobre nuestras cabezas, "
     "en la Estación Espacial Internacional, y que tiene un giro que no es espacial: es metodológico. "
     "Soy Alan Rosas Palacios, hago un doctorado en el Instituto Politécnico Nacional sobre cómo gobernar de forma autónoma las redes 6G "
     "que incluyen satélites. Y mi tesis nació de una incomodidad muy simple: si pongo inteligencia artificial a decidir dentro de una red, "
     "¿cómo voy a saber si funciona? Esa pregunta parece fácil y no lo es. Lo que voy a compartir con ustedes es por qué, "
     "y qué estoy haciendo para responderla."),

    ("texto", "La idea de hoy, en una frase", "Si al final pueden repetirla, la charla funcionó",
     ["Ya hay agentes de inteligencia artificial operando en el espacio",
      "Los organismos que definen el 6G están escribiendo ahora las reglas que deberán seguir",
      "La pregunta pendiente no es si funcionan mejor, sino cómo sabríamos si funcionan",
      "Y las pruebas con las que el campo decide eso están rotas"],
     "Les adelanto la idea completa, para que todo lo demás cuelgue de ella. Primero: ya hay agentes de inteligencia artificial operando en el espacio, "
     "no en una película, en hardware real. Segundo: los organismos que definen cómo serán las redes 6G están escribiendo, en este momento, "
     "las reglas que esos agentes deberán seguir. Tercero, y aquí está lo que casi nadie pregunta: no si funcionan mejor, sino cómo sabríamos si funcionan. "
     "Y cuarto, la parte incómoda: resulta que las pruebas con las que buena parte del campo decide eso están rotas. "
     "Vamos a recorrer esas cuatro afirmaciones, en ese orden, y al final les pido que me digan si pueden repetirlas."),

    ("seccion", "Un modelo de lenguaje trabajando en órbita", "Una historia con un giro",
     "Empecemos por la historia. Es corta y tiene números, pero los números se dicen, no se leen."),

    ("video", "AstreaAconseja", "Un modelo de lenguaje diminuto, trabajando en órbita",
     "ASTREA · Estación Espacial Internacional · septiembre de 2025",
     "En septiembre de 2025, en la Estación Espacial Internacional, se puso a funcionar un experimento llamado ASTREA. "
     "Un modelo de lenguaje, de los mismos que están detrás de los asistentes conversacionales, pero diminuto: mil quinientos cuarenta millones de parámetros, "
     "comprimido para caber en el hardware de a bordo. Su trabajo era supervisar el sistema de control térmico de una carga útil. "
     "Y fíjense en un detalle que importa: no decidía. Aconsejaba. Ajustaba un parámetro de un controlador automático, ese sí, el que decide. "
     "Es una arquitectura sensata: lo que se equivoca poco y rápido queda en el controlador clásico, y el modelo de lenguaje aporta criterio, no reflejos. "
     "Guarden esa separación entre quien aconseja y quien decide, porque vuelve más adelante en mi propio trabajo."),

    ("video", "AstreaRitmoOrbita", "Falló por ir al ritmo equivocado",
     "Cada 15 minutos empeoró; al ritmo de la órbita, mejoró",
     "Y ahora el detalle bonito, el que quiero que se lleven. Cuando el modelo daba su consejo cada quince minutos, el sistema empeoró: "
     "las violaciones térmicas subieron un veinticuatro por ciento. Cuando le pusieron el ritmo de la propia órbita, noventa minutos, "
     "una vuelta completa a la Tierra, las violaciones bajaron un sesenta y seis por ciento. "
     "La inteligencia no falló por ser poca. Falló por ir al ritmo equivocado. Pensar despacio sobre un sistema que cambia rápido es peor que no pensar. "
     "Y al revés: alinear la decisión con el ritmo natural del sistema fue la diferencia entre empeorarlo y mejorarlo mucho. "
     "Esa es la primera lección de la charla, y es una lección de diseño, no de tamaño de modelo.",
     "La cifra de duración de episodios (+245.8 % alineado a la órbita, −19.1 % con ventana de 15 min) está en la lista permitida, pero aquí no se "
     "interpreta su sentido; verifícala en arXiv:2509.13380 §4.3 antes de decirla en vivo. Por eso este guion solo usa las violaciones térmicas."),

    ("texto", "Cómo citarlo con honestidad", "Un preprint, no un veredicto",
     ["Preprint de un solo autor, con pocos episodios y sin intervalos de confianza",
      "Sus autores lo presentan como el primer sistema agéntico sobre hardware con herencia de vuelo",
      "No es «el primer modelo de lenguaje en el espacio»: hubo otros antes",
      "El agente aconseja; el controlador decide"],
     "Antes de seguir, una advertencia sobre cómo cito esto, porque es lo que da fuerza a la historia. "
     "Es un preprint, de un solo autor, con pocos episodios y sin intervalos de confianza. Lo digo así, en voz alta, porque preferiría que ustedes "
     "desconfiaran de mí por decirlo a que confiaran por callarlo. Y el reclamo está acotado: sus autores lo presentan como el primer sistema agéntico "
     "ejecutado sobre hardware con herencia de vuelo. No como el primer modelo de lenguaje en el espacio, porque hubo otros antes. "
     "Reconocer los límites de la evidencia no le quita fuerza a la historia. Se la da. Y esa actitud, contar lo que sabemos y también lo que no, "
     "es justo la que después voy a pedirle a todo el campo.",
     "Nunca decir «el primero del mundo» a secas."),

    ("video", "StarlingCuatroNaves", "No es un caso aislado: la coordinación autónoma ya voló",
     "NASA · misión Starling · 2023-2024 · reglas, no aprendizaje",
     "Si alguien piensa que esto es un caso aislado, no lo es. La coordinación autónoma entre varias naves ya voló. "
     "La NASA lo demostró con cuatro CubeSats de la misión Starling, entre 2023 y 2024: la primera operación autónoma completamente distribuida "
     "de múltiples naves espaciales. Sin un líder central, cada nave decidiendo con las demás. "
     "Solo que ahí la inteligencia no era aprendida. Era un planificador clásico, de reglas y lógica, escritas por personas. "
     "Y el paso a sesenta naves se probó solo en simulación en tierra. "
     "Eso importa para lo que sigue: lo que está entrando ahora es la parte aprendida, la que no se escribe regla por regla, "
     "y esa es exactamente la parte que sabemos medir peor."),

    ("seccion", "Por qué esto era inevitable", "Una cuestión de aritmética",
     "Ahora, por qué creo que esto no es una moda pasajera sino algo inevitable. Y la razón cabe en tres números."),

    ("video", "AritmeticaDeLaEscala", "Más de dieciséis mil satélites; casi nueve de cada diez se mueven",
     "Cargas activas en órbita · corte de agosto de 2026",
     "Hay dieciséis mil doscientos setenta y nueve satélites activos en órbita, con corte a agosto de 2026. "
     "De ellos, diez mil setecientos cuarenta y dos son de una sola constelación, Starlink: dos de cada tres son de una sola empresa. "
     "Y el ochenta y seis punto ocho por ciento de las cargas activas son maniobrables: casi nueve de cada diez se mueven a propósito. "
     "Es decir, el sistema es dinámico por construcción, no porque algo lo perturbe de vez en cuando. "
     "Compárenlo con el círculo diminuto de allá: es lo que un operador humano puede supervisar con atención real. Decenas. No miles."),

    ("cita", "Nadie supervisa dieciséis mil satélites", "La automatización no es una elección tecnológica: es aritmética",
     "Un operador humano puede supervisar decenas de satélites. Nadie supervisa dieciséis mil. "
     "La automatización no es una elección tecnológica: es aritmética. Déjenme repetirlo despacio, porque es la frase que justifica todo lo demás: "
     "no automatizamos porque sea elegante, automatizamos porque de otro modo no cabe."),

    ("video", "EstandaresEscribenAhora", "Los estándares de 6G se están escribiendo ahora",
     "IETF, ETSI y 3GPP definen qué puede hacer un agente de red",
     "Y esto no es ciencia ficción regulatoria: está pasando ahora, en los estándares. Los organismos que definen cómo funcionarán las redes 6G, "
     "el IETF, ETSI y el 3GPP, están escribiendo en este momento las reglas para agentes de red: qué puede hacer un agente, qué no debe hacer nunca, "
     "qué tiene que registrar. Hay un borrador del IETF de 2026 que lo dice en lenguaje normativo: un agente de dispositivo no debe ejecutar acciones "
     "que violen las políticas, y todas sus acciones significativas deben quedar registradas. "
     "El 3GPP ya concluyó un estudio de requisitos para agentes de inteligencia artificial de red, y sitúa el congelamiento de la primera versión 6G "
     "potencialmente a inicios de 2029. ETSI pasó de estudiar agentes a especificar una entidad de agente autónomo. "
     "El vocabulario con el que se va a leer todo esto se está fijando ahora."),

    ("texto", "Lenguaje normativo, en el texto original", "Borrador del IETF sobre agentes de dispositivo, 2026",
     ["«A DA MUST NOT be allowed to take actions that violate these policies»",
      "«All significant actions taken by a DA MUST be logged»",
      "Tres capas de agentes, hasta un agente en el elemento de red",
      "Las palabras MUST y MUST NOT son lenguaje de estándar: no sugieren, obligan"],
     "Les enseño la cita completa, porque en pantalla impresiona más que dicha. Es del borrador del IETF sobre agentes de dispositivo. Dos frases. La primera: "
     "un agente de dispositivo no debe poder ejecutar acciones que violen estas políticas. La segunda: todas las acciones significativas de un agente deben quedar registradas. "
     "Fíjense en las palabras en mayúsculas, MUST y MUST NOT. En un documento de estándares no son un énfasis, son una obligación: es lenguaje de norma. "
     "El borrador define tres capas de agentes, hasta un agente en el propio elemento de red. Es decir, ya hay una idea bastante concreta de cómo deben comportarse "
     "estos agentes, cómo deben limitarse y cómo deben rendir cuentas. Ahora miren lo que falta en ese documento."),

    ("video", "BuscarSatelite", "Busqué la palabra «satélite» en ese documento",
     "Cero veces",
     "Aquí está el dato que a mí me cambió el año. Tomé ese borrador del IETF, el de los agentes de dispositivo, y busqué la palabra satélite. "
     "Cero veces. Busqué también las siglas de las redes no terrestres. Cero. "
     "No lo digo como crítica: es normal que un estándar arranque por lo terrestre. Lo digo porque ahí es donde encaja el trabajo de un doctorando. "
     "Hay una arquitectura de agentes que se está normalizando, y el caso del agente que vive en un satélite todavía no está en la conversación. "
     "Si alguna vez se preguntan qué puede aportar alguien en formación a un campo tan grande, la respuesta suele estar en esos ceros."),

    ("video", "SateliteDeviceAgent", "El hueco: un agente de red que vive en órbita",
     "Contacto intermitente, energía finita, límites regulatorios",
     "Ese cero deja libre un hueco concreto, y es la parte de esta charla que más preguntas genera. Un agente en el elemento de red, pero en órbita. "
     "Porque un agente en tierra tiene tres lujos que uno en un satélite no tiene. Contacto continuo: en órbita, el enlace va y viene por ventanas. "
     "Energía ilimitada: un satélite tiene batería finita, que se gasta en sombra y se recarga al sol. "
     "Y una regulación local: en el espacio los límites vienen de reglas internacionales que dicen dónde y cuándo se puede emitir. "
     "Un agente de esa clase tiene que decidir bien con menos información, menos energía y más reglas. "
     "Lo presento como un hueco abierto, no como un resultado mío: es una pregunta que me parece que vale la pena que alguien responda."),

    ("video", "NormaSinIA", "Y la norma de autonomía espacial no menciona la IA",
     "ECSS-E-ST-70-11C, revisada en octubre de 2025",
     "Y hay una segunda ausencia igual de elocuente. La norma europea de autonomía de vehículos espaciales, ECSS, revisada en octubre de 2025, "
     "menciona ochenta y una veces la palabra autonomía. Y menciona cero veces inteligencia artificial, cero veces aprendizaje automático "
     "y cero veces constelación. Ni una sola vez. "
     "Piénsenlo: tenemos agentes de inteligencia artificial volando y una escala de autonomía vigente que no sabe que existen. "
     "Si me preguntan qué pasa si el agente se equivoca allá arriba, esa es la respuesta honesta: el marco normativo para esto todavía no existe. "
     "Y por eso importa tanto saber medir bien lo que estos agentes hacen."),

    ("seccion", "¿Y si el examen está mal hecho?", "Aquí cambia el registro",
     "Hasta aquí fue una historia. Ahora viene el problema de verdad, y voy a empezar con una analogía que funciona con cualquier audiencia."),

    ("video", "TermometroRoto", "Dos médicos y un termómetro roto",
     "Una analogía sobre medir sin haber revisado el instrumento",
     "Imaginen que quieren saber cuál de dos médicos diagnostica mejor. Les dan a los dos el mismo termómetro y los mandan a ver pacientes. "
     "Uno acierta el setenta por ciento, el otro el setenta y dos. Concluyen que el segundo es mejor. "
     "Salvo que nadie revisó el termómetro. Y el termómetro marca treinta y siete grados siempre, pase lo que pase con el paciente. "
     "Con ese instrumento, la diferencia entre los dos médicos no significa nada. No es que la medición sea imprecisa: es que no hay nada que medir. "
     "Fíjense qué traicionero es esto: los números salen, las barras se dibujan, y nadie sospecha, porque el error no está en los médicos ni en las cuentas. "
     "Está en el instrumento, y el instrumento casi nunca se revisa. Las cifras de esta analogía son de ejemplo."),

    ("texto", "El mismo ejemplo, con números", "Cifras de ejemplo para entender la idea",
     ["Médico A acierta 70 de cada 100; Médico B, 72 de cada 100",
      "El termómetro marca 37° a todos los pacientes, estén o no enfermos",
      "Los dos «aciertan» solo cuando el paciente, por azar, estaba sano",
      "La diferencia de dos puntos es ruido: el instrumento no discrimina"],
     "Lo pongo con números, como si estuviéramos en una pizarra. Cien pacientes. El médico A acierta setenta, el B acierta setenta y dos, y con eso uno diría que B es mejor. "
     "Pero el termómetro marca treinta y siete grados a todos, estén o no enfermos. Entonces, ¿cuándo aciertan ambos? Solo cuando el paciente, por azar, estaba sano. "
     "Lo que separa a A de B, esos dos puntos, es ruido: cuál de los dos tuvo un par de pacientes sanos más. El instrumento no discrimina entre enfermo y sano, "
     "así que no puede discriminar entre buen médico y mal médico. "
     "Son números de ejemplo, no míos. Pero la estructura es exactamente la de un banco de pruebas que no premia adaptarse: la diferencia que se ve, aunque sea reproducible, no significa nada."),

    ("video", "PoliticaQueNoMira", "Una política que no mira nada gana escenarios",
     "NeurIPS 2023 · el banco de pruebas estándar de agentes que cooperan",
     "Ahora el golpe, que es real y es de otros, no mío. En 2023, un grupo de investigadores publicó en NeurIPS, una de las conferencias más importantes "
     "de inteligencia artificial, un resultado incómodo sobre SMAC, el banco de pruebas estándar con el que todo un subcampo, el de varios agentes que aprenden a cooperar, "
     "comparaba sus algoritmos. Probaron una política que no mira nada. No observa el estado del mundo. Solo cuenta el tiempo y ejecuta una secuencia fija. "
     "Esa política gana escenarios del benchmark. "
     "Léanlo con calma: un agente con los ojos vendados, que repite lo mismo cada vez, le gana a algoritmos sofisticados en el examen que todos usaban. "
     "El examen, en esos escenarios, no premiaba mirar.",
     "Resultado de terceros: preséntalo como tal. Las páginas de las actas de NeurIPS no están verificadas."),

    ("video", "SemillasQueInvierten", "Con diez semillas, el resultado se invierte",
     "Agosto de 2026 · un estudio en otro dominio, el mismo problema de medición",
     "Y en agosto de 2026, otro grupo mostró algo todavía más incómodo sobre el mismo tipo de comparaciones. Con cinco semillas aleatorias, un algoritmo parece mejor. "
     "Con diez, el resultado se invierte. Una política completamente aleatoria puntúa dentro del rango de las entrenadas. "
     "Y ninguna de las comparaciones sobrevive a la corrección estadística por comparaciones múltiples. "
     "Una aclaración de honestidad: ese estudio es sobre un simulador de fútbol, no sobre redes de satélites. Lo traigo porque el problema de medición es el mismo. "
     "Traducción: durante años, buena parte del campo estuvo comparando médicos con un termómetro roto.",
     "Yılmaz y Çelikcan, Applied Sciences 16(15):7650. Es Google Research Football, no NTN: dilo si preguntan."),

    ("texto", "Tres preguntas para leer cualquier comparación", "Sirven para papers, demos y notas de prensa",
     ["¿El entorno premia adaptarse, o una estrategia fija ya es óptima?",
      "¿Cuántas semillas se usaron, y se invierte el resultado con más?",
      "¿Se corrigió por hacer muchas comparaciones a la vez?"],
     "Como esto puede sonar abstracto, les dejo tres preguntas prácticas para leer cualquier comparación de algoritmos, en un paper, en una demostración o en una nota de prensa. "
     "Una: ¿el entorno premia adaptarse, o una estrategia fija ya es óptima? Es la del termómetro. "
     "Dos: ¿cuántas semillas se usaron, y el resultado se sostiene si se usan más? Es la de la inversión con diez semillas. "
     "Tres: ¿se corrigió por hacer muchas comparaciones a la vez? Si uno compara veinte cosas, alguna gana por azar. "
     "No hace falta ser especialista para hacer esas tres preguntas, y una respuesta evasiva ya dice bastante. "
     "Mi tesis es un intento de convertir la primera de ellas en una medición obligatoria."),

    ("cita", "Si el entorno no premia adaptarse, comparar algoritmos sobre él no significa nada.",
     "Y eso no se sabe hasta que se mide.",
     "Esta es la frase que sostiene toda mi tesis. Si el entorno no premia adaptarse, comparar algoritmos sobre él no significa nada. "
     "Y esto es lo que hace que la frase sea más que una queja: eso no se sabe hasta que se mide. "
     "No basta con sospecharlo, ni con que el simulador parezca realista. Hay que medirlo, antes de comparar nada. Voy a mostrarles cómo."),

    ("seccion", "Qué estoy construyendo", "Tres piezas, sin jerga",
     "Ahora sí, mi trabajo. Son tres piezas. Las cuento sin jerga y, cuando aparezca un término técnico, lo traduzco."),

    ("video", "PadaCuatroCajas", "Pieza 1: gobernar la red, no solo controlarla",
     "PADA · Percepción, Análisis, Decisión, Acción",
     "La primera pieza es una arquitectura, que llamo PADA: Percepción, Análisis, Decisión, Acción. "
     "La idea de fondo es separar al que entiende del que decide, precisamente por la lección de ASTREA: la parte lenta y semántica no puede vivir dentro del lazo rápido. "
     "Fíjense en los dos relojes de la pantalla: el análisis piensa despacio, la decisión responde rápido, y las cajas se comunican por interfaces programables. "
     "Otra ventaja práctica: cuando algo falla, se sabe en qué caja. Si la red no vio el problema, si lo entendió mal, si decidió mal o si no pudo ejecutar. "
     "Y no es una preferencia estética: es la separación que la arquitectura de referencia de las redes abiertas ya impone. "
     "Aclaro que esto es trabajo en desarrollo, parte de mi tesis, no un producto terminado."),

    ("video", "ModeloArribaRLAbajo", "Lo lento no puede vivir dentro del lazo rápido",
     "Modelo de lenguaje arriba, aprendizaje por refuerzo abajo",
     "Alguien preguntará: ¿por qué no usar directamente un modelo de lenguaje grande para todo? Porque la propia industria acota dónde sirve. "
     "Un borrador del IETF de 2026, firmado por el autor principal del estándar de redes basadas en intención, señala que la telemetría cruda de una red "
     "excede la capacidad de procesamiento de estos modelos en el futuro previsible, salvo que se tomen otras medidas para reducir el volumen de datos "
     "en varios órdenes de magnitud. Esa coda importa. "
     "El patrón que se está imponiendo es: modelo de lenguaje arriba, para traducir intenciones y explicar; aprendizaje por refuerzo abajo, para decidir rápido. "
     "Y la historia de ASTREA con la que abrí es exactamente eso, medido en vuelo.",
     "Decir la coda completa de la cita («salvo que se tomen otras medidas…»)."),

    ("video", "DecisionConjunta", "Pieza 2: una sola decisión conjunta bajo información incompleta",
     "El modelo formal, en treinta segundos",
     "La segunda pieza es un modelo formal, y le doy treinta segundos, porque esta audiencia no necesita el formalismo: necesita saber que existe. "
     "Trata el problema de varias capas de red, radio, transporte y núcleo, como una sola decisión conjunta, donde cada parte ve solo una fracción de lo que pasa "
     "y todas comparten una recompensa común. Es la diferencia entre tres controladores que cada uno optimiza lo suyo y chocan, "
     "y un conjunto que se coordina. Si a alguien le interesa el formalismo, con gusto se lo cuento después de la charla."),

    ("video", "MargenAdaptativoIdea", "Pieza 3: el margen adaptativo",
     "¿Cuánto se puede ganar, como máximo, por adaptarse?",
     "La tercera pieza es la que considero mi aportación. Defino una cantidad que llamo margen adaptativo, y responde a esta pregunta: "
     "en este entorno, ¿cuánto se puede ganar, como máximo, por adaptarse a lo que pasa, frente a la mejor estrategia fija posible? "
     "Piénsenlo como un terreno. Si el terreno tiene relieve, elegir bien el camino importa: la mejor ruta que se adapta le gana por mucho a la mejor ruta recta. "
     "Ahí el margen es grande y tiene sentido comparar algoritmos que aprenden. "
     "Si el terreno es llano, todos los caminos llevan a lo mismo. El margen es cero, la mejor estrategia fija ya es óptima, y ningún resultado sobre ese entorno "
     "significa nada. Ni a favor ni en contra. Es el termómetro, pero ahora con una regla para saber si marca siempre lo mismo."),

    ("video", "CompuertaAntesDeCorrer", "Comprometerse por escrito a tirar la medición",
     "Umbral fijado antes de correr; sin compuerta, sin reporte",
     "Y aquí está el compromiso. Fijo un umbral, el veinticinco por ciento, antes de correr los experimentos, y lo convierto en una compuerta. "
     "Si el entorno la pasa, se pueden comparar algoritmos. Si no la pasa, los resultados de algoritmos sobre él no se reportan. No se discuten. No existen. "
     "Fíjense en el orden, que es lo que lo hace honesto: el umbral se clava primero. Si yo pudiera bajarlo hasta que mi entorno pasara, la compuerta no valdría nada. "
     "Lo que la hace valer es que me ata las manos antes de ver los resultados. Es una tesis que empieza midiendo su propio instrumento."),

    ("texto", "Lo mío es el uso, no la idea", "Lo que ya existía y lo que aporto",
     ["Revisar el entorno antes de entrenar: hay trabajos que lo hacen desde 2020",
      "En 2026 se publicó un pre-filtro de gemelos digitales antes de entrenar al agente",
      "La cantidad se apoya en un resultado teórico publicado en 2008",
      "Lo mío: fijar el umbral antes de correr y convertirlo en una compuerta"],
     "Quiero ser preciso sobre qué es mío y qué no, porque es fácil exagerar. Revisar el entorno antes de entrenar no es idea mía: hay trabajos que lo hacen desde 2020, "
     "y en 2026 se publicó uno que pre-filtra gemelos digitales antes de entrenar al agente. La cantidad que uso se apoya en un resultado teórico publicado en 2008. "
     "Lo mío es el uso. Fijo el umbral antes de correr los experimentos y lo convierto en una compuerta: si el entorno no lo pasa, los resultados no se reportan. "
     "Busqué precedentes de esa combinación específica y no los encontré, pero eso es una búsqueda mía, no una prueba de que no existan. "
     "Prefiero un reclamo estrecho que aguante a uno ancho que se caiga con una búsqueda.",
     "No decir «nadie valida el entorno antes del algoritmo» (falso: Xu y Chen 2021, Furuta 2021, Oller 2020, Tao et al. 2026)."),

    ("cita", "Una tesis que empieza midiendo su propio instrumento",
     "Y se compromete por escrito a tirar sus resultados si no pasa",
     "Una tesis que empieza midiendo su propio instrumento, y que se compromete por escrito a tirar sus propios resultados si el instrumento no pasa. "
     "Suena a pocas ganas de ganar. Es lo contrario: es la única manera de que una victoria, cuando llegue, valga algo. Y ahora les cuento cómo me fue."),

    ("seccion", "Lo que encontré, incluido lo que salió mal", "Este es el bloque que da credibilidad",
     "Este bloque lo cuento en primera persona y sin defenderme. Es el que da credibilidad y por eso no lo recorto."),

    ("video", "RecorridoDelMargen", "Mi primer banco de pruebas reprobó",
     "Margen de 1.7 % en la versión 1; 31.8 % en la versión 2, con umbral de 25 %",
     "Primero: mi propio banco de pruebas reprobó. La primera versión del entorno que construí tenía un margen adaptativo del uno punto siete por ciento. "
     "Prácticamente cero. Era un termómetro roto, y era el mío. Si hubiera corrido los experimentos ahí, habría obtenido gráficas bonitas y conclusiones sin valor. "
     "La segunda versión llegó a treinta y uno punto ocho por ciento, con el umbral en veinticinco. "
     "Una honestidad más: de ese treinta y uno punto ocho, lo que efectivamente logré alcanzar con una política real fue cerca del diez por ciento. Lo cuento en un momento. "
     "Y después hubo un episodio peor, que también cuento: en un piloto, un banco mal configurado produjo resultados espectaculares, tres veces mejores que el techo del entorno real, lo cual es imposible. "
     "El protocolo los detectó y los anuló. Esa es la mejor prueba de que el marco sirve. Un sistema de validación que nunca invalida nada no está midiendo nada.",
     "El 31.8 % es la envolvente (estimador cota inferior); el margen decisional alcanzable medido en G2b es 9.5 %. Reporta el par, no el número suelto. "
     "El 25 % también aparece como objetivo de diseño del entorno: la primera validación es en parte calibración."),

    ("video", "AlgoritmoVsEstatica", "Con el instrumento válido, el algoritmo ganó",
     "Entre 9.5 % y 16.3 % mejor que la mejor estrategia fija, en las tres semillas",
     "Segundo: cuando el instrumento ya era válido, el algoritmo ganó. El método de aprendizaje multiagente superó a la mejor estrategia fija en las tres semillas aleatorias "
     "probadas, con mejoras de entre nueve punto cinco y dieciséis punto tres por ciento. Y alcanzó entre el ochenta y cuatro y el ochenta y siete por ciento "
     "del rendimiento de una política con información privilegiada, una especie de trampa autorizada que sirve de techo de referencia, y que es una cota inferior del óptimo, "
     "no el máximo teórico. "
     "Es un resultado modesto y es honesto. Modesto, porque el entorno todavía es pequeño. Honesto, porque el instrumento estaba certificado antes de correr. "
     "No les estoy diciendo que la inteligencia artificial ganó. Les estoy diciendo que ahora, si gana, sé qué significa. Tres semillas, no treinta."),

    ("video", "VarianteSimpleNoEmpeora", "Un resultado negativo, publicable",
     "La variante sin componente no lineal no empeora (n = 3)",
     "Tercero: un resultado negativo. Probé una variante más simple del algoritmo, sin su componente no lineal. No empeora. "
     "Conclusión provisional: en este régimen, la complejidad extra no se gana su sitio. "
     "Y lo digo con cautela: son tres semillas. Es un diagnóstico, no una demostración, y no tiene potencia estadística para afirmar que son equivalentes. "
     "Pero en un campo con un fuerte sesgo de publicación, donde nadie reporta lo que no funciona o lo que sobra, poder decir esto en voz alta es parte del valor del marco. "
     "Un resultado que otros habrían escondido, aquí es un producto.",
     "No llamarlo «resultado negativo demostrado»: es un diagnóstico con n = 3."),

    ("seccion", "Lo que viene, y por qué corre prisa", "Lo honesto primero",
     "Y ahora lo que viene. Empiezo por lo honesto, que es lo que me toca decir."),

    ("video", "SimuladorMasReal", "El siguiente paso: ¿sobrevive el margen al realismo?",
     "Órbitas reales, enlaces entre satélites y latencias medidas · propuesto",
     "Lo honesto primero: mi entorno actual es pequeño, con dos satélites, y el umbral que le exigí aparecía también como objetivo de diseño. "
     "Eso significa que la primera validación es, en parte, calibración. "
     "El siguiente paso, que planteo pero aún debo acordar con mi asesor, es la prueba de verdad: llevar el marco a un simulador con órbitas reales, enlaces entre satélites "
     "y latencias medidas, y preguntar si el margen sobrevive al aumento de realismo. "
     "Y esto es lo que más me gusta de haber diseñado así la tesis: si el margen no sobrevive, eso también es un resultado. Sabríamos a qué nivel de realismo deja de haber "
     "algo que aprender. Esa clase de pregunta, planteada así, no la encontré en la literatura que revisé.",
     "El CLAUDE.md de la tesis (2026-09-17) registra que el Dr. Barrera aprobó el memo consolidado, pero deja pendiente el detalle punto por punto. "
     "Confirma qué de esto quedó ratificado antes de decir «aún debo acordar». Dice «propuesto» mientras no lo confirmes."),

    ("video", "PrisaDosMilVeintinueve", "El vocabulario se está fijando ahora",
     "Freeze de la primera versión 6G a inicios de 2029; mi defensa cae del otro lado",
     "¿Y por qué corre prisa? El 3GPP sitúa el congelamiento de la primera versión del estándar 6G potencialmente a inicios de 2029, "
     "y ya está evaluando qué protocolos usarán los agentes de red para hablar entre sí. "
     "Mi doctorado va de febrero de 2026 a febrero de 2030, voy en el segundo semestre de ocho. Mi defensa cae justo del otro lado de esa frontera. "
     "Eso tiene una consecuencia práctica: lo que aporte tiene que poder leerse en el vocabulario que ese estándar va a fijar, no en uno anterior. "
     "Por eso mi posición es deliberadamente estrecha. No pretendo reinventar la arquitectura de agentes, que ya se está normalizando. "
     "Pretendo aportar lo que a ese trabajo le falta: el caso de los satélites y la validación del instrumento."),

    ("texto", "Para llevarse", "Tres ideas",
     ["Ya hay inteligencia artificial decidiendo en el espacio, y las reglas se escriben ahora",
      "El campo compara algoritmos con pruebas que a veces no miden nada",
      "Primero medir el instrumento, y tirar los resultados si no pasa"],
     "Si se llevan tres cosas, que sean estas. Una: ya hay inteligencia artificial decidiendo en el espacio, con ritmo, con reglas y con límites, "
     "y las reglas se están escribiendo ahora. Dos: el campo compara algoritmos con pruebas que a veces no miden nada, "
     "y no lo sabe porque nadie lo mide. Tres: la respuesta no es un algoritmo mejor, sino medir primero el instrumento y comprometerse por escrito a tirar "
     "los resultados si no pasa. Si pueden repetir esas tres, la charla cumplió."),

    ("cita", "No estoy tratando de demostrar que la inteligencia artificial gana.",
     "Estoy tratando de que, cuando gane o cuando pierda, sepamos que la medición significaba algo.",
     "Y con esto cierro. No estoy tratando de demostrar que la inteligencia artificial gana. Estoy tratando de que, cuando gane o cuando pierda, "
     "sepamos que la medición significaba algo."),

    ("cierre",
     "Muchas gracias. Con gusto recibo preguntas, y les adelanto que tengo respuestas preparadas para las más frecuentes: si los satélites ya piensan solos, "
     "qué pasa si el agente se equivoca, si esto sirve de algo en México, por qué no usar un modelo de lenguaje para todo, y cuánto me falta."),

    ("respaldo", "¿Los satélites ya piensan solos?", "Deciden solos algunas cosas; lo aprendido apenas entra",
     ["Sí deciden solos algunas cosas, desde hace tiempo", "Pero con reglas escritas por humanos, no aprendidas",
      "Lo que entra ahora es la parte aprendida", "Por eso importa saber medirla"],
     "Deciden solos algunas cosas, sí, desde hace tiempo, pero con reglas escritas por humanos, no aprendidas. Lo que está entrando ahora es la parte aprendida, "
     "y por eso importa saber medirla."),

    ("respaldo", "¿Y si el agente se equivoca allá arriba?", "Esa es exactamente la pregunta abierta",
     ["La norma ECSS vigente (oct-2025): 81 veces «autonomía»", "Cero veces IA, aprendizaje automático o constelación",
      "El marco normativo para esto no existe todavía"],
     "Esa es exactamente la pregunta abierta. Las escalas de autonomía espacial vigentes, la norma europea ECSS revisada en octubre de 2025, no mencionan ni una sola vez "
     "inteligencia artificial, aprendizaje automático ni constelación. Hay ochenta y una apariciones de autonomía y cero de IA. El marco normativo para esto no existe todavía."),

    ("respaldo", "¿Esto sirve para algo en México?", "La conectividad satelital llega donde la fibra no",
     ["Vía realista para zonas donde la fibra no llega",
      "Las reglas de gobierno de las constelaciones se escriben en foros internacionales ahora",
      "Tener gente formada aquí no es un lujo"],
     "La conectividad satelital es la vía realista para zonas donde la fibra no llega, y las reglas de cómo se gobiernan esas constelaciones se están escribiendo en foros "
     "internacionales ahora. Tener gente formada en esto aquí no es un lujo."),

    ("respaldo", "¿Por qué no un modelo de lenguaje para todo?", "Lenguaje arriba, refuerzo abajo",
     ["La telemetría cruda excede la capacidad de estos modelos en el futuro previsible",
      "…salvo reducir el volumen de datos en varios órdenes de magnitud",
      "Lenguaje arriba para traducir y explicar; refuerzo abajo para decidir rápido"],
     "Porque la propia industria acota dónde sirve. Un borrador del IETF de 2026 señala que los datos de telemetría de una red exceden la capacidad de procesamiento de estos modelos "
     "en el futuro previsible, salvo que se reduzca el volumen de datos en varios órdenes de magnitud. El patrón que se impone es modelo de lenguaje arriba y aprendizaje por refuerzo abajo. "
     "Y ASTREA es exactamente eso, medido en vuelo."),

    ("respaldo", "¿Cuánto te falta?", "Segundo semestre de ocho",
     ["Doctorado: febrero de 2026 a febrero de 2030", "Voy en el segundo semestre de ocho"],
     "El doctorado va de febrero de 2026 a febrero de 2030. Voy en el segundo semestre de ocho."),
]


if __name__ == "__main__":
    main(CFG, DIAPOS)
