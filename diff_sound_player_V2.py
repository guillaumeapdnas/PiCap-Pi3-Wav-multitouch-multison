import tkinter as tk
from tkinter import ttk, filedialog
import threading
import time
import os
import json
import pygame
from pygame.mixer import Sound
import MPR121

# --- Constantes
DEFAULT_CONFIG_FILE = "config.json"
num_electrodes = 12
num_sounds = 12

# --- Initialisation capteur
sensor = MPR121.begin()
default_touch_threshold = 40
default_release_threshold = 20
sensor.set_touch_threshold(default_touch_threshold)
sensor.set_release_threshold(default_release_threshold)

# --- Initialisation pygame
pygame.mixer.pre_init(frequency=44100, channels=64, buffer=1024)
pygame.init()

# --- Chargement des sons
sounds = {}
for e in range(num_electrodes):
    sounds[e] = []
    folder = f"tracks/E{e}"
    for i in range(num_sounds):
        path = os.path.join(folder, f"{i:03}.wav")
        if os.path.exists(path):
            sounds[e].append(Sound(path))
        else:
            sounds[e].append(None)

# --- Variables
last_played = [None] * num_electrodes
last_time_played = [0] * num_electrodes

def get_diff(e):
    return sensor.get_baseline_data(e) - sensor.get_filtered_data(e)

# --- Interface Tkinter
root = tk.Tk()
root.title("Configuration des plages capacitives")

# Variables globales
touch_threshold_var = tk.IntVar(value=default_touch_threshold)
release_threshold_var = tk.IntVar(value=default_release_threshold)

# Variables de seuils min/max
plages = [
    [tk.IntVar(value=(i * 1 + 1 if i != 0 else 1)) for i in range(num_sounds * 2)]
    for _ in range(num_electrodes)
]

diff_labels = [tk.StringVar(value="0") for _ in range(num_electrodes)]
entry_widgets = [
    [None for _ in range(num_sounds * 2)] for _ in range(num_electrodes)
]

# Variables pour synchronisation min/max
sync_vars = [tk.BooleanVar(value=False) for _ in range(num_sounds * 2)]

# --- Fonctions de sauvegarde / chargement / reset
def save_config():
    config = {
        "touch_threshold": touch_threshold_var.get(),
        "release_threshold": release_threshold_var.get(),
        "plages": [
            [var.get() for var in plages_electrode]
            for plages_electrode in plages
        ]
    }
    filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if filepath:
        with open(filepath, "w") as f:
            json.dump(config, f, indent=4)
        print(f"Configuration sauvegard\u00e9e dans {filepath}.")

def load_config():
    filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if filepath and os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                config = json.load(f)
            touch_threshold_var.set(config.get("touch_threshold", default_touch_threshold))
            release_threshold_var.set(config.get("release_threshold", default_release_threshold))
            plages_config = config.get("plages", [])
            for e in range(num_electrodes):
                if e < len(plages_config):
                    for i in range(num_sounds * 2):
                        if i < len(plages_config[e]):
                            plages[e][i].set(plages_config[e][i])
            apply_thresholds()
            print(f"Configuration charg\u00e9e depuis {filepath}.")
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")

def apply_thresholds():
    sensor.set_touch_threshold(touch_threshold_var.get())
    sensor.set_release_threshold(release_threshold_var.get())
    print(f"Seuils appliqu\u00e9s : Touch={touch_threshold_var.get()} / Release={release_threshold_var.get()}")

def reset_all():
    touch_threshold_var.set(default_touch_threshold)
    release_threshold_var.set(default_release_threshold)
    for e in range(num_electrodes):
        for i in range(num_sounds * 2):
            plages[e][i].set(0)
    apply_thresholds()
    print("Configuration r\u00e9initialis\u00e9e.")

# --- Fonction de synchronisation min/max
def sync_column(i):
    if sync_vars[i].get():
        value_to_copy = plages[0][i].get()
        for e in range(1, num_electrodes):
            plages[e][i].set(value_to_copy)

# --- Play/Stop Control
running = True
def toggle_running():
    global running
    running = not running
    if running:
        status_label.config(text="Lecture: ON", foreground="green")
        threading.Thread(target=sound_loop, daemon=True).start()
    else:
        status_label.config(text="Lecture: OFF", foreground="red")

# --- Loop de lecture sons
def sound_loop():
    while running:
        sensor.update_baseline_data()
        sensor.update_filtered_data()
        now = time.time()
        for e in range(num_electrodes):
            diff = get_diff(e)
            diff_labels[e].set(str(diff))

            for i in range(num_sounds * 2):
                entry_widgets[e][i].configure(bg="white")

            for i in range(num_sounds):
                min_v = plages[e][2*i].get()
                max_v = plages[e][2*i+1].get()
                if min_v <= diff <= max_v:
                    entry_widgets[e][2*i].configure(bg="lightgreen")
                    entry_widgets[e][2*i+1].configure(bg="lightgreen")
                    if sounds[e][i] is not None:
                        if last_played[e] != i or (now - last_time_played[e]) > 1.0:
                            sounds[e][i].play()
                            last_played[e] = i
                            last_time_played[e] = now
                    break
        time.sleep(0.1)

# --- Contr\u00f4le du volume
def set_volume(val):
    volume = float(val) / 100
    pygame.mixer.set_num_channels(64)
    for e in range(num_electrodes):
        for i in range(num_sounds):
            if sounds[e][i] is not None:
                sounds[e][i].set_volume(volume)
    print(f"Volume r\u00e9gl\u00e9 \u00e0 {volume * 100}%")

# --- Construction Interface
param_frame = ttk.Frame(root)
param_frame.pack(side="top", fill="x", pady=5)

ttk.Label(param_frame, text="Touch Threshold:").pack(side="left", padx=5)
touch_entry = ttk.Entry(param_frame, textvariable=touch_threshold_var, width=5)
touch_entry.pack(side="left")

ttk.Label(param_frame, text="Release Threshold:").pack(side="left", padx=5)
release_entry = ttk.Entry(param_frame, textvariable=release_threshold_var, width=5)
release_entry.pack(side="left")

apply_button = ttk.Button(param_frame, text="Appliquer", command=apply_thresholds)
apply_button.pack(side="left", padx=5)

save_button = ttk.Button(param_frame, text="Sauver config", command=save_config)
save_button.pack(side="left", padx=5)

load_button = ttk.Button(param_frame, text="Charger config", command=load_config)
load_button.pack(side="left", padx=5)

reset_button = ttk.Button(param_frame, text="Reset", command=reset_all)
reset_button.pack(side="left", padx=5)

playstop_button = ttk.Button(param_frame, text="Play/Stop", command=toggle_running)
playstop_button.pack(side="left", padx=10)

status_label = ttk.Label(param_frame, text="Lecture: ON", foreground="green")
status_label.pack(side="left", padx=10)

volume_label = ttk.Label(param_frame, text="Volume:")
volume_label.pack(side="left", padx=5)

volume_slider = ttk.Scale(param_frame, from_=0, to=100, orient="horizontal", command=set_volume)
volume_slider.set(100)
volume_slider.pack(side="left", padx=5)

# --- Tableau electrodes
canvas = tk.Canvas(root)
scroll = ttk.Scrollbar(root, orient="horizontal", command=canvas.xview)
frame = ttk.Frame(canvas)

canvas.configure(xscrollcommand=scroll.set)
canvas.pack(side="top", fill="both", expand=True)
scroll.pack(side="bottom", fill="x")
canvas.create_window((0, 0), window=frame, anchor='nw')

# --- En-t\u00eate
header = ["E", "Diff"]
for i in range(num_sounds):
    bg_color = "lightblue" if i % 2 == 0 else "lightyellow"
    tk.Label(frame, text=f"S{i}\nmin", bg=bg_color, font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=2+2*i, sticky="nsew")
    tk.Label(frame, text=f"S{i}\nmax", bg=bg_color, font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=3+2*i, sticky="nsew")

# --- Remplir le tableau
for e in range(num_electrodes):
    color = "lightblue" if e % 2 == 0 else "lightyellow"
    tk.Label(frame, textvariable=diff_labels[e], fg="red", width=5, bg=color).grid(row=e+1, column=0)
    tk.Label(frame, text=f"E{e}", width=5, bg=color).grid(row=e+1, column=1)
    for i in range(num_sounds):
        entry_min = tk.Entry(frame, textvariable=plages[e][2*i], width=5, bg=color)
        entry_min.grid(row=e+1, column=2+(i*2))
        entry_widgets[e][2*i] = entry_min

        entry_max = tk.Entry(frame, textvariable=plages[e][2*i+1], width=5, bg=color)
        entry_max.grid(row=e+1, column=2+(i*2)+1)
        entry_widgets[e][2*i+1] = entry_max

# --- Ajouter les checkboxes de synchronisation sous les colonnes
for i in range(num_sounds * 2):
    cb = tk.Checkbutton(frame, variable=sync_vars[i], command=lambda idx=i: sync_column(idx))
    cb.grid(row=num_electrodes+2, column=2+i, sticky="nsew")

def update_scrollregion(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

canvas.bind('<Configure>', update_scrollregion)

def stop():
    global running
    running = False
    root.destroy()

root.protocol("WM_DELETE_WINDOW", stop)

# --- D\u00e9marrage
threading.Thread(target=sound_loop, daemon=True).start()
root.mainloop()
