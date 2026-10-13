import tkinter as tk
import math


class JarvisCoreUI:

    def __init__(self, jarvis):

        self.jarvis = jarvis

        # ==================================================
        # VENTANA
        # ==================================================

        self.root = tk.Tk()
        self.root.title("YAELCORE OS")
        self.root.configure(bg="black")

        self.root.attributes(
            "-fullscreen",
            True
        )

        self.root.bind(
            "<Escape>",
            self.close
        )

        # ==================================================
        # DIMENSIONES
        # ==================================================

        self.width = (
            self.root.winfo_screenwidth()
        )

        self.height = (
            self.root.winfo_screenheight()
        )

        self.center_x = (
            self.width // 2
        )

        self.center_y = int(
            self.height * 0.38
        )

        # ==================================================
        # CANVAS
        # ==================================================

        self.canvas = tk.Canvas(
            self.root,
            bg="black",
            highlightthickness=0
        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        # ==================================================
        # ANIMACIÓN
        # ==================================================

        self.angle = 0.0
        self.pulse = 0.0

        # ==================================================
        # TEXTO
        # ==================================================

        self.title = self.canvas.create_text(
            self.center_x,
            int(self.height * 0.74),
            text="YAELCORE OS",
            fill="#EAF7FF",
            font=("Arial", 28)
        )

        self.state_text = self.canvas.create_text(
            self.center_x,
            int(self.height * 0.80),
            text="NEURONEXUS // SYSTEM READY",
            fill="#00BFFF",
            font=("Consolas", 14)
        )

        self.system_text = self.canvas.create_text(
            self.center_x,
            int(self.height * 0.85),
            text=(
                "VOICE SYSTEM   •   AI CORE   •   MEMORY   •   AUTONOMY"
            ),
            fill="#4D6B78",
            font=("Consolas", 10)
        )

        self.command_text = self.canvas.create_text(
            self.center_x,
            int(self.height * 0.90),
            text="",
            fill="#7FA9B8",
            font=("Consolas", 9)
        )

        # ==================================================
        # ARRANCAR
        # ==================================================

        self.animate()

    # ==================================================
    # ESTADO ACTUAL
    # ==================================================

    def get_state(self):

        try:
            return self.jarvis.state.value
        except Exception:
            return "IDLE"

    # ==================================================
    # CONFIGURACIÓN SEGÚN ESTADO
    # ==================================================

    def get_visual_state(self):

        state = self.get_state()

        settings = {

            "BOOTING": {
                "speed": 1.0,
                "pulse_speed": 0.10,
                "core_scale": 1.00,
                "ring_width": 2,
                "state_text": "NEURONEXUS // INITIALIZING",
            },

            "IDLE": {
                "speed": 1.0,
                "pulse_speed": 0.08,
                "core_scale": 1.00,
                "ring_width": 2,
                "state_text": "NEURONEXUS // SYSTEM READY",
            },

            "LISTENING": {
                "speed": 2.2,
                "pulse_speed": 0.16,
                "core_scale": 1.10,
                "ring_width": 3,
                "state_text": "NEURONEXUS // LISTENING",
            },

            "PROCESSING": {
                "speed": 6.0,
                "pulse_speed": 0.24,
                "core_scale": 1.18,
                "ring_width": 4,
                "state_text": "NEURONEXUS // PROCESSING",
            },

            "SPEAKING": {
                "speed": 3.5,
                "pulse_speed": 0.20,
                "core_scale": 1.13,
                "ring_width": 4,
                "state_text": "NEURONEXUS // SPEAKING",
            },

            "ERROR": {
                "speed": 0.0,
                "pulse_speed": 0.05,
                "core_scale": 0.95,
                "ring_width": 2,
                "state_text": "NEURONEXUS // ERROR",
            },
        }

        return settings.get(
            state,
            settings["IDLE"]
        )

    # ==================================================
    # CORE
    # ==================================================

    def draw_core(self):

        self.canvas.delete(
            "core"
        )

        visual = self.get_visual_state()

        self.angle += visual["speed"]
        self.pulse += visual["pulse_speed"]

        pulse_amount = (
            math.sin(self.pulse) * 10
        )

        scale = visual["core_scale"]

        outer_radius = (
            165 * scale
            + pulse_amount
        )

        middle_radius = (
            118 * scale
        )

        inner_radius = (
            128 * scale
        )

        core_radius = (
            40 * scale
            + pulse_amount * 0.4
        )

        # ------------------------------------------
        # ANILLO EXTERIOR
        # ------------------------------------------

        self.canvas.create_oval(
            self.center_x - outer_radius,
            self.center_y - outer_radius,
            self.center_x + outer_radius,
            self.center_y + outer_radius,
            outline="#006F9E",
            width=visual["ring_width"],
            tags="core"
        )

        # ------------------------------------------
        # ANILLO MEDIO
        # ------------------------------------------

        self.canvas.create_oval(
            self.center_x - middle_radius,
            self.center_y - middle_radius,
            self.center_x + middle_radius,
            self.center_y + middle_radius,
            outline="#004B6B",
            width=1,
            tags="core"
        )

        # ------------------------------------------
        # ANILLO INTERIOR
        # ------------------------------------------

        self.canvas.create_oval(
            self.center_x - inner_radius,
            self.center_y - inner_radius,
            self.center_x + inner_radius,
            self.center_y + inner_radius,
            outline="#00384F",
            width=1,
            tags="core"
        )

        # ------------------------------------------
        # ARCOS
        # ------------------------------------------

        self.draw_arc(
            outer_radius,
            self.angle,
            65,
            4
        )

        self.draw_arc(
            middle_radius,
            -self.angle * 1.5,
            90,
            2
        )

        self.draw_arc(
            inner_radius,
            self.angle * 2,
            35,
            3
        )

        # ------------------------------------------
        # MARCADORES
        # ------------------------------------------

        for i in range(12):

            angle = math.radians(
                (i * 30) + self.angle
            )

            radius = (
                outer_radius + 10
            )

            x1 = (
                self.center_x
                + math.cos(angle)
                * radius
            )

            y1 = (
                self.center_y
                + math.sin(angle)
                * radius
            )

            x2 = (
                self.center_x
                + math.cos(angle)
                * (radius + 7)
            )

            y2 = (
                self.center_y
                + math.sin(angle)
                * (radius + 7)
            )

            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill="#007EA7",
                width=2,
                tags="core"
            )

        # ------------------------------------------
        # NÚCLEO
        # ------------------------------------------

        self.canvas.create_oval(
            self.center_x - core_radius,
            self.center_y - core_radius,
            self.center_x + core_radius,
            self.center_y + core_radius,
            outline="#00BFFF",
            width=2,
            tags="core"
        )

        center_radius = (
            5
            + abs(pulse_amount) * 0.15
        )

        self.canvas.create_oval(
            self.center_x - center_radius,
            self.center_y - center_radius,
            self.center_x + center_radius,
            self.center_y + center_radius,
            fill="#00BFFF",
            outline="",
            tags="core"
        )

    # ==================================================
    # ARCOS
    # ==================================================

    def draw_arc(
        self,
        radius,
        start,
        extent,
        width
    ):

        self.canvas.create_arc(
            self.center_x - radius,
            self.center_y - radius,
            self.center_x + radius,
            self.center_y + radius,
            start=start,
            extent=extent,
            style=tk.ARC,
            outline="#00BFFF",
            width=width,
            tags="core"
        )

    # ==================================================
    # ESTADO
    # ==================================================

    def update_state(self):

        visual = self.get_visual_state()

        self.canvas.itemconfig(
            self.state_text,
            text=visual["state_text"]
        )

        state = self.get_state()

        labels = {
            "BOOTING": "BOOTING",
            "IDLE": "READY",
            "LISTENING": "MIC ACTIVE",
            "PROCESSING": "AI CORE ACTIVE",
            "SPEAKING": "VOICE ACTIVE",
            "ERROR": "SYSTEM ERROR",
        }

        mode = labels.get(
            state,
            "READY"
        )

        self.canvas.itemconfig(
            self.system_text,
            text=(
                "VOICE SYSTEM   •   AI CORE   •   MEMORY   •   "
                f"{mode}"
            )
        )

    # ==================================================
    # ANIMACIÓN
    # ==================================================

    def animate(self):

        self.draw_core()
        self.update_state()

        self.root.after(
            40,
            self.animate
        )

    # ==================================================
    # MOSTRAR COMANDO
    # ==================================================

    def show_command(self, text):

        self.canvas.itemconfig(
            self.command_text,
            text="COMMAND // " + str(text)[:80]
        )

    # ==================================================
    # MOSTRAR RESPUESTA
    # ==================================================

    def show_response(self, text):

        self.canvas.itemconfig(
            self.command_text,
            text="YAELCORE // " + str(text)[:80]
        )

    # ==================================================
    # CERRAR
    # ==================================================

    def close(self, event=None):

        try:
            self.root.destroy()
        except Exception:
            pass

    # ==================================================
    # MOSTRAR
    # ==================================================

    def show(self):

        self.root.mainloop()