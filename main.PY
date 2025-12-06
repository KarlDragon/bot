import threading
import time
import tkinter as tk
from tkinter import ttk
from pynput.keyboard import Key, Controller as KeyController, Listener as KeyListener
from pynput.mouse import Button, Controller as MouseController
import ctypes
import ctypes.wintypes as wintypes

keyboard = KeyController()
mouse = MouseController()

# ============================================================
# RAW INPUT MOUSE MOVE
# ============================================================

SendInput = ctypes.windll.user32.SendInput
MOUSEEVENTF_MOVE = 0x0001

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.c_void_p)
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("mi", MOUSEINPUT)
    ]

def move_raw(dx, dy):
    inp = INPUT()
    inp.type = 0
    inp.mi = MOUSEINPUT(dx, dy, 0, MOUSEEVENTF_MOVE, 0, None)
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

# ============================================================
# CONFIG VARIABLES
# ============================================================

running = False
auto_move_enabled = True
auto_click_enabled = True
mouse_sway_enabled = True

w_time = 2000
s_time = 2000
click_interval = 500
sway_offset = 100
sway_speed = 10

# ============================================================
# SMOOTH SWAY FUNCTION (same as the “other” code)
# ============================================================

def sway_mouse():
    """Smooth 20-step mouse sway, like the other script."""
    if sway_offset <= 0 or not mouse_sway_enabled:
        return

    steps = 20
    step_size = sway_offset / steps
    delay = sway_speed / 1000.0

    # Right
    for i in range(steps):
        move_raw(int(step_size), 0)
        time.sleep(delay)

    # Left
    for i in range(steps):
        move_raw(int(-step_size), 0)
        time.sleep(delay)

# ============================================================
# BOT LOOP (your style + integrated sway like the other script)
# ============================================================

def movement_loop():
    global running
    while True:
        if running and auto_move_enabled:
            # Hold W
            keyboard.press('w')
            time.sleep(w_time / 1000)
            keyboard.release('w')

            # Hold S
            keyboard.press('s')
            time.sleep(s_time / 1000)
            keyboard.release('s')

            # Smooth sway (AFTER movement)
            sway_mouse()

        else:
            time.sleep(0.05)

def auto_click_loop():
    global running
    while True:
        if running and auto_click_enabled:
            mouse.click(Button.left)
            time.sleep(click_interval / 1000)
        else:
            time.sleep(0.05)

# ============================================================
# START/STOP CONTROL
# ============================================================

def toggle_running():
    global running
    running = not running

    status_label.config(text=f"Status: {'RUNNING' if running else 'STOPPED'}",
                        fg="green" if running else "red")

def on_press(key):
    if key == Key.f6:
        toggle_running()

# ============================================================
# GUI
# ============================================================

root = tk.Tk()
root.title("Minecraft Bot Controller")
root.geometry("320x470")

def build_entry(label, default):
    tk.Label(root, text=label).pack()
    e = tk.Entry(root)
    e.insert(0, str(default))
    e.pack()
    return e

entry_w = build_entry("W hold time (ms):", w_time)
entry_s = build_entry("S hold time (ms):", s_time)
entry_click = build_entry("Left-click interval (ms):", click_interval)
entry_sway = build_entry("Mouse sway offset (px):", sway_offset)
entry_sway_speed = build_entry("Mouse sway speed (ms per step):", sway_speed)

auto_move_var = tk.BooleanVar(value=True)
auto_click_var = tk.BooleanVar(value=True)
mouse_sway_var = tk.BooleanVar(value=True)

tk.Checkbutton(root, text="Enable Auto-Move (W/S)", variable=auto_move_var).pack()
tk.Checkbutton(root, text="Enable Auto-Click", variable=auto_click_var).pack()
tk.Checkbutton(root, text="Enable Mouse Sway", variable=mouse_sway_var).pack()

def update_values():
    global w_time, s_time, click_interval, sway_offset, sway_speed
    global auto_move_enabled, auto_click_enabled, mouse_sway_enabled

    w_time = int(entry_w.get())
    s_time = int(entry_s.get())
    click_interval = int(entry_click.get())
    sway_offset = int(entry_sway.get())
    sway_speed = int(entry_sway_speed.get())

    auto_move_enabled = auto_move_var.get()
    auto_click_enabled = auto_click_var.get()
    mouse_sway_enabled = mouse_sway_var.get()

tk.Button(root, text="Update Values", command=update_values).pack(pady=10)
tk.Button(root, text="Start/Stop (F6)", command=toggle_running).pack()

status_label = tk.Label(root, text="Status: STOPPED", fg="red")
status_label.pack(pady=15)

threading.Thread(target=movement_loop, daemon=True).start()
threading.Thread(target=auto_click_loop, daemon=True).start()

listener = KeyListener(on_press=on_press)
listener.start()

root.mainloop()
