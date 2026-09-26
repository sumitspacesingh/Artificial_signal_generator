
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class SignalGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Artificial Signal Generator")
        self.root.geometry("1000x650")

        self.running = False
        self.current_time = 0.0
        self.window = 5.0
        self.time_buffer = np.array([])
        self.signal_buffer = np.array([])

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

        self.create_widgets()
        self.create_plot()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(frame, text="Formula f(t) =").grid(row=0, column=0, sticky="w")
        self.formula = tk.StringVar(value="sin(2*pi*5*t)")
        ttk.Entry(frame, textvariable=self.formula, width=50).grid(row=0, column=1, columnspan=3, sticky="ew", padx=5)

        ttk.Label(frame, text="Sampling rate (Hz)").grid(row=1, column=0, sticky="w")
        self.fs = tk.StringVar(value="1000")
        ttk.Entry(frame, textvariable=self.fs, width=10).grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Duration (s)").grid(row=1, column=2, sticky="e")
        self.duration = tk.StringVar(value="10")
        ttk.Entry(frame, textvariable=self.duration, width=10).grid(row=1, column=3, sticky="w")

        self.mode = tk.StringVar(value="limited")
        ttk.Radiobutton(frame, text="Limited", variable=self.mode, value="limited").grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(frame, text="Live", variable=self.mode, value="live").grid(row=2, column=1, sticky="w")

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=8)

        ttk.Button(btn_frame, text="Start", command=self.start).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Stop", command=self.stop).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save CSV", command=self.save_csv).pack(side=tk.LEFT, padx=5)

        frame.columnconfigure(1, weight=1)

    def create_plot(self):
        self.fig = Figure(figsize=(9,5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Generated Signal")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude")
        self.line, = self.ax.plot([], [], lw=1.5)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def evaluate(self, t):
        return eval(self.formula.get(), {"__builtins__": {}}, {**self.allowed, "t": t})

    def start(self):
        try:
            self.fs_value = float(self.fs.get())
            if self.fs_value <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Invalid sampling rate.")
            return

        self.clear()

        if self.mode.get() == "limited":
            self.run_limited()
        else:
            self.running = True
            self.update_live()

    def stop(self):
        self.running = False

    def clear(self):
        self.running = False
        self.current_time = 0.0
        self.time_buffer = np.array([])
        self.signal_buffer = np.array([])
        self.line.set_data([], [])
        self.ax.set_xlim(0, 5)
        self.ax.set_ylim(-2, 2)
        self.canvas.draw()

    def run_limited(self):
        try:
            duration = float(self.duration.get())
            t = np.arange(0, duration, 1/self.fs_value)
            y = self.evaluate(t)
        except Exception as e:
            messagebox.showerror("Formula Error", str(e))
            return

        self.time_buffer = t
        self.signal_buffer = y

        self.line.set_data(t, y)
        self.ax.set_xlim(0, max(duration, 1))
        ymin, ymax = np.min(y), np.max(y)
        if ymin == ymax:
            ymin -= 1
            ymax += 1
        self.ax.set_ylim(ymin - 0.1*abs(ymin), ymax + 0.1*abs(ymax))
        self.canvas.draw()

    def update_live(self):
        if not self.running:
            return

        chunk = 0.05
        t_new = np.arange(self.current_time, self.current_time + chunk, 1/self.fs_value)

        try:
            y_new = self.evaluate(t_new)
        except Exception as e:
            self.running = False
            messagebox.showerror("Formula Error", str(e))
            return

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
        self.ax.set_ylim(ymin - 0.1*abs(ymin), ymax + 0.1*abs(ymax))

        self.canvas.draw_idle()

        self.current_time += chunk
        self.root.after(int(chunk * 1000), self.update_live)

    def save_csv(self):
        if len(self.time_buffer) == 0:
            messagebox.showinfo("No Data", "No signal available to save.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv")])
        if not path:
            return

        data = np.column_stack([self.time_buffer, self.signal_buffer])
        np.savetxt(path, data, delimiter=",", header="Time,Signal", comments="")
        messagebox.showinfo("Saved", f"Signal saved to:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SignalGeneratorApp(root)
    root.mainloop()
