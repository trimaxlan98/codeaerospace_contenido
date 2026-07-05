---
title: Superficies inteligentes reconfigurables (RIS)
level: avanzado
summary: Metasuperficies con control de fase por elemento que convierten el canal radio en algo programable, su modelo matemático, el régimen near-field y sus límites reales.
tags: [ris, metasuperficies, beamforming, near-field, canal]
minutes: 12
order: 4
---

## Objetivos

- Explicar qué es una RIS y cómo una metasuperficie logra controlar la reflexión de una onda.
- Formular el modelo de canal en cascada $y = (\mathbf{h}_r^H \boldsymbol{\Theta} \mathbf{h}_t)x + n$ y extraer sus consecuencias.
- Entender la ley de escalado de potencia con $N^2$ elementos y el doble desvanecimiento que la motiva.
- Describir el régimen de campo cercano (near-field) y por qué cambia el beamforming de dirección a punto.
- Evaluar los prototipos existentes y las limitaciones prácticas que separan la promesa del despliegue.

## La idea: programar el canal, no solo los extremos

Toda la historia de las comunicaciones inalámbricas aceptó un axioma: el canal —los rebotes, bloqueos y desvanecimientos entre transmisor y receptor— es un hecho de la naturaleza que solo cabe medir y compensar. Las **superficies inteligentes reconfigurables** (RIS, *Reconfigurable Intelligent Surfaces*) atacan el axioma mismo: paneles planos y delgados, compuestos por cientos o miles de elementos reflectores subλ, cada uno capaz de alterar la fase (y a veces la amplitud) de la onda que refleja bajo control electrónico. Coordinando las fases de todos los elementos, el panel deja de reflejar especularmente como una placa metálica y pasa a comportarse como un **espejo programable**: concentra la energía incidente en un haz dirigido hacia donde se ordene —por ejemplo, hacia el receptor que quedó a la sombra de un edificio. El canal se vuelve, parcialmente, un parámetro de diseño.

Físicamente, una RIS es una **metasuperficie**: la versión bidimensional de los metamateriales (que reaparecerán en la categoría de Tecnología de Frontera). Cada elemento es una celda resonante impresa —un parche metálico sobre sustrato— cuyo tamaño y separación son fracciones de la longitud de onda (típicamente λ/4 a λ/2). Integrando en cada celda un componente sintonizable —un diodo varactor cuya capacitancia varía con la tensión, diodos PIN que conmutan entre estados discretos de fase (1–2 bits es lo común en prototipos), o cristal líquido en diseños para frecuencias altas— se desplaza la resonancia de la celda y con ella la fase de la onda reflejada. El atributo decisivo es lo que la RIS *no* tiene: ni cadenas de RF, ni amplificadores, ni conversión de frecuencia, ni ADCs. Es **casi pasiva** (solo consume el control, vatios frente a los cientos de vatios de una estación base), delgada, silenciosa electromagnéticamente y, en principio, barata de fabricar en volumen —la propuesta económica que la distingue de un simple repetidor activo o de una celda pequeña adicional.

## El modelo: canal en cascada

Con un transmisor de una antena, una RIS de $N$ elementos y un receptor de una antena, la señal recibida por la vía de la RIS se escribe:

$$y = \left(\mathbf{h}_r^H \, \boldsymbol{\Theta} \, \mathbf{h}_t\right) x + n$$

donde $\mathbf{h}_t \in \mathbb{C}^N$ es el canal del transmisor a los elementos de la RIS, $\mathbf{h}_r \in \mathbb{C}^N$ el de la RIS al receptor, y $\boldsymbol{\Theta} = \text{diag}(\beta_1 e^{j\theta_1}, \ldots, \beta_N e^{j\theta_N})$ la matriz diagonal de reflexión, con $\theta_n$ la fase aplicada por el elemento $n$ (y $\beta_n \le 1$ su eficiencia). El canal efectivo es la suma de $N$ productos: $\sum_n \beta_n e^{j\theta_n} h_{r,n}^* h_{t,n}$. La optimización óptima es transparente: elegir cada $\theta_n$ para cancelar la fase del producto $h_{r,n}^* h_{t,n}$, de modo que las $N$ contribuciones se sumen **coherentemente** (alineadas en fase) en el receptor. Si además existe un enlace directo $h_d$, las fases se alinean contra él.

De aquí sale el resultado más citado del área: con alineación perfecta, la amplitud recibida crece como $N$ y la **potencia como $N^2$** —duplicar los elementos cuadruplica la potencia recibida vía RIS. Ese crecimiento aparentemente mágico tiene su contrapeso en el **doble desvanecimiento** (*double fading*): el enlace en cascada multiplica dos pérdidas de trayecto, y su atenuación total escala como el *producto* $d_t^2 \cdot d_r^2$ de las distancias a la RIS (en campo lejano), mucho peor que el $d^2$ de un enlace directo comparable. La ganancia $N^2$ existe precisamente para pagar esa factura: una RIS necesita ser *grande* (cientos a miles de elementos) para competir, y rinde más cuanto más cerca está de uno de los extremos del enlace (minimizando uno de los dos factores del producto). Por eso la geometría canónica de despliegue es la RIS en la fachada próxima a la zona de sombra, no a medio camino.

El talón de Aquiles operativo es la **estimación del canal**: la RIS pasiva no puede medir $\mathbf{h}_t$ ni $\mathbf{h}_r$ por sí misma; la red debe estimar el canal en cascada barriendo patrones de fase durante secuencias piloto, con un costo que crece con $N$ —para $N$ de miles, un problema serio que la investigación ataca con estructura (sparsity angular, agrupación de elementos) o con RIS *semi-pasivas* que incorporan unos pocos sensores.

## Near-field: cuando el haz se vuelve un foco

Una consecuencia fascinante del tamaño: la frontera entre campo cercano y lejano de una apertura, la **distancia de Rayleigh** $d_R = 2D^2/\lambda$, crece con el cuadrado del tamaño $D$ del panel. Una RIS de 1 m operando a 30 GHz ($\lambda = 1$ cm) tiene $d_R = 200$ m: prácticamente *toda su zona de servicio queda en campo cercano*, donde los frentes de onda ya no son planos sino esféricos. Esto invalida el modelo angular clásico pero regala una capacidad nueva: con fases ajustadas a la curvatura esférica, la superficie no forma un haz hacia una *dirección* sino un **foco en un punto** del espacio (*beamfocusing*): energía concentrada a 20 m que se desvanece a 25 m sobre la misma línea. Las implicaciones: multiplexar usuarios alineados angularmente pero a distancias distintas (imposible en far-field), posicionamiento fino usando la curvatura como observable extra (sinergia directa con ISAC de la lección anterior), y transferencia de energía inalámbrica más eficiente. El costo: los modelos, los códigos de precodificación y la estimación de canal del far-field deben rehacerse —el "near-field massive MIMO" es un área de investigación completa que 6G hereda junto con las RIS y los arreglos XL-MIMO, que cruzan la misma frontera.

## Prototipos y limitaciones reales

Los prototipos publicados desde 2020 (NTT DOCOMO con metasuperficies transparentes en 28 GHz, ZTE/China Mobile en pruebas de campo sub-6 GHz y mmWave, el prototipo RFocus del MIT con 3200 elementos, paneles académicos de 1100+ elementos en 5.8 GHz) demuestran consistentemente ganancias de 10–25 dB de potencia recibida en la zona de sombra objetivo, y los ensayos de operadores reportan mejoras de cobertura reales en esquinas urbanas y interiores. ETSI creó en 2021 el grupo ISG-RIS para pre-estandarización, y 3GPP la considera candidata de estudio para Rel-20/21 (su pariente simple, el repetidor controlado por red NCR, ya se especificó en Rel-18 como paso previo).

Las limitaciones que moderan el entusiasmo, ordenadas por severidad práctica. **El caso de negocio contra alternativas**: una celda pequeña o un repetidor activo resuelven la misma sombra con tecnología madura; la RIS gana solo si su costo total (fabricación + instalación + control) es realmente una fracción, lo que aún no está demostrado a escala. **Estimación y señalización**: el overhead de pilotos crece con $N$, y el canal de control estación-RIS necesita estandarización. **Banda estrecha del control de fase**: cada fase $\theta_n$ es óptima a una frecuencia; sobre canales anchos (los GHz del sub-THz) el desajuste de fase entre bordes del canal (*beam squint*) erosiona la ganancia. **Cuantización**: con 1–2 bits de fase se pierden ~1–3 dB respecto a fase continua (tolerable, pero real). **Estática frente a movilidad**: reconfigurar para usuarios que se mueven exige lazos de control rápidos que chocan con la propuesta de simplicidad. La síntesis honesta del estado del arte: la RIS es físicamente sólida y demostrada, su nicho inicial más plausible es la **cobertura estática de zonas de sombra en mmWave/sub-THz y FR3 alto** (donde celdas adicionales son caras y los haces son estrechos), y su expansión dependerá de que el costo por metro cuadrado y el problema de estimación de canal se resuelvan a favor.

## Ideas clave

- Una RIS es una metasuperficie casi pasiva de N elementos con fase controlable: convierte la reflexión en un grado de libertad de diseño — el canal deja de ser solo un hecho de la naturaleza.
- El modelo en cascada $y = (\mathbf{h}_r^H \boldsymbol{\Theta} \mathbf{h}_t)x + n$ se optimiza alineando fases para suma coherente: amplitud ∝ N, potencia ∝ N², la ganancia que paga el doble desvanecimiento ($\propto d_t^2 d_r^2$) del enlace reflejado.
- La RIS rinde donde es grande y está cerca de un extremo del enlace; su problema operativo central es estimar canales que ella misma no puede medir.
- Con paneles grandes y frecuencias altas, la zona de servicio cae en campo cercano ($d_R = 2D^2/\lambda$): el beamforming direccional se convierte en beamfocusing a un punto, con oportunidades nuevas (multiplexado por distancia, posicionamiento) y modelos por rehacer.
- Prototipos reales muestran 10–25 dB de ganancia en sombras; los frenos son el caso de negocio frente a repetidores y celdas pequeñas, el overhead de estimación, el beam squint en banda ancha y la movilidad.

## Para seguir

La última lección de la categoría, *Redes no terrestres (NTN) en 6G*, sube la mirada: la integración de satélites LEO y plataformas de gran altitud como capa estructural de la red — el punto donde esta categoría se encuentra con las de Satélites y Redes de Telecomunicaciones.
