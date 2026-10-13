import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import cv2
import time


class JarvisSplash:

    # ==================================================
    # AJUSTES VISUALES
    # ==================================================
    # Aquí podrás hacer futuros cambios rápidos sin
    # buscar valores por todo el código.
    #
    # POSICIÓN DEL NÚCLEO
    CORE_X = 0.50
    CORE_Y = 0.41

    # TAMAÑO DEL NÚCLEO
    CORE_SIZE_FACTOR = 0.30

    # POSICIÓN DE LA BARRA
    BAR_X = 0.50
    BAR_Y = 0.78

    # ANCHO DE LA BARRA
    BAR_WIDTH_FACTOR = 0.27

    # Duración mínima de la carga
    MIN_LOADING_SECONDS = 8

    # ==================================================
    # INICIALIZACIÓN
    # ==================================================

    def __init__(self, on_complete):

        self.on_complete = on_complete

        # --------------------------------------------------
        # VENTANA
        # --------------------------------------------------

        self.root = tk.Tk()
        self.root.title("YAELCORE OS")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", self.close)

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # --------------------------------------------------
        # CANVAS
        # --------------------------------------------------

        self.canvas = tk.Canvas(
            self.root,
            bg="black",
            highlightthickness=0
        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        # --------------------------------------------------
        # RUTAS
        # --------------------------------------------------

        base_path = Path(__file__).resolve().parents[2]

        self.image_path = (
            base_path
            / "assets"
            / "yaelcore_interface.png"
        )

        self.video_path = (
            base_path
            / "assets"
            / "yaelcore_interface.mp4"
        )

        if not self.image_path.exists():
            raise FileNotFoundError(
                f"No se encontró la imagen:\n{self.image_path}"
            )

        if not self.video_path.exists():
            raise FileNotFoundError(
                f"No se encontró el video:\n{self.video_path}"
            )

        # --------------------------------------------------
        # IMAGEN BASE
        # --------------------------------------------------

        original = Image.open(
            self.image_path
        ).convert("RGB")

        self.background_image = self.fit_image(
            original,
            self.screen_width,
            self.screen_height
        )

        # --------------------------------------------------
        # VIDEO
        # --------------------------------------------------

        self.video = cv2.VideoCapture(
            str(self.video_path)
        )

        if not self.video.isOpened():
            raise RuntimeError(
                "No se pudo abrir yaelcore_interface.mp4"
            )

        self.video_width = int(
            self.video.get(cv2.CAP_PROP_FRAME_WIDTH)
        )

        self.video_height = int(
            self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )

        self.video_fps = (
            self.video.get(cv2.CAP_PROP_FPS)
            or 24
        )

        self.video_frames = int(
            self.video.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        self.video_duration = (
            self.video_frames / self.video_fps
            if self.video_frames > 0
            else 10
        )

        # --------------------------------------------------
        # POSICIÓN / TAMAÑO DEL NÚCLEO DEL VIDEO
        # --------------------------------------------------

        self.core_x = self.CORE_X
        self.core_y = self.CORE_Y

        self.core_size = int(
            min(
                self.screen_width,
                self.screen_height
            ) * self.CORE_SIZE_FACTOR
        )

        # Zona del MP4 que contiene el reactor.
        self.video_center_x = (
            self.video_width * 0.50
        )

        self.video_center_y = (
            self.video_height * 0.425
        )

        self.video_radius = (
            min(
                self.video_width,
                self.video_height
            ) * 0.21
        )

        # --------------------------------------------------
        # MÁSCARA DEL NÚCLEO
        # --------------------------------------------------

        self.core_mask = Image.new(
            "L",
            (
                self.core_size,
                self.core_size
            ),
            0
        )

        draw = ImageDraw.Draw(
            self.core_mask
        )

        center = self.core_size // 2

        radius = int(
            self.core_size * 0.47
        )

        draw.ellipse(
            (
                center - radius,
                center - radius,
                center + radius,
                center + radius
            ),
            fill=255
        )

        self.core_mask = self.core_mask.filter(
            ImageFilter.GaussianBlur(
                max(
                    3,
                    int(
                        self.core_size * 0.018
                    )
                )
            )
        )

        # --------------------------------------------------
        # ESTADO
        # --------------------------------------------------

        self.running = True
        self.finished = False

        self.start_time = time.monotonic()

        # --------------------------------------------------
        # BARRA DE CARGA
        # --------------------------------------------------

        self.bar_center_x = (
            self.screen_width * self.BAR_X
        )

        self.bar_center_y = (
            self.screen_height * self.BAR_Y
        )

        self.bar_width = int(
            self.screen_width
            * self.BAR_WIDTH_FACTOR
        )

        self.bar_height = int(
            max(
                8,
                self.screen_height * 0.012
            )
        )

        self.bar_x1 = (
            self.bar_center_x
            - self.bar_width / 2
        )

        self.bar_x2 = (
            self.bar_center_x
            + self.bar_width / 2
        )

        # --------------------------------------------------
        # TEXTO DE LA BARRA
        # --------------------------------------------------

        self.system_title = self.canvas.create_text(
            self.bar_center_x,
            self.bar_center_y - 43,
            text="SISTEMA NEURONEXUS",
            fill="#00BFFF",
            font=("Consolas", 11),
            tags="ui"
        )

        self.initialization_text = self.canvas.create_text(
            self.bar_center_x - 38,
            self.bar_center_y - 22,
            text="SYSTEM INITIALIZATION",
            fill="#D8E8F0",
            font=("Consolas", 9),
            tags="ui"
        )

        self.percent_text = self.canvas.create_text(
            self.bar_center_x + 83,
            self.bar_center_y - 22,
            text="0%",
            fill="#EAF7FF",
            font=("Consolas", 15),
            tags="ui"
        )

        # --------------------------------------------------
        # BARRA BASE
        # --------------------------------------------------

        self.canvas.create_rectangle(
            self.bar_x1,
            self.bar_center_y - 4,
            self.bar_x2,
            self.bar_center_y + 4,
            fill="#071923",
            outline="#0B3448",
            width=1,
            tags="ui"
        )

        # --------------------------------------------------
        # SEGMENTOS
        # --------------------------------------------------

        self.segment_count = 16
        self.segments = []

        gap = 4

        segment_width = (
            self.bar_width
            - gap * (self.segment_count - 1)
        ) / self.segment_count

        for i in range(self.segment_count):

            x1 = (
                self.bar_x1
                + i * (
                    segment_width + gap
                )
            )

            x2 = x1 + segment_width

            segment = self.canvas.create_rectangle(
                x1,
                self.bar_center_y - 3,
                x2,
                self.bar_center_y + 3,
                fill="#09202B",
                outline="",
                tags="ui"
            )

            self.segments.append(segment)

        # --------------------------------------------------
        # TEXTO INFERIOR
        # --------------------------------------------------

        self.sync_text = self.canvas.create_text(
            self.bar_center_x,
            self.bar_center_y + 24,
            text="SINCRONIZACIÓN EN CURSO",
            fill="#8EA5AF",
            font=("Consolas", 8),
            tags="ui"
        )

        # --------------------------------------------------
        # ESTADO SUPERIOR
        # --------------------------------------------------

        self.state_text = self.canvas.create_text(
            self.screen_width * 0.50,
            self.screen_height * 0.022,
            text="ESTADO: INICIALIZANDO",
            fill="#00FF88",
            font=("Consolas", 10),
            tags="ui"
        )

        # --------------------------------------------------
        # ARRANCAR
        # --------------------------------------------------

        self.animate()

    # ==================================================
    # IMAGEN COMPLETA SIN DEFORMAR
    # ==================================================

    def fit_image(self, image, width, height):

        scale = max(
            width / image.width,
            height / image.height
        )

        new_width = int(
            image.width * scale
        )

        new_height = int(
            image.height * scale
        )

        resized = image.resize(
            (
                new_width,
                new_height
            ),
            Image.Resampling.LANCZOS
        )

        left = (
            new_width - width
        ) // 2

        top = (
            new_height - height
        ) // 2

        return resized.crop(
            (
                left,
                top,
                left + width,
                top + height
            )
        )

    # ==================================================
    # OBTENER FRAME DEL NÚCLEO
    # ==================================================

    def get_core_frame(self):

        success, frame = self.video.read()

        if not success:

            self.video.set(
                cv2.CAP_PROP_POS_FRAMES,
                0
            )

            success, frame = self.video.read()

        if not success:
            return None

        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        image = Image.fromarray(frame)

        radius = self.video_radius

        left = max(
            0,
            int(
                self.video_center_x
                - radius
            )
        )

        top = max(
            0,
            int(
                self.video_center_y
                - radius
            )
        )

        right = min(
            image.width,
            int(
                self.video_center_x
                + radius
            )
        )

        bottom = min(
            image.height,
            int(
                self.video_center_y
                + radius
            )
        )

        core = image.crop(
            (
                left,
                top,
                right,
                bottom
            )
        )

        core = core.resize(
            (
                self.core_size,
                self.core_size
            ),
            Image.Resampling.LANCZOS
        )

        core.putalpha(
            self.core_mask
        )

        return core

    # ==================================================
    # DIBUJAR INTERFAZ + NÚCLEO
    # ==================================================

    def draw_interface(self):

        core = self.get_core_frame()

        frame = self.background_image.copy()

        if core is not None:

            x = int(
                self.screen_width * self.core_x
                - self.core_size / 2
            )

            y = int(
                self.screen_height * self.core_y
                - self.core_size / 2
            )

            frame.paste(
                core,
                (
                    x,
                    y
                ),
                core
            )

        self.photo = ImageTk.PhotoImage(frame)

        self.canvas.delete("interface")

        self.canvas.create_image(
            0,
            0,
            image=self.photo,
            anchor="nw",
            tags="interface"
        )

        # La barra y estados siempre quedan encima.
        self.canvas.tag_raise("ui")

    # ==================================================
    # ACTUALIZAR PROGRESO
    # ==================================================

    def update_progress(self):

        elapsed = (
            time.monotonic()
            - self.start_time
        )

        duration = max(
            self.MIN_LOADING_SECONDS,
            self.video_duration
        )

        progress = min(
            100,
            (elapsed / duration) * 100
        )

        value = int(progress)

        # --------------------------------------------------
        # ESTADO
        # --------------------------------------------------

        if value < 20:
            state = "ESTADO: INICIALIZANDO"

        elif value < 40:
            state = "ESTADO: CARGANDO INTELIGENCIA"

        elif value < 60:
            state = "ESTADO: SINCRONIZANDO PERCEPCIÓN"

        elif value < 80:
            state = "ESTADO: CALIBRANDO REACCIÓN"

        elif value < 100:
            state = "ESTADO: ACTIVANDO AUTONOMÍA"

        else:
            state = "ESTADO: SISTEMA ACTIVO"

        self.canvas.itemconfig(
            self.state_text,
            text=state
        )

        # --------------------------------------------------
        # PORCENTAJE
        # --------------------------------------------------

        self.canvas.itemconfig(
            self.percent_text,
            text=f"{value}%"
        )

        # --------------------------------------------------
        # SEGMENTOS
        # --------------------------------------------------

        active_count = int(
            (progress / 100)
            * self.segment_count
        )

        for i, segment in enumerate(
            self.segments
        ):

            self.canvas.itemconfig(
                segment,
                fill=(
                    "#58C8FF"
                    if i < active_count
                    else "#09202B"
                )
            )

        # --------------------------------------------------
        # TEXTO INFERIOR
        # --------------------------------------------------

        self.canvas.itemconfig(
            self.sync_text,
            text=(
                "SINCRONIZACIÓN COMPLETA"
                if value >= 100
                else "SINCRONIZACIÓN EN CURSO"
            )
        )

        return progress

    # ==================================================
    # ANIMACIÓN
    # ==================================================

    def animate(self):

        if not self.running:
            return

        self.draw_interface()

        progress = self.update_progress()

        if progress >= 100:

            if not self.finished:

                self.finished = True

                self.canvas.itemconfig(
                    self.state_text,
                    text="ESTADO: SISTEMA ACTIVO"
                )

                self.canvas.itemconfig(
                    self.sync_text,
                    text="SINCRONIZACIÓN COMPLETA"
                )

                self.root.after(
                    900,
                    self.finish
                )

            return

        self.root.after(
            40,
            self.animate
        )

    # ==================================================
    # FINALIZAR
    # ==================================================

    def finish(self):

        if not self.running:
            return

        self.running = False

        if self.video is not None:
            self.video.release()

        self.root.destroy()

        self.on_complete()

    # ==================================================
    # CERRAR
    # ==================================================

    def close(self, event=None):

        self.running = False

        if self.video is not None:
            self.video.release()

        self.root.destroy()

    # ==================================================
    # MOSTRAR
    # ==================================================

    def show(self):

        self.root.mainloop()


if __name__ == "__main__":

    splash = JarvisSplash(
        lambda: print(
            "YAELCORE OS iniciado."
        )
    )

    splash.show()