import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, StringVar
from tkinter import ttk, Toplevel

from ttkthemes import ThemedStyle

from imgC import convert


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
                fps.get(),
                size.get()
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
root.title("ImageConverter - Change image format and size")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

filepath = StringVar()
out_suffixes = [".jpg", ".jpg", ".png", ".tif", ".pdf", ".mp4", ".gif", '.ico']
in_suffixes = ["*", "*", ".jpg", ".png", ".tif", ".pdf", ".dcm", ".mp4", ".gif"]
filter_suffix = StringVar()
suffix = StringVar()
suffix.set(".jpg")  # set default value
filter_suffix.set("*")  # set default value

fps = tk.DoubleVar()
fps.set(30.0)  # set default value
size = tk.IntVar()
size.set(256)  # set default value

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
filter_suffix_menu = ttk.OptionMenu(mainframe, filter_suffix, *in_suffixes)
filter_suffix_menu.grid(column=2, row=2, sticky=tk.W)

ttk.Label(mainframe, text="Output:").grid(column=1, row=3, sticky=tk.W)
suffix_menu = ttk.OptionMenu(mainframe, suffix, *out_suffixes)
suffix_menu.grid(column=2, row=3, sticky=tk.W)

min_size_label = ttk.Label(mainframe, text="Min size in MB:")
min_size_label.grid(column=3, row=2, sticky=tk.W)
min_size_var = tk.DoubleVar()
min_size_var.set(0.0)
min_size = ttk.Spinbox(mainframe, from_=0.0, to=1000.0, increment=0.1, format="%.1f", textvariable=min_size_var,)
min_size.grid(column=4, row=2, sticky=tk.W)

max_size_label = ttk.Label(mainframe, text="Max size in MB:")
max_size_label.grid(column=3, row=3, sticky=tk.W)
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

fps_label = ttk.Label(mainframe, text="FPS:")
fps_spinbox = ttk.Spinbox(mainframe, from_=0.1, to=60.0, increment=0.1, format="%.1f", textvariable=fps)

ico_size_label = ttk.Label(mainframe, text="Size:")
ico_size_spinbox = ttk.Spinbox(mainframe, from_=32, to=1000.0, increment=1, format="%.1f", textvariable=size)
def update_gui(*args):
    if suffix.get() in [".mp4", ".gif"]:
        # Hide the min/max size options and show the fps option
        min_size_label.grid_remove()
        min_size.grid_remove()
        max_size_label.grid_remove()
        max_size.grid_remove()
        ico_size_label.grid_remove()
        ico_size_spinbox.grid_remove()

        fps_label.grid(column=3, row=2, sticky=tk.W)
        fps_spinbox.grid(column=4, row=2, sticky=tk.W)
        if suffix.get() == ".gif":
            ico_size_label.grid(column=3, row=3, sticky=tk.W)
            ico_size_spinbox.grid(column=4, row=3, sticky=tk.W)
    elif suffix.get() == '.ico':
        min_size_label.grid_remove()
        min_size.grid_remove()
        max_size_label.grid_remove()
        max_size.grid_remove()
        fps_label.grid_remove()
        fps_spinbox.grid_remove()

        ico_size_label.grid(column=3, row=2, sticky=tk.W)
        ico_size_spinbox.grid(column=4, row=2, sticky=tk.W)
    else:
        # Hide the fps option and show the min/max size options
        fps_label.grid_remove()
        fps_spinbox.grid_remove()
        ico_size_label.grid_remove()
        ico_size_spinbox.grid_remove()

        min_size_label.grid(column=3, row=2, sticky=tk.W)
        min_size.grid(column=4, row=2, sticky=tk.W)
        max_size_label.grid(column=3, row=3, sticky=tk.W)
        max_size.grid(column=4, row=3, sticky=tk.W)
    root.update_idletasks()
    width = root.winfo_reqwidth()
    height = root.winfo_reqheight()
    root.geometry(f"{width}x{height}")


suffix.trace_add("write", update_gui)

ttk.Button(mainframe, text="Convert", command=run_conversion).grid(
    column=1, row=6, columnspan=4, sticky=(tk.E, tk.W)
)


for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

update_gui()
root.resizable(0, 0)
root.iconbitmap("icon.ico")
root.mainloop()
