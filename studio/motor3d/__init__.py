"""Motor 3D del estudio (GPU, moderngl): Tierra con texturas NASA, atmósfera con dispersión
de Rayleigh/Mie, estrellas, terminador solar real, satélites con material y halo (bloom).

Pensado para dibujar DATOS de simulación (ROS 2: actitud, órbitas, enlaces) con aspecto
fotográfico, no para inventar movimiento: cada pose sale de una corrida.

    from motor3d import GPU, Escena, Video
"""
from .gpu import GPU                      # noqa: F401
from .escena import Escena, Camara        # noqa: F401
from .video import Video                  # noqa: F401
from . import astro, mallas               # noqa: F401
