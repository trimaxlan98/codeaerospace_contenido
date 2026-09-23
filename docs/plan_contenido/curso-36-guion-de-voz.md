# Curso 36 — Guion de voz (48 clips)

El VPS no tiene guionista automático (`MS_TTS_GUIONISTA=ninguno`, voz
`edge`): la narración se escribe aquí, a mano, y `guiones.py --solo-audio`
la sintetiza desde los `.txt`. Presupuesto: **2.2 palabras por segundo de
clip, con 10 % de margen** (un clip de 29 s admite ~57 palabras). Cada
bloque `### N.M.K` es el `.txt` de ese clip, tal cual. La herramienta
`studio/tools/voz_tesis6g.py` los reparte en `guiones/<slug>/`.

Reglas de honestidad (R6 de la tesis): lo que la tesis no ha corrido no se
dice como hecho (G3); el oráculo es cota inferior; la envolvente es de
Oliehoek 2008; nunca "el primero".

## 1.1 La red que se mueve

### 1.1.1
Una persona puede vigilar unas decenas de satélites. En órbita hay más de dieciséis mil activos, y cada punto de esta malla representa cien. Dos de cada tres pertenecen a una sola constelación. Nadie puede supervisar esto satélite por satélite: la automatización no es una elección técnica, es aritmética.

### 1.1.2
Un satélite a seiscientos kilómetros, con la Tierra a escala. Desde la estación solo sirve por encima de diez grados de elevación. Asoma, pasa casi por el cenit y se pierde. El pase entero dura menos de nueve minutos, y el retardo de ida cambia de dos a más de seis milisegundos en ese tiempo.

### 1.1.3
Si alejamos la vista, el pase era un arco pequeño de una vuelta completa. El satélite sigue su órbita y la estación se queda sola: hay enlace poco más del nueve por ciento de la vuelta. El resto, casi ochenta y ocho minutos, no hay nadie arriba.

### 1.1.4
Por eso se usan trenes de satélites que se relevan. Con suficiente solape, la estación nunca se queda sola. Pero si los pases apenas se tocan, la rotación de la Tierra abre un hueco de unos cuarenta segundos. La red no está siempre ahí: hay que gobernarla, no fijarla.

## 1.2 Una red, dos mundos

### 1.2.1
Este es el banco de pruebas de la tesis: dos satélites, un gateway en tierra y una ruta terrestre alterna hacia el resto de la red. Cada satélite puede usar un canal de espectro bajo, uno alto, o dejar el tráfico a la ruta alterna. Tres agentes deciden a la vez, cada uno con lo que ve.

### 1.2.2
La visibilidad de cada satélite sube y baja con su órbita. Cuando cae por debajo de cero coma treinta y cinco, el enlace por espectro se desploma al diez por ciento. Cada satélite pasa así veinticinco de cada sesenta pasos, y los dos a la vez, uno de cada seis.

### 1.2.3
La ruta terrestre no es refugio: el gateway se congestiona en un ciclo de cuarenta y cinco pasos, y en el pico su capacidad cae al treinta y cinco por ciento. Ese ciclo no coincide con la órbita: el dibujo solo se repite cada ciento ochenta pasos.

### 1.2.4
Hay un tercer mecanismo que nadie observa: uno de los canales se degrada y cambia cada ochenta pasos. Ningún agente lo ve, pero su interferencia lo delata: sube hasta saturar y cae a la mitad en menos de dos pasos cuando se abandona el canal. Tres ritmos que no coinciden: adaptarse puede pagar.

## 1.3 Gobernar no es controlar

### 1.3.1
Primero, las redes se configuraban a mano, nodo por nodo. Luego llegaron los automatismos por función, como las redes autoorganizadas del estándar. La tercera era es un lazo que gobierna el conjunto. La industria la mide en niveles de autonomía, del cero al cinco.

### 1.3.2
En la Estación Espacial, un modelo de lenguaje aconseja al control térmico de una carga útil. Aconsejando cada quince minutos, las violaciones térmicas subieron un veinticuatro por ciento. Al ritmo de la órbita, noventa minutos, bajaron dos tercios. La inteligencia no falló por poca: falló por ir al ritmo equivocado.

### 1.3.3
Las redes abiertas separan los lazos por su escala de tiempo: el de tiempo real, el casi real, entre diez milisegundos y un segundo, y el lento, de más de un segundo. La arquitectura de la tesis se apoya en esa separación: lo que piensa despacio va por fuera, lo que actúa rápido, por dentro.

### 1.3.4
Si la política está desacoplada de la infraestructura, es un cartucho: el mismo zócalo recibe una estática, una heurística ingenua o una afinada. La tesis midió las tres. La ingenua queda por debajo de la estática; la afinada, elegida entre doscientas setenta, apenas la supera. El rival importa.

## 1.4 Decidir sin verlo todo

### 1.4.1
El estado del mundo tiene diez números. Cada agente ve seis, y no los mismos. Hay una casilla del estado que ningún agente observa: qué canal está degradado. Decidir así es la situación normal en una red distribuida, no la excepción.

### 1.4.2
Sin ver el canal, se puede creer. Un filtro de dos hipótesis toma una señal ruidosa, interferencia alta o baja, que se equivoca el quince por ciento de las veces. La creencia sigue al estado oculto casi todo el tiempo, y tarda unos pocos pasos en darse cuenta de cada cambio.

### 1.4.3
Tres agentes con tres acciones cada uno dan veintisiete acciones conjuntas. En el banco de la tesis, la mejor combinación fija es que los tres usen la ruta alterna. Esa es la gestión estática contra la que todo lo demás tendrá que medirse.

### 1.4.4
Si cada agente decide con su historia de observaciones, el número de políticas posibles explota: a diez pasos ya hay más de diez elevado a mil cuatrocientos. El problema es de los más difíciles que se conocen. Pero ojo: que sea difícil de calcular no dice nada de cuánto se gana adaptándose.

## 2.1 Aprender por refuerzo

### 2.1.1
Lo único que recibe un agente de refuerzo es un número por paso. En la tesis, ese número suma el caudal, resta la latencia y castiga fuerte la interferencia. En este paso de ejemplo, ochenta de caudal, menos seis, menos uno: setenta y tres. Un episodio tiene cien pasos.

### 2.1.2
Con un juguete del banco de pruebas, dos estados y tres acciones, la tabla de valores aprende sola: con el satélite a la vista conviene el espectro alto; en eclipse, la ruta alterna. Cada celda se corrige hacia la recompensa que de verdad llega. En este juguete, adaptarse vale un ocho por ciento.

### 2.1.3
Sin explorar no se aprende: el agente que nunca prueba otra cosa se queda con la primera acción que eligió. Por eso se explora al azar al principio. El QMIX de la tesis reduce la exploración un uno por mil por episodio, hasta un piso de cinco por ciento, que alcanza hacia el episodio tres mil.

### 2.1.4
Esta es la curva de entrenamiento real de QMIX en la compuerta G2b, cinco mil episodios. Empieza muy por debajo de la mejor estática, la cruza y se estabiliza entre ella y el oráculo. Evaluado sin exploración, supera a la estática en un dieciséis por ciento en esta semilla.

## 2.2 Muchos agentes

### 2.2.1
Dos satélites aprenden por separado a no chocar en el mismo canal. Como cada uno cambia mientras el otro aprende, al principio se persiguen. En mil semillas, tardan una mediana de catorce pasos en coordinarse; un aprendiz conjunto, que decide por los dos, lo hace casi de inmediato.

### 2.2.2
QMIX usa un término medio: entrenamiento centralizado, ejecución descentralizada. Mientras aprende, un mezclador ve el estado global y combina los valores de cada agente. Al desplegarse, el mezclador desaparece y cada agente decide solo, con su propia observación.

### 2.2.3
El mezclador no puede ser cualquier función: tiene que ser monótono, que si un agente mejora el equipo no empeore. Así, lo mejor de cada uno por separado es lo mejor del equipo. La suma y la mezcla monótona lo cumplen en quinientos casos al azar; una no monótona falla en la mayoría.

### 2.2.4
La tesis probó cambiar el mezclador no lineal de QMIX por la simple suma. Con el mismo protocolo, las dos superan a la estática en las tres semillas y quedan pegadas, a menos de tres por ciento. En este entorno, la complejidad extra no se gana su sitio: un resultado negativo, y publicable.

## 2.3 Consenso con traidores

### 2.3.1
Para decidir aunque algunos mientan, hacen falta al menos tres veces los traidores, más uno. Así, dos mayorías cualesquiera comparten al menos una réplica honesta. Y réplicas de más no siempre compran algo: con seis se tolera lo mismo que con cuatro, y el quórum sube a cuatro, no a tres.

### 2.3.2
El consenso clásico va en tres fases: el primario propone, todos confirman a todos, y todos se comprometen. Con cuatro réplicas son veinticuatro mensajes. El tráfico crece con el cuadrado del número de réplicas: con mil, casi dos millones de mensajes por decisión.

### 2.3.3
La tesis propone decidir por grupos: la constelación se parte en grupos de diez que deciden dentro y propagan entre ellos. Con mil satélites, el tráfico baja de casi dos millones a dieciocho mil mensajes, un noventa y nueve por ciento menos. El precio es latencia entre grupos.

### 2.3.4
Y el líder no se elige por turno sino por reputación: tiempo activo, calidad de sus decisiones y fallos. Aquí, el mejor candidato de partida es un traidor que propone decisiones inválidas; cada fallo le resta, y a la primera ronda el liderazgo pasa a otro, sin votación global.

## 2.4 La arquitectura PADA

### 2.4.1
La arquitectura de la tesis se llama PADA: percepción, análisis, decisión y acción, y vuelta a percibir. No es un controlador más dentro de la red, sino una capa de gobernanza por encima de ella, con interfaces para cambiar las políticas sin tocar la infraestructura.

### 2.4.2
Los agentes no pueden contárselo todo: el enlace es el cuello de botella. La teoría del cuello de botella de información dice cuánto de lo relevante sobrevive a cada bit enviado. En este ejemplo gaussiano, con dos bits ya se conserva el ochenta y seis por ciento de lo que importa.

### 2.4.3
PADA no inventa protocolos: se apoya en los de las redes abiertas. El entrenamiento centralizado cae en el controlador lento y la ejecución en el rápido: esa partición ya la induce la arquitectura. Un pase como el de la lección uno, con ida y vuelta de cuatro a trece milisegundos, cabe justo en el lazo rápido.

### 2.4.4
Y una regla: ninguna política nueva toca la red sin pasar antes por su gemelo digital. El gemelo solo la deja salir si el entorno de prueba premia adaptarse, con un margen de al menos veinticinco por ciento. El de la tesis midió treinta y uno coma ocho.

## 3.1 El termómetro roto

### 3.1.1
Imaginemos dos médicos comparados con el mismo termómetro, y uno acierta un poco más. Salvo que el termómetro marca treinta y siete grados siempre, pase lo que pase. Con ese instrumento, la diferencia entre los dos no significa nada: no es que la medición sea imprecisa, es que no hay nada que medir.

### 3.1.2
Pasó de verdad. En el banco de pruebas más usado del aprendizaje multiagente cooperativo, una política que no mira nada, que solo cuenta el tiempo, alcanzaba victorias en muchos escenarios: cada episodio repetía al anterior. Cuando se añadió azar, el plan fijo dejó de servir. Nadie había medido el margen antes.

### 3.1.3
Otra trampa: dos algoritmos idénticos evaluados con cinco semillas. Uno parece mejor. Con diez semillas, el orden se invierte. No es mala suerte: le pasa a uno de cada cuatro experimentos, y la probabilidad sale de una fórmula de dos líneas.

### 3.1.4
De ahí la definición que sostiene la tesis. El margen adaptativo es cuánto gana quien ve todo y elige en cada instante, frente a la mejor opción fija, medido en unidades de esa opción fija. Es una propiedad del entorno, no del algoritmo: primero se mide el termómetro, después se comparan algoritmos.

## 3.2 Lo que el margen acota

### 3.2.1
Hay tres clases de políticas, una dentro de otra: las estáticas, las desplegables, donde cada agente usa lo suyo, y las privilegiadas, que ven el estado. Sus mejores valores quedan ordenados, y de ahí salen dos márgenes. La tesis mide los dos como cotas inferiores: nueve y medio y treinta y uno coma ocho por ciento.

### 3.2.2
La desigualdad que acota a toda política desplegable ya estaba publicada. Es el último eslabón de una escalera de cotas de Oliehoek, Spaan y Vlassis, de dos mil ocho: cada peldaño ve un poco más. La tesis la cita y la cede; lo propio es el uso que le da.

### 3.2.3
Ese uso es el piso de falsabilidad: si el entorno no premia adaptarse, ninguna política adaptativa puede ganarle a la estática. Aquí una opción domina siempre, el oráculo coincide con ella, y cualquier adaptación solo pierde. En un entorno así, comparar algoritmos no informa de nada.

### 3.2.4
Pero la condición es necesaria, no suficiente. Aquí nadie ve qué casilla paga: el margen del entorno crece con las casillas y aun así ninguna política desplegable gana nada. Por eso la tesis exhibe una política que gana. El margen no promete ganancia; sin margen, no hay ganancia posible.

## 3.3 Medir sin engañarse

### 3.3.1
El oráculo de la tesis ve todo, pero solo mira un paso adelante: no es el techo. Mirando dos pasos, con setecientas veintinueve secuencias por decisión, se gana algo más en las tres semillas, siempre menos del uno por ciento. El margen medido es una cota inferior, y ajustada.

### 3.3.2
Desde el mismo estado, dos acciones distintas dejan mundos distintos: la colisión carga la interferencia, y la carga se descarga despacio, un treinta por ciento por paso. La acción de hoy decide el estado de mañana. Por eso el oráculo de un paso no es exacto en este entorno.

### 3.3.3
Otra trampa sutil: la mejor de veintisiete estáticas, elegida por su promedio en pocos episodios, sale sobreestimada; y si el denominador se infla, el margen sale deprimido. Con treinta episodios el sesgo desaparece. La curva de la tesis lo muestra: de cero coma diecinueve a cero coma treinta y dos.

### 3.3.4
Y una guardia automática: toda corrida que supere en más de un cinco por ciento al oráculo se invalida sola. Un piloto mal configurado dio casi tres veces el oráculo, algo que ninguna política legítima puede hacer, y el protocolo lo tumbó. Un protocolo que nunca invalida nada no está midiendo nada.

## 3.4 Lo que ya se encontró

### 3.4.1
El banco de pruebas de la tesis, medido con su propio termómetro. La primera versión casi no premiaba adaptarse: uno coma siete por ciento. Un termómetro roto, y era el mío. La segunda llegó a treinta y uno coma ocho, sobre un umbral fijado antes. Y una política desplegable ya alcanza nueve y medio.

### 3.4.2
En la compuerta G2b, QMIX le gana a la mejor estática en las tres semillas, entre nueve y medio y dieciséis por ciento, y llega al ochenta y cinco por ciento del oráculo. Un resultado modesto, porque el entorno es pequeño, y honesto, porque el instrumento estaba certificado antes.

### 3.4.3
Las compuertas funcionan como esclusas. La primera documentó el entorno que no servía; la segunda aprobó el instrumento; las dos siguientes, el aprendizaje. La prueba a escala completa está desbloqueada, pero todavía no se ha corrido. Se dibuja a trazos a propósito.

### 3.4.4
Lo que viene es llevar el marco a un simulador con órbitas reales y preguntar si el margen sobrevive al realismo; si no sobrevive, también es un resultado. Y el reloj corre: el estándar 6G se congela, potencialmente, a inicios de dos mil veintinueve. No se trata de demostrar que la inteligencia gana, sino de que la medición signifique algo.
