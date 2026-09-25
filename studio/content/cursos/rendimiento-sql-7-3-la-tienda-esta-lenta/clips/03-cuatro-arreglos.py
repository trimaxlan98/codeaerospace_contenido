class Clip3(Scene):
    """7.3.3 - Los cuatro arreglos del caso, uno por cada tipo de peticion,
    cada uno la lectura de una leccion anterior (sin nombrar el numero de
    leccion): el ticket (indice en la llave foranea), mis pedidos (indice
    que cubre), login (el tipo del parametro) y el reporte (rango en vez
    de envolver la columna). Sin cifras nuevas: es un resumen de metodo.
    (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Cuatro arreglos"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        filas = [
            ("el ticket", icono_llave,
             ["CREATE INDEX ix_detalle", "  ON detalle (id_pedido)"]),
            ("mis pedidos", icono_viaje,
             ["INDEX (id_cliente, fecha DESC)", "  INCLUDE (estatus, total)"]),
            ("login", icono_tipo, ["DECLARE @email VARCHAR(120)"]),
            ("reporte", icono_year,
             ["WHERE fecha_pedido >= @d1", "  AND fecha_pedido < @d2"]),
        ]
        ys = [1.9, 0.7, -0.5, -1.7]

        for (nombre, fabrica_icono, codigo), y in zip(filas, ys):
            nom = Text(nombre, font_size=24, color=C_TITULO)
            nom.move_to([-5.15, y + 0.5, 0])
            icono = fabrica_icono(escala=1.25)
            icono.move_to([-5.15, y, 0])
            cod = S.codigo(codigo, font_size=18)
            cod.move_to([0.3, y, 0])
            self.play(FadeIn(nom), FadeIn(icono), run_time=0.6)
            self.wait(0.6)
            self.play(FadeIn(cod, shift=LEFT * 0.15), run_time=0.6)
            chk = marca_hecho(escala=1.3)
            chk.move_to([4.9, y, 0])
            self.play(FadeIn(chk), run_time=0.4)
            self.wait(2.2)

        self.wait(9.6)
