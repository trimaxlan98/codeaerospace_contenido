class Clip2(Scene):
    """8.2.2 - El paquete se vuelve bundle y cada salto acepta la custodia:
    el almacenamiento es parte de la red, no un accidente. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El bundle y la custodia")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: de paquete a bundle ---------------------------------
        rot.mostrar(pie_curso("En Internet el dato es un paquete que caduca "
                              "en segundos. Aqui se vuelve un bundle."),
                    zona="abajo", run_time=0.5)
        ip = paquete([("IP", 1.0, "20 B"), ("TCP", 1.0, "20 B"),
                      ("Carga", 3.0, "%s MB" % fmt(TAM_MB, 0))],
                     ancho=6.4, alto=0.80, fs=17, color_carga=C_PAQUETE)
        ip.move_to(UP * 0.95)
        et_ip = tag_junto(ip, "datagrama IP", DOWN, buff=0.30, font_size=19)
        self.play(FadeIn(ip), FadeIn(et_ip), run_time=0.6)
        self.wait(2.4)
        self.play(FadeOut(ip), FadeOut(et_ip), run_time=0.4)
        bundle = paquete([("Origen", 1.0, "rover"),
                          ("Destino", 1.0, "control"),
                          ("Vida util", 1.0, "30 d"),
                          ("Custodia", 1.0, "si"),
                          ("Carga", 1.7, "%s MB" % fmt(TAM_MB, 0))],
                         ancho=9.4, alto=0.86, fs=17, color_carga=C_PAQUETE)
        bundle.move_to(UP * 0.95)
        et_bundle = tag_junto(bundle, "bundle", DOWN, buff=0.30,
                              font_size=19)
        self.play(FadeIn(bundle), FadeIn(et_bundle), run_time=0.7)
        self.wait(3.0)

        # --- momento: el ACK que no vuelve --------------------------------
        rot.mostrar(pie_curso("Nadie espera aqui un ACK de la otra punta: "
                              "tardaria %s minutos en volver."
                              % fmt(MARTE["rtt_min"], 0)),
                    zona="abajo", run_time=0.5)
        marcado = bundle.con_valores({})
        marcado.iluminar("Vida util", C_CIFRA)
        self.play(Transform(bundle, marcado), run_time=0.5)
        cifras = cifras_apiladas(
            [("Marte a %s UA: %s min luz por sentido"
              % (fmt(MARTE["ua"], 1), fmt(MARTE["ida_min"], 1)), C_CALCULO),
             ("el apreton de TCP gasta un RTT entero: %s min antes del "
              "primer byte" % fmt(MIN_ANTES_DEL_PRIMER_BYTE, 0), C_CALCULO),
             ("en orbita geoestacionaria el RTT era de %s ms"
              % fmt(GEO["rtt_ms"], 1), C_TENUE)],
            fs=19, pos=DOWN * 1.85)
        self.play(FadeIn(cifras, shift=0.12 * UP), run_time=0.7)
        self.wait(4.4)

        # --- momento: la custodia se firma --------------------------------
        rot.mostrar(pie_curso("Lo que se traspasa no es solo el dato: es la "
                              "CUSTODIA. El siguiente se hace responsable."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(bundle), FadeOut(et_bundle), FadeOut(cifras),
                  run_time=0.4)
        pos = {"rover": (-4.6, 0.0), "orbitador": (-1.55, 0.0),
               "DSN": (1.55, 0.0), "control": (4.6, 0.0)}
        aristas = {("rover", "orbitador"): None,
                   ("orbitador", "DSN"): None,
                   ("DSN", "control"): None}
        tipos = {"rover": "host", "orbitador": "satelite",
                 "DSN": "router", "control": "servidor"}
        cadena = topologia(pos, aristas, tipos, costos=False, tam=0.46)
        cadena.shift(UP * 1.45)
        almacenes = {}
        for k in CAMINO:
            q = cola(capacidad=3, ocupacion=0, lado=0.30, color=C_EJE,
                     color_lleno=C_PAQUETE)
            q.move_to(cadena.punto(k) + DOWN * 0.98)
            almacenes[k] = q
        et_alm = tag_hud("almacen", font_size=18, color=C_TENUE)
        et_alm.next_to(almacenes["rover"], DOWN, buff=0.20)
        self.play(FadeIn(cadena.enlaces), FadeIn(cadena.nodos),
                  *[FadeIn(q) for q in almacenes.values()],
                  FadeIn(et_alm), run_time=0.9)
        q_rover = almacenes["rover"]
        self.play(Transform(q_rover, q_rover.con_ocupacion(1)), run_time=0.35)
        b = ficha("B", lado=0.44, fs=15)
        b.move_to(cadena.punto("rover") + UP * 0.46)
        self.play(FadeIn(b, scale=1.3), run_time=0.4)
        self.play(b.animate.move_to(cadena.punto("orbitador") + UP * 0.46),
                  run_time=1.0)
        q_orb = almacenes["orbitador"]
        self.play(FadeOut(b),
                  Transform(q_orb, q_orb.con_ocupacion(1)),
                  Transform(q_rover, q_rover.con_ocupacion(0)),
                  run_time=0.45)
        et_cust = tag_hud("custodia aceptada", font_size=19, color=C_OK)
        et_cust.next_to(almacenes["orbitador"], DOWN, buff=0.22)
        self.play(FadeIn(et_cust), cadena.nodo("orbitador").forma.animate
                  .set_stroke(C_OK, width=3.6), run_time=0.45)
        self.wait(3.2)

        # --- momento: el almacen es parte de la red -----------------------
        rot.mostrar(pie_curso("Y si el siguiente tramo no esta, el bundle no "
                              "se descarta: se queda guardado."),
                    zona="abajo", run_time=0.5)
        corte = cruz((cadena.punto("orbitador") + cadena.punto("DSN")) / 2.0)
        self.play(FadeIn(corte, scale=1.5), run_time=0.4)
        self.wait(0.6)
        cifras2 = cifras_apiladas(
            [("%s MB ocupando disco en el orbitador, no un bufer de ms"
              % fmt(TAM_MB, 0), C_PAQUETE),
             ("el rover ya borro su copia: la responsabilidad viajo con el "
              "bundle", C_OK)],
            fs=19, pos=DOWN * 2.05)
        self.play(FadeIn(cifras2, shift=0.12 * UP), run_time=0.6)
        self.wait(4.4)
