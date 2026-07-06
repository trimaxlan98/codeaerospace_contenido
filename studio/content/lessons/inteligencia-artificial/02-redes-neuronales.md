---
title: Redes neuronales desde cero
level: medio
summary: La neurona artificial, las funciones de activación, el descenso de gradiente y la retropropagación que hacen aprender a una red, más el problema del sobreajuste y cómo se combate.
tags: [redes-neuronales, gradiente, backpropagation, activacion, regularizacion]
minutes: 12
order: 2
---

## Objetivos

- Escribir el cómputo de una neurona artificial y entender cada término de $y = \sigma(\mathbf{w}^T\mathbf{x} + b)$.
- Justificar por qué hacen falta funciones de activación no lineales y comparar las más usadas.
- Explicar el descenso de gradiente como el motor del aprendizaje y el papel de la tasa de aprendizaje.
- Comprender la retropropagación como una aplicación de la regla de la cadena, sin perderse en el álgebra.
- Reconocer el sobreajuste y las técnicas que lo controlan.

## La neurona artificial

Toda red neuronal se construye con una pieza mínima que imita, muy libremente, a una neurona biológica. Recibe varias entradas $x_1, \dots, x_n$, las pondera con **pesos** $w_1, \dots, w_n$, suma un **sesgo** $b$ y pasa el resultado por una función de activación $\sigma$:

$$y = \sigma\!\left(\sum_{i=1}^{n} w_i x_i + b\right) = \sigma(\mathbf{w}^T\mathbf{x} + b)$$

Interpretación: el término $\mathbf{w}^T\mathbf{x} + b$ es una **combinación lineal** —geométricamente, un hiperplano—. Los pesos deciden cuánto importa cada entrada (y con qué signo), y el sesgo desplaza el umbral de activación. Una sola neurona con activación escalón es exactamente un clasificador lineal: el **perceptrón** de 1958. Su límite, demostrado en 1969, fue célebre: no puede aprender la función XOR, porque XOR no es separable por una sola recta. La solución tardó y resultó ser *apilar* neuronas.

Una **capa** es un conjunto de neuronas que reciben las mismas entradas en paralelo; su cómputo se escribe de golpe con una matriz de pesos $W$ y un vector de sesgos $\mathbf{b}$: $\mathbf{h} = \sigma(W\mathbf{x} + \mathbf{b})$. Una **red profunda** encadena capas: la salida de una es la entrada de la siguiente. Las capas intermedias se llaman **ocultas** porque no vemos directamente sus valores; en ellas la red construye representaciones cada vez más abstractas —de píxeles a bordes, de bordes a formas, de formas a objetos—. Ese es el "profundo" de *deep learning*.

## Por qué la no linealidad lo es todo

Si quitáramos las funciones de activación, cada capa sería una transformación lineal, y la composición de transformaciones lineales es… otra transformación lineal. Una red de mil capas sin activaciones colapsa a una sola matriz: no ganaría ninguna capacidad expresiva sobre el perceptrón. La **no linealidad** de $\sigma$ es lo que permite a la red doblar y plegar el espacio de entrada hasta separar clases que una recta jamás podría —y el teorema de aproximación universal garantiza que, con suficientes neuronas, una red de una capa oculta puede aproximar cualquier función continua—.

Las activaciones más comunes:

| Función | Fórmula | Uso típico |
|---------|---------|-----------|
| Sigmoide | $\sigma(z) = 1/(1+e^{-z})$ | Salida de probabilidad binaria; hoy poco en capas ocultas (se satura) |
| Tanh | $\tanh(z)$ | Centrada en cero; redes recurrentes clásicas |
| ReLU | $\max(0, z)$ | La opción por defecto en capas ocultas: barata y no se satura para $z>0$ |
| GELU / SiLU | variantes suaves de ReLU | Transformers modernos |
| Softmax | $e^{z_i}/\sum_j e^{z_j}$ | Capa final de clasificación multiclase |

La ReLU merece un comentario: su simplicidad (`if z<0 then 0`) fue clave para que las redes muy profundas se volvieran entrenables hacia 2011, porque no aplasta el gradiente como la sigmoide en sus extremos —el problema del **gradiente que se desvanece** que había estancado el campo—.

## Aprender es minimizar una pérdida

Entrenar una red es encontrar los pesos que hacen buenas predicciones. Para eso necesitamos una medida de "cuán mal lo hace": la **función de pérdida** $\mathcal{L}$. Para regresión, el error cuadrático medio; para clasificación, la entropía cruzada. La pérdida es una función de *todos* los parámetros de la red $\theta$ (todos los pesos y sesgos, a menudo miles de millones), y aprender es buscar el $\theta$ que la minimiza.

No podemos resolverlo analíticamente, pero sí guiarnos por la pendiente. El **gradiente** $\nabla_\theta \mathcal{L}$ es el vector de derivadas parciales: apunta en la dirección de máximo *ascenso* de la pérdida. Para bajar, damos un paso en dirección contraria. Esa es la regla del **descenso de gradiente**:

$$\theta \leftarrow \theta - \eta \, \nabla_\theta \mathcal{L}$$

El escalar $\eta$ es la **tasa de aprendizaje** (*learning rate*), el hiperparámetro más delicado: demasiado grande y el entrenamiento oscila o diverge; demasiado pequeño y tarda una eternidad o se atasca. En la práctica no se calcula el gradiente sobre todos los datos (caro) sino sobre pequeños lotes aleatorios —**descenso de gradiente estocástico** (SGD)—, y optimizadores como Adam adaptan la tasa por parámetro para acelerar la convergencia.

## Retropropagación: la regla de la cadena a escala

Queda una pregunta: ¿cómo se calcula el gradiente de la pérdida respecto a un peso que está enterrado en la tercera capa, a través de todas las no linealidades intermedias? La respuesta es la **retropropagación** (*backpropagation*), que no es más que la regla de la cadena del cálculo aplicada con orden.

La idea, sin álgebra: en la pasada **hacia adelante** (*forward*) la entrada atraviesa la red y produce una predicción y una pérdida. En la pasada **hacia atrás** (*backward*) se calcula cuánto contribuyó cada peso al error, propagando la "culpa" desde la salida hacia la entrada capa por capa. Cada capa recibe de la capa siguiente cuánto debe cambiar su salida, y con eso calcula (a) cuánto debe cambiar cada uno de sus pesos y (b) qué mensaje de error pasar a la capa anterior. Es eficiente porque reutiliza los cálculos intermedios en lugar de rehacerlos para cada peso. Los frameworks modernos (PyTorch, JAX) hacen esto automáticamente mediante **diferenciación automática**: uno escribe solo la pasada hacia adelante y la biblioteca deriva el resto. Un ciclo forward + backward + actualización sobre un lote es un **paso de entrenamiento**; millones de pasos componen el entrenamiento completo.

## El enemigo: sobreajuste

Una red con millones de parámetros puede, literalmente, *memorizar* los ejemplos de entrenamiento —incluidos su ruido y sus rarezas— sin aprender el patrón general. Eso es el **sobreajuste** (*overfitting*): pérdida bajísima en entrenamiento y pésima en datos nuevos. Su síntoma es la brecha creciente entre la curva de pérdida de entrenamiento (que sigue bajando) y la de validación (que empieza a subir). El extremo opuesto, el **subajuste**, es un modelo demasiado simple que no captura ni siquiera el patrón de entrenamiento; entre ambos vive el punto óptimo de generalización.

Las armas contra el sobreajuste conforman la **regularización**: penalizar pesos grandes añadiendo su magnitud a la pérdida (regularización $L_2$ o *weight decay*); **dropout**, que apaga aleatoriamente una fracción de neuronas en cada paso para que la red no dependa de ninguna en particular; **parada temprana** (*early stopping*), cortar cuando la validación deja de mejorar; y **aumento de datos**, generar variaciones de los ejemplos (rotar imágenes, parafrasear texto). La lección de fondo es que más datos casi siempre generalizan mejor que más trucos —y esa observación es la que motiva la escala masiva de la lección siguiente—.

## Ideas clave

- Una neurona calcula $y = \sigma(\mathbf{w}^T\mathbf{x} + b)$: una combinación lineal seguida de una activación; sin la no linealidad de $\sigma$, apilar capas no aporta poder expresivo.
- La ReLU ($\max(0,z)$) destronó a la sigmoide en capas ocultas porque no satura el gradiente y volvió entrenables las redes profundas.
- Aprender es minimizar una función de pérdida con descenso de gradiente $\theta \leftarrow \theta - \eta\nabla_\theta\mathcal{L}$; la tasa de aprendizaje $\eta$ es el hiperparámetro crítico y se usa SGD por lotes.
- La retropropagación es la regla de la cadena aplicada eficientemente para repartir el error entre todos los pesos; los frameworks la automatizan con diferenciación automática.
- El sobreajuste (memorizar en vez de generalizar) se detecta por la brecha entrenamiento-validación y se combate con regularización, dropout, parada temprana y más datos.

## Para seguir

Con la neurona, el gradiente y la retropropagación en su sitio, la próxima lección aborda la arquitectura que domina la IA actual: el *Transformer* y los grandes modelos de lenguaje construidos sobre él.
