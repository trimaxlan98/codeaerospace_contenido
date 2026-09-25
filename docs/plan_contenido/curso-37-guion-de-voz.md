# Curso 37 — Guion de voz (84 clips)

La narración se escribe aquí, a mano, y `guiones.py --solo-audio --proveedor edge` la sintetiza desde los `.txt` (voz es-MX-JorgeNeural, como el curso 36). Presupuesto: **2.2 palabras por segundo de clip, con 10 % de margen** (un clip de 30 s admite ~60 palabras). Cada bloque `### N.M.K` es el `.txt` de ese clip, tal cual.

Registro: **público general de YouTube**. Se habla de «la tienda», nunca de un curso, una sesión, una demo o un script. Los números se dicen redondos cuando la pantalla ya los muestra exactos («unas veintidós mil páginas»), y exactos solo cuando son el punto. Lo que midió el motor se dice como medición («SQL Server midió...», «el motor leyó...»); lo que calculamos, como cálculo.

## 1.1 La página: lo que cuesta leer

### 1.1.1
Una tienda en línea: doscientos mil clientes, un millón y medio de pedidos y casi cuatro millones de renglones de detalle. Queremos los pedidos de un cliente. ¿Cuánto cuesta esa consulta? El tiempo engaña: cambia en cada ejecución y en cada máquina. Lo que no cambia es cuántas páginas leyó el motor.

### 1.1.2
SQL Server no guarda filas sueltas: las guarda en páginas de ocho kilobytes. En cada página de pedidos caben unas sesenta y siete filas. La tabla completa ocupa más de veintidós mil páginas. Cada vez que una consulta necesita un dato, abre la página entera. Esa es la unidad con la que se paga todo lo que sigue.

### 1.1.3
Buscar un pedido por su número es barato. Las páginas forman un árbol: el motor abre la raíz, baja a un nivel intermedio y llega a la hoja donde está el pedido. Tres páginas, tres lecturas. Y con tres niveles alcanza para el millón y medio de pedidos de la tienda.

### 1.1.4
Ahora busquemos por cliente, una columna sin índice. El motor no sabe dónde están sus pedidos, así que abre la tabla entera: más de veintidós mil lecturas. Solo le servían ciento noventa y una filas, que cabrían en tres páginas. Más de cien páginas por cada fila útil. Esa diferencia es lo que vamos a aprender a eliminar.

## 1.2 Lo que pasa al ejecutar

### 1.2.1
Una consulta llega como texto. SQL Server la analiza, comprueba que las tablas y columnas existen, la optimiza y solo entonces la ejecuta. Lo que sale del optimizador ya no es texto: es un plan, una lista de operadores que se leen de derecha a izquierda. El plan decide cuánto se va a leer.

### 1.2.2
Para una misma consulta hay muchos planes posibles. El optimizador estima el costo de cada uno y se queda con el más barato. Para buscar los pedidos de un cliente puede recorrer la tabla entera o usar un índice y volver por cada fila. Aquí gana el índice: seiscientas lecturas contra veintidós mil.

### 1.2.3
Compilar un plan cuesta, así que el motor lo guarda. La primera ejecución compila; las siguientes reutilizan el plan guardado y arrancan de inmediato. Pero ojo: si llega otro valor, por ejemplo otro cliente, también recibe el mismo plan, aunque no le convenga. Volveremos a esto más adelante.

### 1.2.4
El optimizador decide con estimaciones. Para los pedidos pendientes, estima bien: el punto estimado y el real caen dentro de la misma franja. Pero si le escondemos el valor en una variable, cree que llegarán ocho filas y llegan casi ciento cincuenta mil. Una diferencia de más de diez veces es la primera pista de un mal plan.

## 1.3 Leer un plan

### 1.3.1
Un plan se lee de derecha a izquierda. A la derecha, el operador que toca los datos; a la izquierda, el que entrega el resultado. El grosor de cada flecha es la cantidad de filas: millón y medio salen del scan y solo ciento noventa y una pasan el filtro.

### 1.3.2
Tres operadores de acceso aparecen una y otra vez. El scan lee todas las páginas. El seek baja por el árbol del índice y abre tres. El lookup hace un seek y luego vuelve a la tabla por el resto de las columnas, una vez por cada fila encontrada.

### 1.3.3
Para unir dos tablas hay tres métodos. Nested loops recorre una tabla y, por cada fila, busca en la otra: ideal si hay pocas. Merge avanza por dos listas ya ordenadas al mismo tiempo. Hash reparte una tabla en cubetas y luego busca en ellas la otra, útil cuando las dos son grandes.

### 1.3.4
Cuando la tabla es grande, el motor reparte el trabajo. El scan se divide entre ocho hilos que leen a la vez, y un coordinador junta lo que encuentran. Por eso el motor informa nueve recorridos: ocho hilos más uno. Se leyó millón y medio de filas para entregar ciento noventa y una.

## 2.1 El árbol B

### 2.1.1
Buscar en una lista desordenada obliga a revisar carta por carta hasta dar con la que queremos. Si la lista está ordenada y tiene un índice, como el de un libro, podemos saltar directo al lugar correcto. Un índice de base de datos es exactamente eso: un orden.

### 2.1.2
Ese orden se guarda en un árbol. Cada página intermedia tiene cientos de entradas que apuntan a páginas de abajo: unas seiscientas veinte. Con tantas ramas por nivel basta bajar tres niveles, de la raíz a la hoja, para encontrar cualquier pedido entre un millón y medio. Tres lecturas.

### 2.1.3
Y el árbol crece muy despacio. Con un millón y medio de filas tiene tres niveles. Para necesitar un cuarto nivel habría que pasar de decenas de millones de filas, y con cuatro caben más de dieciséis mil millones. Multiplicar los datos por mil cuesta, a lo sumo, una página más.

### 2.1.4
Pongamos las dos búsquedas lado a lado. Con el índice, tres lecturas. Sin índice, más de veintidós mil. La escala es logarítmica: en realidad la diferencia es de más de siete mil veces. Un índice es un orden, y el orden ahorra lecturas.

## 2.2 El viaje de vuelta: lookup

### 2.2.1
Creemos un índice sobre la columna del cliente. Ese índice es delgado: en cada hoja guarda solo el número de cliente y la llave del pedido. Todo lo demás, la fecha, el estatus, el total, sigue en la tabla. Para devolverlo, el motor tendrá que ir a buscarlo.

### 2.2.2
Para el cliente quinientos uno el índice encuentra ciento noventa y una filas. Por cada una, el motor vuelve a la tabla y baja tres niveles del árbol: tres lecturas por fila. El modelo da quinientas setenta y seis; SQL Server midió quinientas noventa y siete. Casi lo mismo.

### 2.2.3
Ahora el mayorista, el cliente uno, con casi ciento cincuenta mil pedidos. Tres lecturas por fila serían unas cuatrocientas cincuenta mil. Leer la tabla completa cuesta veintidós mil. El optimizador lo sabe y elige el scan: veinte veces menos lecturas.

### 2.2.4
El cruce entre los dos caminos es el punto de inflexión: unas siete mil cuatrocientas filas, apenas medio por ciento de la tabla. Por debajo, el lookup gana; por encima, conviene leerlo todo. Un lookup es barato; ciento cincuenta mil lookups, no.

## 2.3 El índice que cubre

### 2.3.1
¿Y si el índice ya tuviera lo que la consulta pide? Con INCLUDE, la fecha, el estatus y el total bajan a la hoja del índice. La llave sigue siendo el cliente, pero la hoja engorda. Solo los comentarios se quedan fuera.

### 2.3.2
Ahora el cliente quinientos uno se resuelve sin salir del índice: bajar tres niveles y leer una hoja. Cuatro lecturas en total, contra quinientas noventa y siete del lookup. Ciento cuarenta y nueve veces menos, sin cambiar una línea de la consulta.

### 2.3.3
Y el mayorista también gana. Sus pedidos están juntos en el índice, uno detrás de otro, en unas setecientas ochenta hojas de ciento noventa filas cada una. Setecientas ochenta y cinco lecturas en lugar de las veintidós mil del scan: veintiocho veces menos.

### 2.3.4
Pero basta pedir una columna que no está en el índice para perder todo. Un SELECT asterisco pide también los comentarios, y el motor vuelve a la tabla por cada fila: otra vez quinientas noventa y siete lecturas. Pide solo lo que usas: el índice ya lo tiene.

## 3.1 El orden de las llaves

### 3.1.1
Un índice de dos columnas se puede ordenar de dos maneras. Por fecha y luego estatus: en un mismo día se mezclan todos los estatus. O por estatus y luego fecha: todos los cancelados quedan juntos, y dentro de ellos, en orden de fecha. Mismos datos, dos órdenes distintos.

### 3.1.2
Si buscamos los pedidos entregados, casi da igual el orden: son más del noventa y uno por ciento de la tabla. El tramo que recorre cada índice es prácticamente el mismo, porque casi todo es entregado.

### 3.1.3
Con los cancelados de dos mil veinticinco la historia cambia. Ordenado por fecha, el motor recorre todo el año, más de cuatrocientos mil pedidos, para quedarse con los cancelados. Ordenado por estatus, salta directo a los treinta y tres mil cancelados de ese año. Mil novecientas lecturas contra ciento sesenta: doce veces menos.

### 3.1.4
La regla es sencilla: primero la columna que se compara por igualdad, después la que se busca por rango. El estatus fija un valor; la fecha recorre un intervalo dentro de él. El orden de las llaves importa: igualdad primero, rango después.

## 3.2 Índices que no se ven

### 3.2.1
Los pedidos pendientes son apenas dos mil setecientos, menos del dos por mil de la tabla, y todos están entre los más recientes. Pero un panel de operación los consulta todo el día. Leer la tabla entera cada vez para encontrar tan pocos es un desperdicio.

### 3.2.2
Un índice filtrado guarda solo las filas que cumplen una condición: aquí, estatus igual a pendiente. En lugar de un índice sobre todos los pedidos, queda un árbol pequeñito de catorce páginas. La consulta del panel se resuelve en trece lecturas.

### 3.2.3
Ahora el detalle de los pedidos: casi cuatro millones de renglones, más de diecisiete mil páginas, y ningún índice en la columna del pedido. Para mostrar el ticket de una sola compra, el motor recorre la tabla completa, aunque el ticket cabe en una página.

### 3.2.4
Con un índice en esa llave, el ticket cuesta tres lecturas en lugar de dieciocho mil: seis mil veces menos. Toda llave foránea que se usa para buscar pide su índice. Y para lo raro que se consulta mucho, un índice filtrado.

## 3.3 Columnas en vez de filas

### 3.3.1
Para sumar las ventas solo hacen falta dos columnas: la cantidad y el precio. Pero si la tabla se guarda por filas, cada página trae las cuatro columnas juntas y el motor tiene que abrirlas todas. Guardada por columnas, cada columna vive aparte y basta con leer dos de cuatro.

### 3.3.2
Un índice de columnas reparte la tabla en grupos de hasta un millón cuarenta y ocho mil filas. Los casi cuatro millones de renglones del detalle caben en cuatro grupos; el último, a medio llenar. Dentro de cada grupo, cada columna se guarda comprimida por separado.

### 3.3.3
Además cambia la forma de procesar. En modo fila, el motor avanza de una fila en una fila: casi cuatro millones de vueltas. En modo por lotes, procesa cerca de novecientas filas de golpe: apenas unos cuatro mil doscientos lotes para la misma tabla.

### 3.3.4
SQL Server midió la misma consulta de ventas: dieciséis mil cuatrocientas lecturas guardando por filas y seis mil quinientas por columnas, con un solo hilo. Dos veces y media menos, y con mucho menos trabajo de procesador. Para sumar millones, guarda columnas, no filas.

## 4.1 No envuelvas la columna

### 4.1.1
Ahora tenemos un índice por fecha: los pedidos ordenados en el tiempo, cada año más poblado que el anterior. Si pedimos dos mil veinticinco como un rango de fechas, el motor pone dos marcas en el índice y lee solo lo que queda entre ellas. A eso se le llama un predicado sargable.

### 4.1.2
Pero muchas veces escribimos YEAR de la fecha igual a dos mil veinticinco. Se lee más natural, y es mucho más caro: el motor tiene que calcular el año de cada entrada del índice, porque el índice está ordenado por fecha, no por año. Siete mil lecturas contra menos de dos mil con el rango.

### 4.1.3
Hay una excepción útil: convertir la fecha a DATE sí se puede buscar. El optimizador la traduce a un rango alrededor de ese día y lee diecisiete páginas. Convertirla a texto, en cambio, rompe el orden: ya no hay rango posible y el motor recorre todo el índice.

### 4.1.4
Lo mismo con la aritmética. Si sumamos treinta días a la columna, el motor calcula la suma fila por fila: siete mil lecturas. Si movemos el cálculo al otro lado y restamos treinta días a la constante, la columna queda sola y el índice se usa: doscientas veintisiete. La columna va sola; el cálculo, del otro lado.

## 4.2 El tipo equivocado

### 4.2.1
El correo de los clientes se guarda como VARCHAR, un byte por carácter, y tiene su índice ordenado. Pero la aplicación lo busca con un parámetro NVARCHAR, de dos bytes. Cuando los tipos no coinciden, gana NVARCHAR, y el motor tiene que convertir la columna, entrada por entrada. El orden del índice ya no sirve.

### 4.2.2
En el plan se ve la consecuencia. Lo que debía ser una búsqueda directa en el índice se convierte en un recorrido completo, y junto al SELECT aparece un triángulo de advertencia: CONVERT IMPLICIT, una conversión que nadie escribió pero que cuesta.

### 4.2.3
La diferencia medida es enorme. Con el tipo equivocado, novecientas sesenta lecturas. Con el tipo correcto, tres. Trescientas veinte veces menos, para exactamente la misma búsqueda y el mismo resultado.

### 4.2.4
El arreglo es una sola palabra: declarar el parámetro del procedimiento como VARCHAR, igual que la columna. La consulta vuelve a buscar en el índice y lee tres páginas. El tipo del parámetro debe ser el tipo de la columna.

## 4.3 LIKE, ISNULL y OR

### 4.3.1
Un índice sobre el apellido es una lista ordenada. Si buscamos los que empiezan con Gar, el motor sabe dónde está ese tramo: cincuenta y cinco lecturas. Si buscamos los que terminan en cía, no sabe por dónde entrar y revisa la lista completa: más de mil. Y el resultado es el mismo: unos diez mil García.

### 4.3.2
ISNULL tiene la misma trampa. Casi cuarenta mil clientes no tienen teléfono, y por eso alguien escribió ISNULL sobre la columna. Pero envolverla obliga a revisar cada fila: quinientas treinta y cinco lecturas. Comparar la columna directamente usa el índice: tres.

### 4.3.3
Hay un caso en el que el optimizador nos salva. El correo no admite nulos, así que un ISNULL sobre él no hace nada, y el motor lo quita solo antes de ejecutar. Lo que parecía un recorrido completo vuelve a ser una búsqueda de tres páginas.

### 4.3.4
Un OR entre dos columnas distintas parece imposible de buscar en un solo índice. Pero si cada columna tiene el suyo, el motor hace dos búsquedas y une los resultados: catorce lecturas en total. El motor busca rangos: dale rangos que pueda ver.

## 5.1 Lo que el optimizador sabe

### 5.1.1
Para decidir, el optimizador no lee la tabla: lee un resumen de cada columna indexada, las estadísticas. Su parte principal es un histograma de hasta doscientos pasos. Cada paso termina en un valor y cuenta cuántas filas tienen exactamente ese valor y cuántas quedan entre ese paso y el anterior.

### 5.1.2
En la columna del cliente, casi todos los pasos miden lo mismo, salvo uno: el cliente uno, el mayorista, tiene un paso para él solo. Nuestro modelo del histograma le da ciento cuarenta y nueve mil novecientas setenta filas, exactamente lo que SQL Server guarda en sus estadísticas.

### 5.1.3
El resumen incluye también la densidad: cuántos valores distintos hay. En la tienda compraron unos ciento ochenta y nueve mil clientes. Si el optimizador no sabe qué cliente le van a pedir, supone el promedio: un millón y medio entre ciento ochenta y nueve mil, unas ocho filas. Para el mayorista, eso es un error enorme.

### 5.1.4
Las estadísticas se actualizan solas cuando cambian suficientes filas. Antes el umbral era el veinte por ciento de la tabla: trescientos mil cambios. Hoy es la raíz de mil por el número de filas: menos de treinta y nueve mil, casi ocho veces antes. El optimizador no lee la tabla: lee su resumen.

## 5.2 Adivinar a ciegas

### 5.2.1
Pidamos los pedidos del cliente uno escribiendo el número directamente en la consulta. El optimizador consulta el histograma, ve que son casi ciento cincuenta mil filas y decide que conviene leer la tabla completa. SQL Server midió veintidós mil lecturas: el plan correcto.

### 5.2.2
Ahora el mismo número, guardado antes en una variable. Al compilar, el optimizador no sabe qué valor tendrá la variable, así que no puede usar el histograma: usa el promedio, unas ocho filas. Para ocho filas, lo lógico es buscar en el índice y volver a la tabla por cada una.

### 5.2.3
Pero llegan ciento cuarenta y nueve mil novecientas setenta filas. El plan pensado para ocho hace un viaje a la tabla por cada una de ellas: cuatrocientas cincuenta mil lecturas. La estimación se equivocó casi diecinueve mil veces.

### 5.2.4
Mismo resultado, dos costos: veintidós mil lecturas con el número a la vista, cuatrocientas cincuenta mil con la variable. Veinte veces más, solo porque el optimizador tuvo que adivinar. Una mala estimación es un mal plan.

## 5.3 El motor que aprende

### 5.3.1
Una variable de tabla es una tabla temporal en memoria. Aquí la llenamos con los pedidos del mayorista: casi ciento cincuenta mil. Pero durante años el optimizador asumió que una variable de tabla tiene una sola fila, y armaba el plan para esa única fila.

### 5.3.2
Las versiones recientes de SQL Server corrigen eso cambiando el orden: primero llenan la variable y después compilan la consulta, ya con el número real de filas. En esta tienda, la misma consulta pasó de uno punto ocho segundos a sesenta y siete centésimas: casi tres veces más rápida.

### 5.3.3
Las funciones escalares tenían un problema parecido. Si una consulta llama a una función para cada fila, el motor la ejecuta una y otra vez, por separado: quinientas llamadas para quinientos clientes. Con la versión anterior, esta consulta tardó diecisiete segundos y medio.

### 5.3.4
Ahora el motor puede fundir la función dentro de la consulta y resolver todo de una sola vez. El mismo reporte bajó a ochenta y cinco centésimas de segundo: veinte veces más rápido, sin cambiar una línea de código. Actualizar el motor también es optimizar.

## 6.1 El primero decide

### 6.1.1
Los procedimientos almacenados guardan su plan. La primera vez que se ejecutan, el optimizador compila un plan pensado para el valor de esa primera llamada. Desde entonces, cada llamada, con el valor que sea, recibe ese mismo plan guardado.

### 6.1.2
Si el primero en llegar es el cliente quinientos uno, con ciento noventa y una filas, el plan elegido busca en el índice y vuelve a la tabla por cada fila: quinientas noventa y siete lecturas, perfecto para él. Pero luego llega el mayorista con ese mismo plan: cuatrocientas sesenta mil lecturas.

### 6.1.3
Si vaciamos la caché y el mayorista llega primero, se guarda el plan que lee la tabla entera: veintidós mil lecturas, lo razonable para él. Y ahora el cliente quinientos uno paga exactamente lo mismo, veintidós mil lecturas, para devolver ciento noventa y una filas.

### 6.1.4
El problema no está en el código, sino en los datos: en la misma columna conviven un cliente con ciento noventa y una filas y otro con casi ciento cincuenta mil, casi ochocientas veces más. Ningún plan único sirve a los dos. El primero que llega decide por todos.

## 6.2 Remedios

### 6.2.1
El remedio más directo es no guardar el plan: con la opción RECOMPILE, la consulta se compila de nuevo en cada ejecución, con el valor real. Cada cliente recibe su plan bueno: el quinientos uno busca en el índice, el mayorista lee la tabla. El precio es compilar cada vez.

### 6.2.2
Otra opción es fijar el valor típico con OPTIMIZE FOR. El plan siempre se compila como si llegara el cliente quinientos uno. Para la mayoría de los clientes funciona, pero el mayorista queda atrapado en un plan que no es para él: setecientas setenta veces más caro.

### 6.2.3
El remedio de fondo es un índice que sirva a todos: por cliente y fecha, con las columnas que la consulta necesita incluidas. Con él, un solo plan resuelve los dos casos: seis lecturas para el cliente quinientos uno y menos de dos mil para el mayorista, en lugar de cuatrocientas sesenta mil.

### 6.2.4
Las versiones recientes traen una ayuda automática que crea variantes del plan cuando detecta datos sesgados. En esta tienda no se activó: cero variantes. Las heurísticas ayudan, pero no sustituyen un buen diseño. El mejor remedio es un índice que sirva a todos.

## 7.1 La caja negra

### 7.1.1
Los aviones llevan una caja negra; las bases de datos también. Se llama Query Store y guarda, intervalo por intervalo, cada consulta, los planes que ha usado y cuánto le costó cada uno. Cuando algo se pone lento, no hay que adivinar qué pasó: está registrado.

### 7.1.2
Con ella se ve una regresión en el momento en que ocurre. La consulta de pedidos del mayorista usaba el plan A, que lee la tabla completa: veintidós mil lecturas. Un día se compila con el plan B, pensado para clientes pequeños, y el costo salta a cuatrocientas sesenta mil. Veintiún veces más.

### 7.1.3
Como el plan bueno quedó guardado, se puede forzar sin tocar el código de la aplicación: una sola instrucción y la consulta vuelve al plan A en cada ejecución, con sus veintidós mil lecturas. El plan B sigue registrado, pero ya no se usa.

### 7.1.4
SQL Server dos mil veinticinco va más lejos: si un reporte pesado se lanza en plena hora pico, se le puede poner una marca para que falle de inmediato, con el error ocho mil setecientos setenta y ocho, mientras el resto del servidor sigue atendiendo. Lo que no se registra, no se puede arreglar.

## 6.3 Parámetros opcionales

### 6.3.1
Una pantalla de búsqueda deja filtrar por cliente, por estatus o por fecha, y cualquiera puede venir vacío. La forma cómoda de escribirlo es una consulta comodín: cada filtro dice «si el parámetro es nulo, ignóralo». Tres búsquedas muy distintas terminan en el mismo procedimiento.

### 6.3.2
Y el mismo procedimiento tiene un solo plan, que debe servir para cualquier combinación. El resultado es un plan de talla única: leer toda la tabla y revisar las tres condiciones en cada fila. Para buscar los pedidos del cliente quinientos uno, veinte mil lecturas.

### 6.3.3
SQL Server dos mil veinticinco trae una optimización para este patrón: crea dos variantes del plan según qué parámetros llegan. La búsqueda por cliente usa el índice y baja de veinte mil a seis lecturas. Las búsquedas por estatus o por fecha siguen en veinte mil, porque no tienen un índice propio.

### 6.3.4
La alternativa clásica funciona en cualquier versión: SQL dinámico parametrizado. El procedimiento arma el texto de la consulta solo con los filtros que llegaron, y cada forma de pregunta tiene su propio plan: seis lecturas para el cliente. Un plan por forma de pregunta, no uno para todas.

## 7.2 Esperar a otro

### 7.2.1
A veces una consulta no es lenta por lo que lee, sino porque espera a otra. La sesión A cambia el estatus de un pedido, pero todavía no confirma. La sesión B quiere leer ese pedido y se queda esperando hasta que A termine. El motor lo registra como una espera por bloqueo.

### 7.2.2
Con la lectura por versiones, llamada RCSI, el motor guarda aparte la versión anterior del pedido mientras A lo modifica. B lee esa versión confirmada y sigue su camino sin esperar, aunque la transacción de A siga abierta. Los lectores ya no esperan a los que escriben.

### 7.2.3
Ahora A actualiza diez mil pedidos del mayorista de un golpe. Cada fila lleva su candado, y al pasar de cinco mil en la misma tabla, el motor los cambia por uno solo sobre la tabla entera. B quiere tocar otro pedido, de otro cliente, y aun así tiene que esperar.

### 7.2.4
SQL Server dos mil veinticinco trae el bloqueo optimizado. A ya no acumula miles de candados: mantiene uno de intención sobre la tabla y uno solo por su transacción. B actualiza su pedido y pasa de inmediato. Leer no debería esperar a escribir.

## 7.3 La tienda está lenta

### 7.3.1
Cuando alguien dice «la tienda está lenta», el servidor no responde con esa frase: responde en qué está esperando, si en leer páginas, en esperar a otra sesión o en el procesador. Y Query Store, ordenando las consultas por lecturas, señala por dónde empezar.

### 7.3.2
Juntemos todo en un caso. Trescientas peticiones de la tienda, de cuatro tipos: iniciar sesión, ver mis pedidos, abrir un ticket y, de vez en cuando, el reporte mensual de ventas. Sin ningún índice, esa carga tardó cincuenta y tres segundos.

### 7.3.3
Cuatro arreglos, uno por cada tipo, y todos ya los vimos. Un índice en la llave del detalle para el ticket. Un índice que cubre para mis pedidos. El tipo correcto del parámetro para el login. Y un rango de fechas en lugar de YEAR para el reporte.

### 7.3.4
La misma carga, después de los cuatro arreglos: tres punto nueve segundos. Más de trece veces más rápida, sin cambiar un solo servidor. Medir, leer el plan y leer menos: eso es optimizar. Gracias por acompañarnos.
