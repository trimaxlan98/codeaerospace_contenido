"""Salida de video: cuadros RGB por tubería a ffmpeg (H.264, yuv420p)."""
import subprocess


class Video:
    def __init__(self, ruta, ancho, alto, fps=30, crf=17, audio=None):
        self.ruta = str(ruta)
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{ancho}x{alto}", "-r", str(fps), "-i", "-"]
        if audio:
            cmd += ["-i", str(audio), "-c:a", "aac", "-b:a", "192k", "-shortest"]
        cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p",
                "-movflags", "+faststart", self.ruta]
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    def escribir(self, rgb):
        self.p.stdin.write(rgb.tobytes())

    def cerrar(self):
        self.p.stdin.close()
        if self.p.wait() != 0:
            raise RuntimeError(f"ffmpeg falló escribiendo {self.ruta}")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.cerrar()
