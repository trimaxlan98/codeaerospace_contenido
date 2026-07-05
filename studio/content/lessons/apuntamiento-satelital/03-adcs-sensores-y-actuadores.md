---
title: "ADCS: sensores y actuadores"
level: medio
summary: Star trackers, sensores de sol y magnetómetros miden la actitud; ruedas de reacción, magnetorquers y propulsión la corrigen dentro de un presupuesto de apuntamiento.
tags: [adcs, ruedas-de-reaccion, magnetorquers, star-tracker, presupuesto-de-apuntamiento]
minutes: 9
order: 3
---

## Objetivos

- Describir los sensores de actitud más comunes y su precisión relativa: star trackers, sensores de sol, magnetómetros e IMU.
- Explicar el funcionamiento de las ruedas de reacción y el fenómeno de saturación.
- Describir los magnetorquers y la propulsión como actuadores de actitud, y cuándo se prefiere cada uno.
- Definir un presupuesto de apuntamiento distinguiendo precisión de estabilidad.
- Relacionar la elección de sensores y actuadores con el tipo de misión y su órbita.

## Sensores de actitud

Determinar la actitud requiere medir, con distintos instrumentos, vectores de referencia conocidos (hacia las estrellas, hacia el Sol, el campo magnético terrestre) y compararlos con su dirección esperada para deducir la orientación del satélite.

Los **star trackers** (rastreadores estelares) son, con diferencia, el sensor de actitud absoluta más preciso disponible comercialmente: una cámara óptica captura un campo de estrellas, identifica patrones de constelaciones mediante algoritmos de reconocimiento contra un catálogo estelar embarcado, y calcula la orientación de la cámara —y por tanto del satélite— con precisiones típicas de unos pocos segundos de arco (arcsec). Su principal limitación operativa es que requieren un campo de visión libre de fuentes brillantes (deben incorporar deflectores o baffles para evitar que el Sol, la Luna o el limbo terrestre iluminado saturen el sensor), y no funcionan durante maniobras de reapuntamiento rápido, cuando el desenfoque por movimiento impide identificar estrellas.

Los **sensores de sol** miden la dirección del Sol respecto al satélite, desde versiones simples y robustas (sensores gruesos, basados en fotodiodos, con precisión de grados, usados sobre todo para detectar la dirección solar en modos de seguridad o para orientar paneles solares) hasta sensores finos (basados en máscaras o rejillas que proyectan un patrón dependiente del ángulo de incidencia, con precisión de minutos de arco). Son extremadamente fiables y de bajo consumo, razón por la cual casi todo satélite los incluye como respaldo del modo seguro, incluso cuando el apuntamiento normal de la misión depende de sensores más precisos.

Los **magnetómetros** miden el vector del campo magnético terrestre local, que se compara con el valor esperado según un modelo geomagnético estándar (como el IGRF) para la posición orbital conocida en ese instante. Son sensores baratos, robustos y de bajo consumo, pero de precisión modesta (grados), y su utilidad decae con la altitud, porque el campo magnético terrestre se debilita rápidamente al alejarse del planeta —por lo que son prácticamente inútiles como sensor de actitud primario en GEO.

Las **unidades de medición inercial** (IMU), en particular los giroscopios, miden directamente la velocidad angular del satélite. No dan una actitud absoluta por sí mismas (integrar la velocidad angular para obtener orientación acumula error sin límite, un fenómeno llamado deriva o *drift*), pero su medición es continua y de alta frecuencia, lo que las hace indispensables como complemento de los sensores absolutos (más lentos o intermitentes) dentro de un filtro de estimación —normalmente un filtro de Kalman, como el descrito en la lección de determinación de órbitas, adaptado aquí a la estimación de actitud— que combina la deriva suave de la IMU con las correcciones periódicas y absolutas de star trackers o sensores de sol.

## Actuadores: ruedas de reacción y su saturación

Para *corregir* la actitud, no solo medirla, el actuador más común en satélites de tamaño mediano a grande es la **rueda de reacción**: un volante interno cuya velocidad de giro se controla con un motor eléctrico. Por conservación del momento angular total del sistema satélite-rueda, acelerar la rueda en una dirección produce un torque de reacción igual y opuesto sobre el cuerpo del satélite en la dirección contraria, permitiendo rotarlo de forma precisa y continua sin gastar propelente. Un conjunto típico usa tres ruedas ortogonales (una por eje) más, a menudo, una cuarta en configuración inclinada para redundancia ante el fallo de cualquiera de las otras tres.

El problema estructural de las ruedas de reacción es la **saturación**: cada vez que se usa una rueda para contrarrestar un torque externo persistente (por ejemplo, el gradiente de gravedad, la presión de radiación solar, o el arrastre residual en LEO bajo), la rueda debe acumular momento angular de forma sostenida para mantener esa oposición, y su velocidad de giro crece monótonamente hasta acercarse a su límite físico (revoluciones por minuto máximas). Una vez saturada, la rueda ya no puede aportar más torque en esa dirección y el control de actitud se pierde en ese eje. La solución es la **desaturación** (o descarga de momento): usar un actuador externo capaz de aplicar un torque neto sobre el satélite completo —típicamente magnetorquers en LEO, o pequeños propulsores en GEO— para frenar la rueda de vuelta a una velocidad de operación segura, transfiriendo el momento angular acumulado al entorno (al campo magnético terrestre, o al propelente expulsado) en lugar de mantenerlo indefinidamente dentro del sistema.

## Magnetorquers y propulsión

Los **magnetorquers** son bobinas (o, en algunos diseños, barras con núcleo ferromagnético) que, al circular corriente eléctrica, generan un momento dipolar magnético $\vec{m}$; su interacción con el campo magnético terrestre local $\vec{B}$ produce un torque $\vec{\tau} = \vec{m}\times\vec{B}$. Son extremadamente simples, ligeros, de bajo consumo y sin partes móviles ni propelente que agotar, por lo que dominan en CubeSats y en misiones LEO de bajo coste, tanto como actuador de control primario en misiones poco exigentes en precisión como para la desaturación de ruedas de reacción en misiones más sofisticadas. Su limitación fundamental es geométrica: el torque resultante del producto cruz $\vec{m}\times\vec{B}$ siempre es perpendicular a $\vec{B}$, por lo que nunca pueden aplicar torque a lo largo de la dirección instantánea del campo magnético, y su magnitud absoluta es pequeña y decae con la altitud —inútiles, de nuevo, en GEO.

La **propulsión** —pequeños propulsores químicos o eléctricos, orientados para producir pares de fuerzas— se reserva típicamente para maniobras de actitud rápidas y de gran amplitud (reapuntamientos agresivos), para la desaturación de ruedas en órbitas donde el campo magnético es demasiado débil (GEO, MEO alto), o como respaldo de emergencia. Su coste, en comparación con ruedas o magnetorquers, es que consume una masa de propelente finita y limitada, un recurso que a menudo determina directamente la vida útil operativa de la misión.

## Presupuesto de apuntamiento

El diseño de un sistema ADCS se resume en un **presupuesto de apuntamiento**, que distingue dos magnitudes con significado físico distinto: la **precisión** (o exactitud), el error entre la orientación real y la comandada en un instante dado, y la **estabilidad**, la variación (jitter) de esa orientación durante una ventana de tiempo relevante —por ejemplo, mientras un instrumento óptico realiza una exposición. Ambas se expresan habitualmente en fracciones de grado: minutos de arco (arcmin) o segundos de arco (arcsec) para misiones exigentes, grados o décimas de grado para misiones de comunicaciones o de observación de resolución moderada. Un satélite de comunicaciones GEO típico opera con precisión de apuntamiento del orden de $0.05°$–$0.1°$ (suficiente para mantener el haz de la antena sobre su zona de cobertura); un telescopio espacial de alta resolución puede requerir estabilidad del orden de milisegundos de arco durante exposiciones prolongadas, una exigencia que domina por completo la elección de sensores (star trackers de altísima precisión) y actuadores (ruedas de reacción de baja vibración, o incluso actuadores piezoeléctricos de ajuste fino) de ese tipo de misión.

## Ideas clave

- Star trackers dan la mayor precisión absoluta (arcsec) pero requieren campo despejado; sensores de sol y magnetómetros son robustos y baratos pero de precisión modesta; las IMU miden velocidad angular con deriva, complementando a los sensores absolutos.
- Las ruedas de reacción producen torque por conservación de momento angular sin gastar propelente, pero se saturan al acumular momento frente a torques externos persistentes.
- La desaturación transfiere el momento acumulado al entorno mediante magnetorquers (en LEO) o propulsores (donde el campo magnético es débil, como en GEO).
- Los magnetorquers son simples y eficientes pero no pueden torquear a lo largo del campo magnético local, y pierden eficacia con la altitud.
- El presupuesto de apuntamiento distingue precisión (error absoluto) de estabilidad (jitter durante una ventana de tiempo), y ambas magnitudes determinan la elección de sensores y actuadores.

## Para seguir

La siguiente lección, *Seguimiento desde estaciones terrenas*, cambia de perspectiva: en lugar de la actitud del propio satélite, aborda cómo una estación en tierra predice y sigue su paso, incluyendo la compensación del efecto Doppler.
