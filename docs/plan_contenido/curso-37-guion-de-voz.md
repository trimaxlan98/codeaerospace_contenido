# Curso 37 — Guion de voz (84 clips)

La narración se escribe aquí, a mano, y `guiones.py --solo-audio --proveedor edge` la sintetiza desde los `.txt` (voz es-MX-JorgeNeural, como el curso 36). Presupuesto: **2.2 palabras por segundo de clip, con 10 % de margen** (un clip de 30 s admite ~60 palabras). Cada bloque `### N.M.K` es el `.txt` de ese clip, tal cual.

Registro: **público general de YouTube**. Se habla de «la tienda», nunca de un curso, una sesión, una demo o un script. Los números se dicen redondos cuando la pantalla ya los muestra exactos («unas veintidós mil páginas»), y exactos solo cuando son el punto. Lo que midió el motor se dice como medición («SQL Server midió...», «el motor leyó...»); lo que calculamos, como cálculo.

## 1.1 La página: lo que cuesta leer

### 1.1.1
Esta es una tienda en línea: doscientos mil clientes, un millón y medio de pedidos y casi cuatro millones de renglones de detalle. Aquí va a vivir todo el curso. Queremos los pedidos de un cliente. ¿Cuánto cuesta esa consulta? El tiempo engaña: cambia con cada ejecución y con cada máquina. Lo que no cambia es cuántas páginas tuvo que leer el motor.

### 1.1.2
SQL Server no guarda filas sueltas: las guarda en páginas de ocho kilobytes. En cada página de pedidos caben unas sesenta y siete filas. La tabla completa ocupa más de veintidós mil páginas. Cada vez que una consulta necesita un dato, abre la página entera. Esa es la unidad con la que se paga todo lo que sigue.

### 1.1.3
Buscar un pedido por su número es barato. Las páginas forman un árbol: el motor abre la raíz, baja a un nivel intermedio y llega a la hoja donde está el pedido. Tres páginas, tres lecturas. Y con tres niveles alcanza para el millón y medio de pedidos de la tienda.

### 1.1.4
Ahora busquemos por cliente, una columna sin índice. El motor no sabe dónde están sus pedidos, así que abre la tabla entera: más de veintidós mil lecturas. Solo le servían ciento noventa y una filas, que cabrían en tres páginas. Más de cien páginas por cada fila útil. Esa diferencia es lo que vamos a aprender a eliminar.
