---
title: "De 5G a 6G: visión y calendario"
level: intro
summary: Lo que 5G prometió y dejó pendiente, los seis escenarios de uso de IMT-2030, los KPIs objetivo de 6G y la hoja de ruta de estandarización hacia 2030.
tags: [6g, imt-2030, 5g, 3gpp, kpis]
minutes: 10
order: 1
---

## Objetivos

- Evaluar qué cumplió 5G y qué quedó pendiente de su visión original.
- Enumerar los seis escenarios de uso definidos por la ITU-R para IMT-2030 (6G).
- Comparar los KPIs objetivo de 6G frente a los de 5G con números concretos.
- Describir la hoja de ruta de estandarización: ITU-R, 3GPP Rel-20/21 y el horizonte comercial ~2030.
- Identificar las capacidades genuinamente nuevas de 6G: sensado integrado, IA nativa y cobertura tridimensional.

## Lo que 5G prometió y lo que entregó

La visión de 5G (IMT-2020) se articuló en tres escenarios: **eMBB** (banda ancha móvil mejorada), **URLLC** (comunicaciones ultra fiables de baja latencia, con objetivos de 1 ms y fiabilidad del 99.999%) y **mMTC** (comunicaciones masivas máquina a máquina, hasta $10^6$ dispositivos/km²). Una década después el balance es desigual. El eMBB se cumplió con creces: velocidades de cientos de Mbps a varios Gbps son reales donde hay despliegue de banda media (3.5 GHz) con MIMO masivo. Pero gran parte de los despliegues fueron **NSA** (*non-standalone*, radio 5G anclada a núcleo 4G), que no habilita las capacidades diferenciales; la migración a núcleo **SA** —requisito para *network slicing* y latencias bajas garantizadas— fue mucho más lenta de lo previsto. URLLC apenas encontró demanda comercial a la altura de su ingeniería: las fábricas conectadas y la cirugía remota siguieron siendo pilotos más que mercados. Las ondas milimétricas (26–39 GHz), protagonistas del marketing inicial, quedaron confinadas a puntos calientes urbanos y recintos por su corto alcance y bloqueo por obstáculos. Y la promesa de que la red generaría nuevos ingresos por servicios (más allá de vender gigabytes) sigue mayormente incumplida —una lección económica que condiciona directamente el diseño de 6G: la próxima generación se justifica menos por "más velocidad" y más por **nuevas capacidades** que abran mercados distintos.

## IMT-2030: los seis escenarios de uso

En junio de 2023, la ITU-R aprobó la *Recomendación del Marco* para **IMT-2030** (el nombre formal de 6G), definiendo seis escenarios de uso. Tres **extienden** los de 5G y tres son **genuinamente nuevos**:

1. **Comunicación inmersiva** (evolución de eMBB): realidad extendida (XR), telepresencia holográfica, video volumétrico —aplicaciones que combinan tasas muy altas con latencia y sincronía estrictas.
2. **Comunicación hiperfiable y de baja latencia** (evolución de URLLC): control industrial cerrado, redes eléctricas inteligentes, robótica cooperativa.
3. **Comunicación masiva** (evolución de mMTC): IoT denso, sensores sin batería, agricultura y logística a escala.
4. **Sensado y comunicación integrados (ISAC)** — nuevo: la red usa sus propias señales de radio como un radar distribuido para detectar posición, movimiento y gestos, habilitando servicios que no transmiten datos de nadie sino que *perciben el entorno*.
5. **IA y comunicación integradas** — nuevo: la red como plataforma de cómputo distribuido para entrenamiento e inferencia de IA (aprendizaje federado en el borde, *AI-native air interface* donde la propia capa física se optimiza con aprendizaje automático).
6. **Conectividad ubicua** — nuevo como escenario formal: cerrar la brecha de cobertura integrando redes no terrestres (satélites LEO, plataformas de gran altitud) con la red terrestre en un sistema único tridimensional.

Atravesando los seis escenarios, la ITU añade cuatro principios de diseño transversales: sostenibilidad (eficiencia energética como métrica de primera clase), seguridad y resiliencia, conectividad para todos, e inteligencia nativa.

## KPIs: 5G contra 6G en números

Los valores de 6G son objetivos de investigación y del marco IMT-2030 (rangos aún en refinamiento); los de 5G, los requisitos de IMT-2020:

| KPI | 5G (IMT-2020) | 6G (IMT-2030, objetivo) | Factor |
|-----|---------------|--------------------------|--------|
| Tasa pico | 20 Gbps | 0.2–1 Tbps | 10–50× |
| Tasa experimentada por usuario | 100 Mbps | 1–10 Gbps | 10–100× |
| Latencia de aire | 1 ms | 0.1–1 ms | hasta 10× |
| Densidad de dispositivos | $10^6$/km² | $10^7$/km² (rango $10^6$–$10^8$) | ~10× |
| Fiabilidad | 99.999% | 99.999–99.99999% | +2 nueves |
| Movilidad | 500 km/h | 500–1000 km/h | 2× |
| Eficiencia espectral | ×1 (referencia) | ×1.5–3 | 1.5–3× |
| Precisión de posicionamiento | ~m (extensiones: dm) | 1–10 cm | 10–100× |
| Eficiencia energética | ×1 (referencia) | mejora explícita como KPI | — |

Dos lecturas prudentes de la tabla. Primera: el pico de 1 Tbps exige anchos de banda de decenas de GHz que solo existen en bandas sub-THz (>100 GHz), con alcances de decenas a centenas de metros —será una capacidad de nicho, no la experiencia típica, igual que ocurrió con mmWave en 5G. Segunda: los KPIs nuevos más significativos no son los de velocidad sino los que no existían: **precisión de sensado** (resolución de la red como radar), **eficiencia energética por bit** como objetivo de diseño (las redes ya consumen ~2–3% de la electricidad en países desarrollados y el tráfico sigue creciendo) y métricas de **cobertura tridimensional** que incluyen el segmento satelital.

## Calendario: de la investigación al despliegue

La estandarización sigue el ritmo bien ensayado de las generaciones anteriores, con la ITU-R fijando requisitos y el **3GPP** produciendo las especificaciones técnicas:

```
2023        ITU-R aprueba el marco IMT-2030 (los 6 escenarios)
2024-2026   ITU-R define requisitos técnicos y metodología de evaluación
2025-2027   3GPP Release 20: estudios técnicos de 6G (en paralelo, 5G-Advanced
            continúa en Rel-18/19/20 como puente comercial)
2027-2029   3GPP Release 21: primera especificación normativa de 6G;
            presentación de candidaturas a la ITU-R
2029-2030   Evaluación y aprobación IMT-2030; primeros despliegues comerciales
~2030+      Lanzamientos comerciales (Corea, Japón, China, EE.UU., Europa)
```

Entre tanto, **5G-Advanced** (Rel-18 en adelante) funciona como banco de pruebas de conceptos que madurarán en 6G: IA/ML aplicado a la interfaz aérea, posicionamiento centimétrico, NTN mejorado, RedCap para IoT. La geopolítica del espectro se decidirá en las Conferencias Mundiales de Radiocomunicaciones (la WRC-27 es clave para las bandas medias-altas candidatas, incluido el rango 7–15 GHz), y la carrera industrial —patentes esenciales, liderazgo en estándares— es explícitamente estratégica para EE.UU., China, la UE, Corea y Japón.

## Qué cambia de verdad

Despojado del marketing, 6G se distingue de "más 5G" en tres apuestas estructurales. Primera, la red deja de ser solo un transporte de bits para convertirse en un **sensor** (ISAC) y en una **plataforma de IA** (inferencia distribuida, interfaz aérea aprendida): servicios cuyo producto no es la conectividad misma. Segunda, la **cobertura se vuelve tridimensional**: la integración satélite-terrestre pasa de parche (mensajes de emergencia direct-to-device sobre 5G NTN) a principio de arquitectura, con LEO y HAPS como capas del mismo sistema. Tercera, la **sostenibilidad pasa de eslogan a KPI**: el consumo por bit y el costo energético total condicionan decisiones de diseño de la capa física hacia arriba. Las lecciones siguientes de esta categoría desarrollan las tecnologías que sostienen estas apuestas: el espectro sub-THz, el sensado integrado, las superficies reconfigurables y las redes no terrestres.

## Ideas clave

- 5G cumplió el eMBB pero dejó pendientes el despliegue SA masivo, la monetización de URLLC/slicing y el uso amplio de mmWave; 6G se diseña con esa lección económica encima de la mesa.
- IMT-2030 define seis escenarios: tres evoluciones (inmersivo, hiperfiable, masivo) y tres nuevos (ISAC, IA integrada, conectividad ubicua), con sostenibilidad y seguridad como principios transversales.
- Los KPIs objetivo: pico 0.2–1 Tbps, latencia hasta 0.1 ms, $10^7$ disp/km², posicionamiento centimétrico — con la advertencia de que los extremos serán capacidades de nicho ligadas al sub-THz.
- Calendario: Rel-20 (estudios, 2025–2027), Rel-21 (primera norma, 2027–2029), comercial ~2030; 5G-Advanced es el puente que madura las piezas.
- Lo estructuralmente nuevo: la red como sensor y plataforma de IA, cobertura tridimensional satélite-terrestre y eficiencia energética como métrica de diseño de primera clase.

## Para seguir

La siguiente lección, *Espectro: sub-THz y nuevas bandas*, examina el recurso físico que condiciona todo lo anterior: dónde caben los terabits y qué precio impone la propagación.
