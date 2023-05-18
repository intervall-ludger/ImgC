import tkinter as tk
from tkinter import ttk, filedialog, StringVar
from pathlib import Path
from imgC import convert
from ttkthemes import ThemedStyle
import threading
import time
from tkinter import ttk, Toplevel, Spinbox


def run_conversion():
    load_win = Toplevel(root)
    load_win.title("Loading...")
    load_win.geometry("200x50")

    loading_label = ttk.Label(load_win)
    loading_label.pack()

    loading_texts = [
        "Loading",
        "Loading.",
        "Loading..",
        "Loading...",
        "Loading....",
        "Loading.....",
    ]
    loading_index = 0

    def update_loading_text():
        nonlocal loading_index
        loading_label.config(text=loading_texts[loading_index])
        loading_index = (loading_index + 1) % len(loading_texts)
        load_win.after(500, update_loading_text)

    def execute_conversion():
        convert(
            Path(filepath.get()),
            suffix.get(),
            float(min_size.get()),
            float(max_size.get()),
            filter_suffix.get(),
        )
        if load_win.winfo_exists():
            load_win.destroy()

    thread = threading.Thread(target=execute_conversion)
    thread.start()

    update_loading_text()  # Start the loading text animation.


def browse_file():
    filename = filedialog.askopenfilename(initialdir="/", title="Select a File")
    filepath.set(filename)


def browse_dir():
    dirname = filedialog.askdirectory(initialdir="/", title="Select a Directory")
    filepath.set(dirname)


root = tk.Tk()
style = ThemedStyle(root)
style.set_theme("clam")
root.title("ImgC - Optimizer for image format and size")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

filepath = StringVar()
out_suffixes = [".jpg", ".png", ".tif", ".pdf", ".mp4", ".gif"]
in_suffixes = ["*", ".jpg", ".png", ".tif", ".pdf", ".dcm"]
filter_suffix = StringVar()
suffix = StringVar()
suffix.set(".jpg")  # set default value
filter_suffix.set("*")  # set default value

ttk.Label(mainframe, text="File/Directory Path:").grid(column=1, row=1, sticky=tk.W)
ttk.Entry(mainframe, width=50, textvariable=filepath).grid(
    column=2, row=1, sticky=(tk.W, tk.E), columnspan=3
)

ttk.Button(mainframe, text="Open File", command=browse_file).grid(
    column=5, row=1, sticky=tk.W
)
ttk.Button(mainframe, text="Open Directory", command=browse_dir).grid(
    column=6, row=1, sticky=tk.W
)

ttk.Label(mainframe, text="Input Filter:").grid(column=1, row=2, sticky=tk.W)
filter_suffix_menu = tk.OptionMenu(mainframe, filter_suffix, *in_suffixes)
filter_suffix_menu.grid(column=2, row=2, sticky=tk.W)

ttk.Label(mainframe, text="Output:").grid(column=1, row=3, sticky=tk.W)
suffix_menu = tk.OptionMenu(mainframe, suffix, *out_suffixes)
suffix_menu.grid(column=2, row=3, sticky=tk.W)

ttk.Label(mainframe, text="Min size in MB:").grid(column=3, row=2, sticky=tk.W)
min_size = Spinbox(mainframe, from_=0.0, to=1000.0, increment=0.1, format="%.1f")
min_size.grid(column=4, row=2, sticky=tk.W)

ttk.Label(mainframe, text="Max size in MB:").grid(column=3, row=3, sticky=tk.W)
max_size_var = tk.DoubleVar()
max_size_var.set(1000.0)
max_size = ttk.Spinbox(
    mainframe,
    from_=0.0,
    to=1000.0,
    increment=0.1,
    format="%.1f",
    textvariable=max_size_var,
)
max_size.grid(column=4, row=3, sticky=tk.W)


ttk.Button(mainframe, text="Run", command=run_conversion).grid(
    column=1, row=6, columnspan=4
)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

root.update_idletasks()
width = root.winfo_reqwidth()
height = root.winfo_reqheight()
root.geometry(f"{width}x{height}")
root.resizable(0, 0)


root.mainloop()
