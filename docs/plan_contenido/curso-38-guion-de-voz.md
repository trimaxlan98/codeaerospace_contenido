# Curso 38 — Guion de voz (96 clips)

La narración se escribe aquí, a mano, y `voz_curso.py` + `guiones.py --solo-audio --proveedor edge` la sintetizan (voz es-MX-JorgeNeural, como los cursos 36 y 37). Presupuesto: **2.2 palabras por segundo de clip, con 10 % de margen** (un clip de 30 s admite ~57 palabras). Cada bloque `### N.M.K` es el `.txt` de ese clip, tal cual, y se escribe DESPUÉS de revisar los fotogramas del clip: la voz dice lo que se ve, en el orden en que aparece.

Registro: público general de YouTube con curiosidad técnica. Los números se dicen como aparecen en pantalla; lo medido se dice como medida y lo que es norma o parámetro, como dato. Sin marcas comerciales salvo «RTL-SDR» (nombre del proyecto).

## 1.1 De la antena al número

### 1.1.1
Así es por dentro una radio definida por software. La señal entra por la antena, pasa por un amplificador de bajo ruido y por un mezclador que la baja de frecuencia; luego un filtro y el conversor analógico digital. A la derecha del conversor ya no hay circuitos: solo números. Y cuesta unos treinta dólares.

### 1.1.2
Esta es la banda de FM comercial, de ochenta y ocho a ciento ocho megahercios. El receptor no la ve entera: ve una ventana de dos punto cuatro megahercios, tan ancha como su frecuencia de muestreo. Al mover el oscilador local, la ventana se desliza. Aquí caben cinco emisoras a la vez.

### 1.1.3
El conversor convierte la onda en escalones. Con cuatro bits hay dieciséis niveles y el error, en rojo, es enorme. Con ocho bits hay doscientos cincuenta y seis, y el error casi desaparece. Lo medimos: cuarenta y nueve punto nueve decibelios entre la señal y el ruido de cuantización. Cada bit extra suma unos seis.

### 1.1.4
Hagamos la cuenta. Dos punto cuatro millones de muestras por segundo, por dos, I y Q, por ocho bits: treinta y ocho punto cuatro megabits por segundo salen por el USB. El audio que escuchamos al final necesita cincuenta veces menos. Todo lo que hay en medio es aritmética.

## 1.2 Mezclar es multiplicar

### 1.2.1
Mezclar dos señales es multiplicarlas. Una emisora en cien punto tres megahercios por un oscilador en ochenta y nueve punto seis. El producto contiene dos frecuencias nuevas: la suma, ciento ochenta y nueve punto nueve, y la diferencia, diez punto siete. Esa diferencia es la frecuencia intermedia clásica de los receptores de FM.

### 1.2.2
Pero hay un problema: una emisora en setenta y ocho punto nueve también cae en diez punto siete. Es la frecuencia imagen: está a la misma distancia, del otro lado del oscilador. Un mezclador de una sola rama no puede distinguirlas, y la imagen llega con toda su fuerza.

### 1.2.3
Con un oscilador complejo, un fasor que gira, la multiplicación no crea copias: desliza el espectro entero. Tomamos la captura en banda base y la corremos setecientos kilohercios. La emisora más fuerte, que estaba a la izquierda, queda justo en cero. Las demás se mueven con ella.

### 1.2.4
Por eso los receptores usan dos ramas, I y Q. Con un mezclador real, la emisora deseada y su imagen aparecen en los dos lados del cero, encimadas. Con I y Q, cada una cae de su lado: la deseada en más diez punto siete y la imagen en menos diez punto siete. Ya se pueden separar.

## 1.3 Las cicatrices del cero-IF

### 1.3.1
El receptor barato convierte directo a cero hercios, y eso deja cicatrices. La primera: un pico justo en el centro que no es ninguna emisora. Es la fuga del oscilador local, a doce decibelios por debajo de la señal. Un filtro que quita la componente continua lo hunde hasta setenta y tres punto ocho decibelios por debajo.

### 1.3.2
La segunda cicatriz: I y Q no son idénticas. Aquí, cinco por ciento de diferencia de ganancia y tres grados de fase. El círculo se vuelve elipse, aquí exagerada, y en el espectro aparece un espejo del tono. El rechazo de imagen queda en veintiocho punto nueve decibelios.

### 1.3.3
Se corrige sin saber nada de la señal, solo con sus estadísticas: se le quita a Q lo que se parece a I y se iguala su potencia. La elipse vuelve a ser círculo y la imagen se hunde bajo el ruido. El rechazo pasa de veintinueve a más de ochenta decibelios.

### 1.3.4
Y un truco para no pelear con el pico del centro: sintonizar un poco al lado. Corremos el oscilador doscientos cincuenta kilohercios, y la emisora queda lejos del pico. Después, un oscilador numérico la trae a cero en software. El hardware barato deja cicatrices; el software las cura.

## 2.1 El piso de ruido

### 2.1.1
Todo receptor tiene un piso de ruido que no se puede evitar: el ruido térmico. A temperatura ambiente son menos ciento setenta y cuatro dBm en cada hercio. Cuanto más ancha la ventana, más ruido entra: en dos kilohercios, menos ciento cuarenta y uno; en dos punto cuatro megahercios, menos ciento diez.

### 2.1.2
Cada eslabón de la cadena añade su propio ruido, y la fórmula de Friis dice que el primero manda. Con el amplificador primero, la cadena suma uno punto cero cuatro decibelios de figura de ruido. Si el cable va antes, tres punto nueve. Sin amplificador, nueve decibelios.

### 2.1.3
La sensibilidad se construye como una escalera: el piso de ruido del ancho de banda, más la figura de ruido, más la relación señal a ruido que necesita el demodulador. Para FM, con doscientos kilohercios, la señal más débil que se entiende es de menos ciento siete punto nueve dBm. Para una baliza estrecha, menos ciento treinta y tres punto nueve.

### 2.1.4
La misma señal débil, de menos ciento veinticinco dBm, con el amplificador en dos lugares. Puesto en la antena, la relación señal a ruido es de catorce punto nueve decibelios. Puesto en el escritorio, después del cable, baja a doce. Tres decibelios perdidos solo por el orden.

## 2.2 La ganancia justa

### 2.2.1
Ahora la ganancia. Si es poca, la señal llega al conversor tan débil que apenas usa dos de sus doscientos cincuenta y seis niveles. La onda real, en ámbar, se convierte en un escalón grueso. La relación señal a ruido y distorsión cae a seis punto tres decibelios, aunque la señal entrara con treinta.

### 2.2.2
Si la ganancia es demasiada, la onda choca con el techo del conversor y se recorta. El recorte siembra señales falsas por todo el espectro: el espurio más fuerte queda a solo doce punto nueve decibelios del tono. Son emisoras fantasma que el propio receptor inventa.

### 2.2.3
Barriendo la ganancia medimos la curva completa. Sube mientras el ruido de cuantización pierde peso, se aplana, y cae de golpe cuando empieza el recorte. El tramo bueno va de cuarenta y ocho a sesenta decibelios de ganancia, con treinta punto tres de máximo.

### 2.2.4
La señal real no se queda quieta: se desvanece. Aquí la entrada varía treinta punto siete decibelios. Un control automático de ganancia mide la salida y corrige: la salida queda en una franja de tres decibelios. Ni tanta ganancia que recorte, ni tan poca que se hunda.

## 2.3 Señales que saturan

### 2.3.1
Dos emisoras fuertes, en noventa y ocho punto uno y noventa y ocho punto cinco, entran a un amplificador que no es perfectamente lineal. A la salida aparecen dos señales que nadie transmitió, en noventa y siete punto siete y noventa y ocho punto nueve. Son productos de intermodulación, y crecen más rápido que las emisoras.

### 2.3.2
Medimos cuánto crecen. Por cada decibelio que sube la entrada, la emisora sube uno y el producto de intermodulación sube tres. Las dos rectas se cruzan en un punto teórico, el de intersección de tercer orden: aquí, once punto dos decibelios. Cuanto más alto ese punto, más aguanta el receptor.

### 2.3.3
El caso real: una emisora de FM potente y un satélite débil en ciento treinta y siete punto uno megahercios, lejos en frecuencia. Cuando la emisora satura el amplificador, le roba ganancia a todo lo demás. El satélite baja once punto dos decibelios, aunque la emisora ni siquiera esté cerca de su canal.

### 2.3.4
La solución es un filtro antes del amplificador que rechace la banda de FM. Con cuarenta decibelios de rechazo, la emisora llega convertida en casi nada y el satélite recupera toda su ganancia: cero decibelios de pérdida. Lo fuerte también estorba; por eso se filtra antes de amplificar.

## 3.1 Sintonizar en software

### 3.1.1
El oscilador numérico es un contador de fase. En cada muestra le suma un paso fijo, que depende de la frecuencia que queremos, y da la vuelta al completar el círculo. De esa aguja salen dos columnas de números: el coseno, I, y el seno, Q. Eso es todo un oscilador en software.

### 3.1.2
Multiplicamos la captura entera por ese fasor. El espectro se desliza sin deformarse: la emisora más fuerte, que estaba en menos setecientos kilohercios, queda exactamente en cero. Sintonizar ya no es mover un circuito: es elegir el paso del contador.

### 3.1.3
Y como es solo aritmética, se puede hacer varias veces sobre la misma captura. Tres osciladores, tres desplazamientos: menos setecientos, más cien y más mil cien kilohercios. Cada copia pone su emisora en cero, con su propio filtro de canal. Tres receptores en uno.

### 3.1.4
Un detalle que muerde: si el contador se reinicia en cada bloque de muestras, la fase salta en cada frontera. En el espectro aparecen rayas falsas cada doscientos cuarenta hercios, a solo nueve punto cinco decibelios de la portadora. Con la fase continua, desaparecen.

## 3.2 Filtrar y diezmar

### 3.2.1
Con la emisora ya en cero, falta aislarla. Un filtro de doscientos diecinueve coeficientes deja pasar el canal y hunde todo lo demás cincuenta y nueve punto tres decibelios. Las otras cuatro emisoras siguen en la captura, pero ya no molestan.

### 3.2.2
¿Para qué filtrar, si al final nos quedamos con menos muestras? Porque diezmar sin filtro pliega el espectro. Una emisora vecina, en quinientos kilohercios, cae dentro del canal, igual de fuerte que la nuestra. Con el filtro antes, queda más de sesenta decibelios por debajo.

### 3.2.3
Filtrar cuesta multiplicaciones. Un solo filtro que diezma por diez necesita cincuenta y dos punto seis millones por segundo. Partido en dos etapas, una ancha y barata y otra estrecha a menor tasa, bastan veintinueve punto cinco millones. Casi la mitad.

### 3.2.4
Así se baja por la escalera: de dos punto cuatro millones de muestras por segundo a doscientas cuarenta mil para el canal, y a cuarenta y ocho mil para el audio. Cincuenta veces menos datos. Primero se recorta, después se tira lo que sobra.

## 3.3 El reloj que miente

### 3.3.1
El reloj del receptor no es perfecto. Un cristal barato puede equivocarse veinticinco partes por millón: a cien megahercios son dos punto cinco kilohercios de error; a mil noventa, más de veintisiete. Con un oscilador compensado de una parte por millón, el error casi desaparece.

### 3.3.2
¿Cómo se mide? Con una señal de frecuencia conocida. Esperábamos la referencia justo en cincuenta kilohercios y aparece tres mil ochocientos noventa y ocho hercios más arriba. Dividido entre su frecuencia, el error del cristal: veintisiete partes por millón.

### 3.3.3
Y el error no se queda quieto. Al calentarse, el cristal deriva, y en el waterfall la señal se inclina con los minutos. A cuatrocientos treinta y siete megahercios medimos novecientos veintiséis hercios de deriva en diez minutos.

### 3.3.4
La corrección es otra vez un oscilador numérico que resta, fila a fila, el error medido. La traza se endereza y queda un residuo de dos punto cuatro hercios. El cristal miente un poco; una señal conocida lo delata.

## 4.1 El discriminador

### 4.1.1
En FM, el mensaje no cambia la amplitud: cambia la velocidad a la que gira el fasor. Cuando el mensaje sube, el fasor acelera; cuando baja, frena. Aquí lo mostramos a escala ilustrativa, mucho más lento que en una emisora real. La frecuencia instantánea es la velocidad de ese giro.

### 4.1.2
Para recuperar el mensaje basta comparar dos muestras seguidas. El ángulo entre una muestra y la anterior dice cuánto giró el fasor; multiplicado por la frecuencia de muestreo, es la frecuencia instantánea. La curva recuperada, en verde, cae exactamente sobre el mensaje original.

### 4.1.3
¿Cuánto ancho ocupa una FM? Con setenta y cinco kilohercios de desviación y un tono de quince, la regla de Carson dice ciento ochenta kilohercios. Medimos el ancho que contiene el noventa y ocho por ciento de la potencia: ciento ochenta punto cero. Con estéreo, la regla sube a doscientos cincuenta y seis.

### 4.1.4
Una rareza de la FM: el ruido a la salida del discriminador crece con la frecuencia, y los agudos llegan más sucios. Por eso la emisora refuerza los agudos y el receptor los atenúa con un filtro de setenta y cinco microsegundos. El ruido de audio baja doce punto dos decibelios.

## 4.2 El múltiplex estéreo

### 4.2.1
Lo que sale del discriminador de una emisora de FM no es solo audio: es una señal múltiplex. De cero a quince kilohercios va la suma de los dos canales, lo que oye un radio mono. En diecinueve, un tono piloto. Entre veintitrés y cincuenta y tres, la diferencia entre izquierda y derecha. Y en cincuenta y siete, los datos.

### 4.2.2
El piloto es la clave. Un lazo de enganche de fase se sincroniza con él, y el error de fase cae por debajo de una centésima de radián. Al duplicar su fase sale la subportadora de treinta y ocho kilohercios, justo la que hace falta para bajar la diferencia a la banda de audio.

### 4.2.3
Con la suma y la diferencia, la matriz es aritmética: izquierda es suma más diferencia; derecha, suma menos diferencia. El tono de un kilohercio queda solo en el canal izquierdo y el de tres en el derecho, separados cincuenta y nueve punto tres decibelios. Con cinco grados de error de fase, aún quedan cuarenta y ocho.

### 4.2.4
Pero el estéreo tiene un precio. El ruido de la FM crece con la frecuencia, y la diferencia viaja justamente arriba, entre veintitrés y cincuenta y tres kilohercios. Ahí el ruido es quince punto cuatro decibelios mayor que en la banda mono. Por eso una emisora débil se oye mejor en mono.

## 4.3 RDS: el texto escondido

### 4.3.1
La emisora esconde datos en cincuenta y siete kilohercios, justo tres veces el piloto. Así el receptor no necesita otro oscilador: le basta multiplicar por tres la fase del piloto que ya tiene enganchado. Por ahí viajan mil ciento ochenta y siete punto cinco bits por segundo.

### 4.3.2
Cada bit se codifica como un salto de fase: la subportadora da media vuelta, ciento ochenta grados. Con la portadora recuperada del piloto, el receptor ve esos saltos y lee los unos y los ceros. Cada bit ocupa ciento noventa y dos muestras.

### 4.3.3
Los bits vienen en bloques de veintiséis: dieciséis de datos y diez de comprobación. Con esos diez, el receptor calcula un síndrome; si coincide con una de cuatro palabras conocidas, el bloque está sano y además sabe qué bloque es. Basta un bit volteado para que no coincida con ninguna.

### 4.3.4
Cuatro grupos, cada uno con un bloque que trae dos letras: C y O, luego D y E, un espacio y F, y M con otro espacio. Se arma el nombre de la emisora, ficticia en este ejemplo: CODE FM, sin un solo bit errado. Y aun con doce bits errados por el ruido, las repeticiones devuelven el mismo nombre.

## 5.1 La constelación que gira

### 5.1.1
Una señal QPSK debería dar cuatro puntos. Pero el reloj del transmisor y el del receptor nunca coinciden del todo, y esa pequeña diferencia de frecuencia hace que cada símbolo llegue girado un poco más que el anterior: aquí, uno punto tres grados. Símbolo a símbolo, los cuatro puntos se estiran en un anillo.

### 5.1.2
El truco es elevar cada muestra a la cuarta potencia. Los cuatro puntos de la QPSK, a cuarenta y cinco, ciento treinta y cinco, doscientos veinticinco y trescientos quince grados, caen en el mismo sitio. La modulación desaparece, y en el espectro queda una sola raya: en cuatro veces el giro.

### 5.1.3
Basta medir dónde está esa raya y dividir entre cuatro. La estimación da uno punto tres tres dos grados por símbolo, con un error de tres décimas por millón de la tasa de símbolos. Sin saber nada de los datos, el receptor ya conoce su propio error.

### 5.1.4
Se corrige girando cada símbolo en sentido contrario, y el anillo vuelve a ser cuatro racimos. Pero fíjate: quedan girados un ángulo fijo. La frecuencia ya está; la fase todavía no. De eso se encarga el siguiente lazo.

## 5.2 El lazo de Costas

### 5.2.1
Para la fase se usa un detector muy simple. En BPSK los símbolos deberían estar sobre el eje I. Si llegan girados, aparece una componente Q, y el producto de I por Q dice cuánto y hacia qué lado: positivo si giró hacia un lado, negativo hacia el otro, cero cuando está en su sitio.

### 5.2.2
Ese error alimenta un oscilador numérico que corrige la fase poco a poco. La fase del oscilador, en fucsia, persigue a la real hasta pegarse a ella, y el anillo de la constelación se convierte en dos puntos. Con este ancho de lazo, engancha en unos ciento trece símbolos.

### 5.2.3
El ancho del lazo es un compromiso. Un lazo estrecho tarda en engancharse, unos novecientos símbolos, pero luego apenas tiembla: un grado y medio. Uno ancho engancha en treinta símbolos, pero tiembla más de cinco grados. No hay un ajuste gratis: se elige según la señal.

### 5.2.4
Y hay una trampa. El detector no distingue un giro de cero grados de uno de ciento ochenta, así que si la fase arranca lejos, el lazo engancha al revés y todos los bits salen negados. La solución es codificar la diferencia entre bits: aunque todo llegue invertido, las diferencias no cambian, y los datos salen limpios.

## 5.3 El reloj de símbolo

### 5.3.1
Queda un tercer reloj: el de los símbolos. El diagrama de ojo muestra cuándo conviene muestrear, justo en el centro, donde el ojo está más abierto. Si muestreamos a destiempo, los errores se disparan: con tres décimas de símbolo de retraso, cuarenta y seis veces más errores que en el centro.

### 5.3.2
El detector de Gardner mide ese desfase con tres muestras: la anterior, la del medio y la actual. Si muestreamos a tiempo, el error es casi cero; si vamos retrasados, sale positivo. Su curva cruza el cero en el centro del símbolo, que es un punto estable, y otra vez en los bordes, que son inestables.

### 5.3.3
Con ese error, un lazo ajusta el instante de muestreo. Arranca con treinta y siete centésimas de símbolo de desfase y en unos cien símbolos se asienta cerca de cero. Medido en la ventana final, queda un residuo de una centésima, con dos de temblor.

### 5.3.4
Se nota en la constelación. Con el reloj desfasado, la nube es ancha: un error de treinta y cinco por ciento. Cuando el lazo converge, se aprieta en dos puntos: seis punto cuatro por ciento. Tres relojes que ajustar antes de leer un bit: frecuencia, fase y símbolo.

## 6.1 ADS-B: aviones

### 6.1.1
Cada avión comercial transmite su identidad en mil noventa megahercios. La señal es una ráfaga de pulsos: un bit por microsegundo, codificado por la posición del pulso. Alto y luego bajo es un uno; bajo y luego alto, un cero. Un receptor de treinta dólares los ve sin esfuerzo.

### 6.1.2
Primero hay que encontrar dónde empieza el mensaje, correlacionando la captura con el preámbulo, un patrón fijo de cuatro pulsos. El pico más alto no siempre es el bueno: aquí, un trozo de datos se parecía al preámbulo. La comprobación lo rechaza, y acepta el verdadero.

### 6.1.3
El mensaje tiene ciento doce bits, por campos: el tipo, la dirección única del avión, cincuenta y seis bits de datos y veinticuatro de comprobación. El receptor recalcula esos veinticuatro con el resto del mensaje: si coinciden, el mensaje llegó sin errores.

### 6.1.4
Y aparece el avión: su dirección única y su indicativo, CODE uno cero uno. Es un avión ficticio, pero el mismo decodificador lee un mensaje real: el vuelo KLM mil veintitrés. Cada avión dice quién es un par de veces por segundo.

## 6.3 LoRa: chirps

### 6.3.1
LoRa usa otro truco: cada símbolo es un chirp, una señal cuya frecuencia sube por todo el canal de ciento veinticinco kilohercios y da la vuelta. El dato no está en la forma, sino en dónde empieza la subida. Aquí, los símbolos cero, cuarenta, noventa y diecisiete; cada uno dura un milisegundo.

### 6.3.2
Para leerlo, el receptor multiplica por un chirp que baja. Las dos rampas se cancelan y queda un tono puro, de frecuencia constante. Su transformada de Fourier tiene un solo pico, justo en el símbolo transmitido: noventa.

### 6.3.3
El factor de dispersión decide cuánto dura cada chirp. Con factor doce, el chirp es treinta y dos veces más largo que con factor siete: casi treinta y tres milisegundos por símbolo. Se transmite más lento, pero cada símbolo acumula mucha más energía.

### 6.3.4
Esa energía permite algo sorprendente. Aquí el chirp está veinte decibelios por debajo del ruido: la señal no se ve. Pero tras quitar el chirp, la transformada muestra un pico claro en el símbolo correcto. En simulación ideal, el factor doce aguanta hasta menos veintitrés decibelios.

## 6.2 AIS: barcos

### 6.2.1
Los barcos también se anuncian: el sistema AIS transmite en dos canales cerca de ciento sesenta y dos megahercios, a nueve mil seiscientos bits por segundo. Usa GMSK: la frecuencia cambia con cada bit, pero suavizada por un filtro gaussiano, así la fase sube y baja sin saltos.

### 6.2.2
Los bits no van tal cual. Con la regla NRZI, un cero cambia el nivel y un uno lo mantiene. Así, al receptor no le importa si la señal llegó invertida: solo mira dónde hay cambios.

### 6.2.3
El mensaje va entre dos banderas: cero, seis unos, cero. Para que esa secuencia nunca aparezca dentro de los datos, tras cinco unos seguidos el transmisor mete un cero de relleno, que el receptor quita. En esta trama de doscientos treinta y tres bits hizo falta uno.

### 6.2.4
Con la comprobación correcta, sale el barco: su identificación, su posición, diecinueve grados norte y noventa y nueve oeste, doce punto tres nudos y rumbo de ochenta y siete grados. Es un barco ficticio, pero así se anuncian todos.

## 7.2 Meteor: del QPSK a la imagen

### 7.2.1
Los satélites meteorológicos NOAA de señal analógica se apagaron en dos mil veinticinco, pero Meteor sigue transmitiendo imágenes en ciento treinta y siete punto nueve megahercios. Es QPSK a setenta y dos mil símbolos por segundo. Tras los lazos de frecuencia, fase y reloj, la constelación queda así: cuatro nubes con mucho ruido.

### 7.2.2
Primero hay que resolver la ambigüedad: el lazo de fase puede quedar girado noventa, ciento ochenta o doscientos setenta grados. Por eso el satélite repite una palabra de sincronía de treinta y dos bits. Se prueba en las cuatro rotaciones y solo una correlaciona fuerte: aquí, noventa grados.

### 7.2.3
Con tanto ruido, el cinco punto seis por ciento de los bits llegan mal: mil trescientos ochenta errores. Pero el satélite los envió con un código convolucional, y el decodificador de Viterbi busca la secuencia más probable. A la salida: cero errores.

### 7.2.4
Y con los bits limpios, la imagen se arma línea a línea. Es una imagen sintética, pero la cadena es la misma. Sin el código, quinientos cincuenta y un píxeles saldrían dañados; con él, ninguno. Una imagen del planeta, desde un aparato de treinta dólares.

## 7.3 GPS bajo el ruido

### 7.3.1
La señal del GPS llega al suelo casi veinte decibelios por debajo del ruido. En la captura solo se ve ruido, y en el espectro, un piso plano: la señal está ahí, pero diez veces más pequeña en amplitud que el ruido que la cubre.

### 7.3.2
La clave es el código. Cada satélite repite su propia secuencia de mil veintitrés chips cada milisegundo. Correlacionada consigo misma da un pico de mil veintitrés, y desplazada solo toma tres valores pequeños. Esa suma coherente aporta treinta decibelios de ganancia.

### 7.3.3
Pero el receptor no sabe ni el Doppler ni en qué punto del código está. Así que prueba todo: veintiún valores de Doppler por dos mil cuarenta y seis posiciones del código, más de cuarenta y dos mil celdas, sumando diez milisegundos. La rejilla se barre fila a fila.

### 7.3.4
Y en una sola celda aparece el pico: dos punto cinco kilohercios de Doppler y cuatrocientos veintitrés chips de retardo, doce punto seis decibelios sobre la media. Con el código de otro satélite, nada: cuatro punto cinco. Veinte decibelios bajo el ruido, y aun así se encuentra.

## 7.1 El Doppler de un pase

### 7.1.1
Un satélite en órbita baja pasa sobre nosotros en unos doce minutos, y su frecuencia no se queda quieta. Mientras se acerca llega más alta; al alejarse, más baja. A cuatrocientos treinta y siete megahercios, el corrimiento va de más diez a menos diez kilohercios, y cruza por cero justo en el cenit.

### 7.1.2
Si no hacemos nada, la señal recorre el waterfall más de veinte kilohercios. Pero la órbita se conoce de antemano, así que un oscilador numérico sigue la curva predicha y la resta. La señal queda quieta en el centro, con un error de apenas tres hercios.

### 7.1.3
Lo difícil es el cenit. Ahí la frecuencia cambia más rápido: ciento veintitrés hercios por segundo. En ese momento, cualquier error en la predicción se paga caro.

### 7.1.4
Si el reloj del receptor va dos segundos adelantado, la curva predicha y la medida casi coinciden. El residuo es pequeño en los extremos y crece en el cenit, hasta doscientos cuarenta y seis hercios: dos segundos por ciento veintitrés hercios por segundo. El satélite cambia de frecuencia, y el receptor lo persigue.

## 8.3 La estación completa

### 8.3.1
La cadena del principio, ahora con cada cifra que medimos. La antena gana tres decibelios; el amplificador en la antena deja la figura de ruido en uno punto cero cuatro; la corrección de I y Q, más de ochenta decibelios de rechazo; el filtro de canal, cincuenta y nueve; ocho bits, cuarenta y nueve punto nueve; treinta y ocho megabits por el USB. Y al final, Viterbi: cero errores.

### 8.3.2
¿Alcanza la señal? El satélite transmite cinco vatios, treinta y siete dBm. A mil ochocientos kilómetros, el espacio se come ciento cuarenta decibelios, y llegan menos ciento tres punto cinco dBm. El piso de ruido está en menos ciento veinticuatro. La diferencia, veinte punto nueve decibelios; la cadena necesita cuatro. Sobran casi diecisiete de margen.

### 8.3.3
El pase de Meteor dura unos quince minutos y medio sobre el horizonte. En ese tiempo el Doppler recorre tres kilohercios arriba y tres abajo, y el receptor lo persigue como vimos. Antes y después, el satélite está bajo el horizonte y no hay nada que recibir.

### 8.3.4
Y al final del pase, la imagen. Sintética en este ejemplo, pero con la misma cadena que recibiría una real: sin un solo error. Desde la antena hasta el último píxel, todo fue aritmética. Una radio es aritmética; ahora sabes leerla.
