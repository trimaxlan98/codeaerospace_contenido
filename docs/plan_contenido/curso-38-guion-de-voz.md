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
