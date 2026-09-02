#!/usr/bin/env python3
"""Sonda de `esp32.py`: comprueba invariantes de la mitad numerica.

Corre DENTRO del contenedor de render (el numpy del host ya corrompio
arrays en silencio una vez) y no importa manim, para que se pueda ejecutar
sin lienzo ni escena:

    docker run --rm --network none -v "$PWD:/workspace:ro" \
        codeaerospace_contenido-manim python \
        /workspace/studio/tools/sonda_esp32.py

Cada comprobacion es un invariante FISICO o ARITMETICO, no un valor
copiado de un render anterior: si la libreria cambia y sigue siendo
correcta, la sonda sigue en verde.
"""
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np

import esp32 as e

ok = fallos = 0


def check(nombre, condicion, detalle=""):
    global ok, fallos
    if condicion:
        ok += 1
        print(f"  ok   {nombre}  {detalle}")
    else:
        fallos += 1
        print(f"  FALLO {nombre}  {detalle}")


print("== 01 ciclos ==")
check("240 MHz durante 1 s son 240 millones", e.ciclos(1.0) == 240_000_000)
t = np.linspace(0, 34.0, 100)
s = e.serie_ciclos(t)
check("la serie es lineal y empieza en cero",
      s[0] == 0 and abs(s[-1] - 34.0 * 240.0) < 1e-6,
      f"final {s[-1]:.0f} millones")

print("== 02 reparto ==")
d = e.tareas()
asig, ini, carga, mk = e.reparto(d, 2)
check("el reparto conserva el trabajo", abs(carga.sum() - d.sum()) < 1e-9)
check("ninguna tarea se parte", len(np.unique(asig)) <= 2 and len(asig) == len(d))
check("el makespan es la carga del nucleo mas cargado",
      abs(mk - carga.max()) < 1e-12, f"{mk:.1f} ms")
check("cada tarea empieza donde acaba la anterior de su nucleo",
      all(abs((ini[asig == k] + d[asig == k]).max() - carga[k]) < 1e-9
          for k in (0, 1)))
a = e.aceleracion(d, 2)
check("la aceleracion esta entre 1 y 2", 1.0 < a <= 2.0, f"x{a:.2f}")
check("con una sola tarea no hay ganancia",
      abs(e.aceleracion(np.array([7.0]), 2) - 1.0) < 1e-12)
check("con tareas iguales y pares la ganancia es exactamente 2",
      abs(e.aceleracion(np.ones(8) * 5.0, 2) - 2.0) < 1e-12)

print("== 03 memoria ==")
b = e.bytes_fotograma(240, 240, 16)
check("240x240 RGB565 son 112.5 KiB", b == 115200, f"{b} B")
n = e.caben(e.memoria_kb(e.HOJA["sram_kb"]), b)
check("caben 4 fotogramas enteros en 520 KB", n == 4, f"{n}")
check("no redondea hacia arriba", e.caben(199, 100) == 1)

print("== 04 reloj ==")
T = e.periodo(e.HOJA["f_cpu"])
check("el periodo son 4.1667 ns", abs(T - 4.16667e-9) < 1e-14, f"{T*1e9:.4f} ns")
L = e.luz_por_ciclo(e.HOJA["f_cpu"])
check("la luz recorre 1.25 m por ciclo", abs(L - 1.2491) < 1e-3, f"{L:.4f} m")
check("el PLL multiplica por 6",
      abs(e.multiplicador_pll() - 6.0) < 1e-12)
check("mas reloj = menos metros por ciclo",
      e.luz_por_ciclo(80e6) > e.luz_por_ciclo(240e6))

print("== 05 pines ==")
check("32 bits son 4 294 967 296 estados",
      e.combinaciones(32) == 4_294_967_296)
t5, v5, ts = e.flanco_rc()
tau = e.HOJA["z_salida_ohm"] * 100e-12
check("el flanco 10-90 son 2.2 tau",
      abs(ts - 2.1972 * tau) < 0.02 * tau, f"{ts*1e9:.2f} ns")
check("la curva arranca en 0 y satura en Vdd",
      v5[0] == 0.0 and 0.999 * 3.3 < v5[-1] <= 3.3,
      f"final {v5[-1]:.5f} V")
check("mas capacidad = flanco mas lento",
      e.flanco_rc(C=470e-12)[2] > ts)

print("== 06 PWM ==")


def _pwm(duty, **kw):
    tp, vp, y, i0 = e.pwm_filtrado(duty, **kw)
    return e.media_y_rizado(tp[i0:], y[i0:])


media, riz = _pwm(0.5)
check("50 % de duty da media Vdd/2", abs(media - 1.65) < 0.02,
      f"{media:.4f} V")
check("el rizado es pequeño pero no nulo", 0.001 < riz < 0.10,
      f"{riz*1000:.1f} mV")
teorico = 3.3 * 0.25 / (5000.0 * 10e3 * 1e-6)
check("el rizado concuerda con V*D*(1-D)/(f*tau)",
      abs(riz - teorico) < 0.25 * teorico,
      f"medido {riz*1000:.1f} mV, formula {teorico*1000:.1f} mV")
m30, _ = _pwm(0.30)
check("30 % de duty da 30 % de Vdd", abs(m30 - 0.99) < 0.02, f"{m30:.4f} V")
_, riz_grande = _pwm(0.5, C=100e-9)
check("menos condensador = mas rizado", riz_grande > riz,
      f"{riz_grande*1000:.1f} mV con 100 nF")
_, riz_rapido = _pwm(0.5, f_pwm=20000.0)
check("mas frecuencia = menos rizado", riz_rapido < riz,
      f"{riz_rapido*1000:.1f} mV a 20 kHz")

print("== 07 ADC ==")
x = np.linspace(0, 3.3, 300_000)
rms, q = e.error_cuantizacion(x)
check("el escalon son 0.806 mV", abs(q - 3.3 / 4096) < 1e-12,
      f"{q*1000:.4f} mV")
check("el error RMS medido es q/sqrt(12)",
      abs(rms - q / np.sqrt(12)) < 0.02 * q,
      f"{rms*1000:.4f} mV vs {q/np.sqrt(12)*1000:.4f}")
check("la SNR ideal de 12 bits son 74 dB",
      abs(e.snr_ideal(12) - 74.0) < 0.05, f"{e.snr_ideal(12):.2f} dB")
sm = e.snr_medido(12)
check("la SNR medida cae cerca de la ideal", abs(sm - e.snr_ideal(12)) < 1.0,
      f"{sm:.2f} dB")
check("un bit mas son 6 dB mas",
      abs(e.snr_medido(13) - sm - 6.02) < 0.6,
      f"{e.snr_medido(13) - sm:.2f} dB")
y7, _ = e.cuantizar(np.array([-1.0, 99.0]))
check("la cuantizacion recorta al rango", y7[0] == 0.0 and y7[1] <= 3.3)

print("== 08 buses ==")
ti = e.tiempo_i2c(1024)
ts8 = e.tiempo_spi(1024)
check("1 KB por I2C a 400 kHz son 23 ms", abs(ti - 0.02306) < 5e-4,
      f"{ti*1000:.2f} ms")
check("1 KB por SPI a 40 MHz son 0.2 ms", abs(ts8 - 2.048e-4) < 1e-7,
      f"{ts8*1000:.4f} ms")
v = e.ventaja_spi()
check("SPI es unas 112 veces mas rapido", 100 < v < 125, f"x{v:.1f}")
check("I2C cuesta 9 bits por byte, no 8",
      e.tiempo_i2c(1000, 1e6) > e.tiempo_spi(1000, 1e6))

print("== 09 antena ==")
lam = e.longitud_onda(2.437e9)
check("2.437 GHz son 12.3 cm", abs(lam - 0.12302) < 1e-4,
      f"{lam*100:.2f} cm")
check("el cuarto de onda en aire son 3.08 cm",
      abs(e.cuarto_de_onda(2.437e9) - lam / 4) < 1e-12,
      f"{e.cuarto_de_onda(2.437e9)*100:.2f} cm")
check("en FR4 la antena sale mas corta",
      e.cuarto_de_onda(2.437e9, 2.6) < e.cuarto_de_onda(2.437e9, 1.0),
      f"{e.cuarto_de_onda(2.437e9, 2.6)*100:.2f} cm")

print("== 10 Wi-Fi ==")
tramos, total = e.tiempo_trama(1500)
check("los tramos suman el total",
      abs(sum(tramos.values()) - total) < 1e-9, f"{total:.1f} us")
ef = e.eficiencia_aire(1500)
check("la eficiencia esta entre 0.4 y 0.8", 0.40 < ef < 0.80,
      f"{ef*100:.1f} %")
check("un payload mas pequeño es menos eficiente",
      e.eficiencia_aire(100) < ef, f"{e.eficiencia_aire(100)*100:.1f} %")
check("el caudal util es menor que la tasa nominal",
      e.caudal_util_mbps(1500) < e.WIFI["tasa_mbps"],
      f"{e.caudal_util_mbps(1500):.1f} Mbps")

print("== 11 BLE ==")
uc, ue = e.anuncio_ble()
check("un evento de anuncio dura ~1.4 ms", 1000 < ue < 2000, f"{ue:.0f} us")
check("el evento son los tres canales", abs(ue - 3 * uc) < 1e-9)
ct = e.ciclo_trabajo(ue * 1e-6, 0.100)
check("el ciclo de trabajo esta por debajo del 2 %", ct < 0.02,
      f"{ct*100:.2f} %")
im = e.corriente_media(e.HOJA["i_ble_tx_ma"], ue * 1e-6,
                       e.HOJA["i_deep_sleep_ua"] / 1000.0, 0.100)
check("la corriente media esta entre los dos extremos",
      e.HOJA["i_deep_sleep_ua"] / 1000.0 < im < e.HOJA["i_ble_tx_ma"],
      f"{im*1000:.0f} uA")
try:
    e.corriente_media(100, 2.0, 0.01, 1.0)
    check("un encendido mayor que el periodo se rechaza", False)
except ValueError:
    check("un encendido mayor que el periodo se rechaza", True)

print("== 12 latencia ==")
ls = e.latencias_sondeo(10.0)
li = e.latencias_isr()
check("el sondeo nunca supera su periodo", ls.max() <= 10.0 + 1e-9,
      f"peor {ls.max():.2f} ms")
check("la media del sondeo es medio periodo",
      abs(ls.mean() - 5.0) < 0.6, f"{ls.mean():.2f} ms")
check("la interrupcion es al menos mil veces mejor",
      ls.max() / li.max() > 1000, f"x{ls.max()/li.max():.0f}")

print("== 13 planificador ==")
_, j0 = e.planificar(acaparador_ms=0.0)
_, j1 = e.planificar(acaparador_ms=4.0)
check("sin acaparador el jitter es despreciable", j0 < 0.02,
      f"{j0*1000:.1f} us")
check("con acaparador el jitter crece", j1 > 20 * j0, f"{j1:.2f} ms")
real, _ = e.planificar(acaparador_ms=4.0)
check("los despertares nunca se adelantan",
      bool(np.all(np.diff(real) > 0)))

print("== 14 pila ==")
i = e.consumo_medio_ua(2.0, 3600.0)
check("despertar 2 s cada hora sale a ~99 uA", 90 < i < 110, f"{i:.1f} uA")
dias = e.autonomia_dias()
check("sin autodescarga da mas de dos años", dias > 700, f"{dias:.0f} dias")
dias_real = e.autonomia_dias(autodescarga_por_ano=0.03)
check("la autodescarga acorta la vida", dias_real < dias,
      f"{dias_real:.0f} dias")
check("despertar mas seguido gasta mas",
      e.autonomia_dias(periodo_s=60.0) < dias)
check("el limite de la pila sola es 1/autodescarga",
      abs(e.autonomia_dias(t_despierto_s=0.0, i_dormido_ua=0.0,
                           autodescarga_por_ano=0.05) - 365.0 / 0.05) < 1.0)

print(f"\n{ok} ok / {fallos} fallos")
sys.exit(1 if fallos else 0)
