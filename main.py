import os
from io import BytesIO
import numpy as np

import matplotlib
matplotlib.use("Agg")  # Non-GUI backend for mobile rendering
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

from kivy.app import App
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView


class SignalGeneratorApp(App):
    def build(self):
        self.title = "Artificial Signal Generator"
        self.running = False
        self.current_time = 0.0
        self.window = 5.0
        self.time_buffer = np.array([])
        self.signal_buffer = np.array([])
        self.fs_value = 1000.0
        self.clock_event = None

        self.allowed = {
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "exp": np.exp,
            "sqrt": np.sqrt,
            "log": np.log,
            "abs": np.abs,
            "pi": np.pi,
            "np": np
        }

        # Root Layout
        root_layout = BoxLayout(orientation="vertical", padding=10, spacing=8)

        # Controls Section
        controls_scroll = ScrollView(size_hint=(1, 0.45))
        controls = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None)
        controls.bind(minimum_height=controls.setter("height"))

        # Formula Input
        controls.add_widget(Label(text="Formula f(t):", size_hint_y=None, height=25))
        self.formula_input = TextInput(text="sin(2*pi*5*t)", multiline=False, size_hint_y=None, height=40)
        controls.add_widget(self.formula_input)

        # Parameters Grid
        grid = GridLayout(cols=2, spacing=6, size_hint_y=None, height=80)
        grid.add_widget(Label(text="Sampling rate (Hz):"))
        self.fs_input = TextInput(text="1000", multiline=False)
        grid.add_widget(self.fs_input)

        grid.add_widget(Label(text="Duration (s):"))
        self.duration_input = TextInput(text="10", multiline=False)
        grid.add_widget(self.duration_input)
        controls.add_widget(grid)

        # Mode Selection
        mode_box = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=40)
        self.btn_limited = ToggleButton(text="Limited", group="mode", state="down")
        self.btn_live = ToggleButton(text="Live", group="mode")
        mode_box.add_widget(self.btn_limited)
        mode_box.add_widget(self.btn_live)
        controls.add_widget(mode_box)

        # Action Buttons
        btn_box = GridLayout(cols=4, spacing=6, size_hint_y=None, height=45)
        btn_start = Button(text="Start", on_press=self.start)
        btn_stop = Button(text="Stop", on_press=self.stop)
        btn_clear = Button(text="Clear", on_press=self.clear)
        btn_save = Button(text="Save CSV", on_press=self.save_csv)
        btn_box.add_widget(btn_start)
        btn_box.add_widget(btn_stop)
        btn_box.add_widget(btn_clear)
        btn_box.add_widget(btn_save)
        controls.add_widget(btn_box)

        controls_scroll.add_widget(controls)
        root_layout.add_widget(controls_scroll)

        # Matplotlib Plot Setup
        self.plot_image = Image(size_hint=(1, 0.55), allow_stretch=True)
        root_layout.add_widget(self.plot_image)

        self.init_plot()
        return root_layout

    def init_plot(self):
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Generated Signal")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude")
        self.line, = self.ax.plot([], [], lw=1.5)
        self.ax.set_xlim(0, 5)
        self.ax.set_ylim(-2, 2)
        self.canvas_agg = FigureCanvasAgg(self.fig)
        self.update_canvas()

    def update_canvas(self):
        self.canvas_agg.draw()
        buf = BytesIO()
        self.fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        core_img = CoreImage(buf, ext="png")
        self.plot_image.texture = core_img.texture

    def evaluate(self, t):
        return eval(self.formula_input.text, {"__builtins__": {}}, {**self.allowed, "t": t})

    def show_popup(self, title, message):
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        content.add_widget(Label(text=message))
        btn = Button(text="OK", size_hint=(1, 0.35))
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def start(self, instance):
        try:
            self.fs_value = float(self.fs_input.text)
            if self.fs_value <= 0:
                raise ValueError
        except Exception:
            self.show_popup("Error", "Invalid sampling rate.")
            return

        self.clear(None)

        if self.btn_limited.state == "down":
            self.run_limited()
        else:
            self.running = True
            if self.clock_event:
                self.clock_event.cancel()
            self.clock_event = Clock.schedule_interval(self.update_live, 0.05)

    def stop(self, instance):
        self.running = False
        if self.clock_event:
            self.clock_event.cancel()

    def clear(self, instance):
        self.stop(None)
        self.current_time = 0.0
        self.time_buffer = np.array([])
        self.signal_buffer = np.array([])
        self.line.set_data([], [])
        self.ax.set_xlim(0, 5)
        self.ax.set_ylim(-2, 2)
        self.update_canvas()

    def run_limited(self):
        try:
            duration = float(self.duration_input.text)
            t = np.arange(0, duration, 1 / self.fs_value)
            y = self.evaluate(t)
        except Exception as e:
            self.show_popup("Formula Error", str(e))
            return

        self.time_buffer = t
        self.signal_buffer = y

        self.line.set_data(t, y)
        self.ax.set_xlim(0, max(duration, 1))
        ymin, ymax = np.min(y), np.max(y)
        if ymin == ymax:
            ymin -= 1
            ymax += 1
        self.ax.set_ylim(ymin - 0.1 * abs(ymin), ymax + 0.1 * abs(ymax))
        self.update_canvas()

    def update_live(self, dt):
        if not self.running:
            return False

        chunk = 0.05
        t_new = np.arange(self.current_time, self.current_time + chunk, 1 / self.fs_value)

        try:
            y_new = self.evaluate(t_new)
        except Exception as e:
            self.stop(None)
            self.show_popup("Formula Error", str(e))
            return False

        self.time_buffer = np.concatenate([self.time_buffer, t_new])
        self.signal_buffer = np.concatenate([self.signal_buffer, y_new])

        mask = self.time_buffer >= (self.current_time - self.window)
        self.time_buffer = self.time_buffer[mask]
        self.signal_buffer = self.signal_buffer[mask]

        self.line.set_data(self.time_buffer, self.signal_buffer)
        self.ax.set_xlim(max(0, self.current_time - self.window), self.current_time + chunk)

        ymin, ymax = np.min(self.signal_buffer), np.max(self.signal_buffer)
        if ymin == ymax:
            ymin -= 1
            ymax += 1
        self.ax.set_ylim(ymin - 0.1 * abs(ymin), ymax + 0.1 * abs(ymax))
        self.update_canvas()

        self.current_time += chunk

    def save_csv(self, instance):
        if len(self.time_buffer) == 0:
            self.show_popup("No Data", "No signal available to save.")
            return

        save_dir = self.user_data_dir
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, "signal_output.csv")

        data = np.column_stack([self.time_buffer, self.signal_buffer])
        np.savetxt(file_path, data, delimiter=",", header="Time,Signal", comments="")
        self.show_popup("Saved", f"Saved successfully to:\n{file_path}")


if __name__ == "__main__":
    SignalGeneratorApp().run()