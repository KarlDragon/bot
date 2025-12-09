import threading
import time
import random
import tkinter as tk
from tkinter import ttk
from pynput.keyboard import Key, Controller as KeyController, Listener as KeyListener
from pynput.mouse import Button, Controller as MouseController
import ctypes

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

w_time_min = 0
w_time_max = 2000
s_time_min = 0
s_time_max = 2000
click_interval_min = 500
click_interval_max = 1000
sway_offset_min = 0
sway_offset_max = 100
sway_speed_min = 0
sway_speed_max = 10

click_button_type = "left"  # "left" or "right"

# ============================================================
# SMOOTH SWAY FUNCTION (with randomization)
# ============================================================

def sway_mouse():
    """Smooth mouse sway with randomized offset and speed."""
    if not mouse_sway_enabled:
        return
    
    # Randomize sway parameters
    sway_offset = random.randint(sway_offset_min, sway_offset_max)
    sway_speed = random.randint(sway_speed_min, sway_speed_max)
    
    if sway_offset <= 0:
        return

    steps = 20
    step_size = sway_offset / steps
    delay = sway_speed / 1000.0

    # Right
    for i in range(steps):
        if not running:
            break
        move_raw(int(step_size), 0)
        time.sleep(delay)

    # Left
    for i in range(steps):
        if not running:
            break
        move_raw(int(-step_size), 0)
        time.sleep(delay)

# ============================================================
# BOT LOOP (with randomization)
# ============================================================

def movement_loop():
    global running
    while True:
        if running and auto_move_enabled:
            # Random W time
            w_duration = random.randint(w_time_min, w_time_max)
            keyboard.press('w')
            time.sleep(w_duration / 1000)
            keyboard.release('w')

            # Random S time
            s_duration = random.randint(s_time_min, s_time_max)
            keyboard.press('s')
            time.sleep(s_duration / 1000)
            keyboard.release('s')

            # Smooth sway
            sway_mouse()

        else:
            time.sleep(0.1)

def auto_click_loop():
    global running
    while True:
        if running and auto_click_enabled:
            # Random click interval
            interval = random.randint(click_interval_min, click_interval_max)
            
            # Click based on button type
            if click_button_type == "left":
                mouse.click(Button.left)
            else:
                mouse.click(Button.right)
            
            time.sleep(interval / 1000)
        else:
            time.sleep(0.1)

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
root.title("Minecraft Bot Controller - Enhanced")
root.geometry("380x620")

def build_range_entry(label, min_default, max_default):
    frame = tk.Frame(root)
    frame.pack(pady=3)
    tk.Label(frame, text=label, width=25, anchor='w').pack(side=tk.LEFT)
    
    e_min = tk.Entry(frame, width=8)
    e_min.insert(0, str(min_default))
    e_min.pack(side=tk.LEFT, padx=2)
    
    tk.Label(frame, text="to").pack(side=tk.LEFT)
    
    e_max = tk.Entry(frame, width=8)
    e_max.insert(0, str(max_default))
    e_max.pack(side=tk.LEFT, padx=2)
    
    return e_min, e_max

tk.Label(root, text="Movement Settings (randomized)", font=("Arial", 10, "bold")).pack(pady=5)
entry_w_min, entry_w_max = build_range_entry("W hold time (ms):", w_time_min, w_time_max)
entry_s_min, entry_s_max = build_range_entry("S hold time (ms):", s_time_min, s_time_max)

tk.Label(root, text="Click Settings (randomized)", font=("Arial", 10, "bold")).pack(pady=5)
entry_click_min, entry_click_max = build_range_entry("Click interval (ms):", click_interval_min, click_interval_max)

# Click button type selection
click_frame = tk.Frame(root)
click_frame.pack(pady=5)
tk.Label(click_frame, text="Click button type:").pack(side=tk.LEFT, padx=5)
click_type_var = tk.StringVar(value="left")
tk.Radiobutton(click_frame, text="Left Click", variable=click_type_var, value="left").pack(side=tk.LEFT)
tk.Radiobutton(click_frame, text="Right Click", variable=click_type_var, value="right").pack(side=tk.LEFT)

tk.Label(root, text="Mouse Sway Settings (randomized)", font=("Arial", 10, "bold")).pack(pady=5)
entry_sway_min, entry_sway_max = build_range_entry("Sway offset (px):", sway_offset_min, sway_offset_max)
entry_sway_speed_min, entry_sway_speed_max = build_range_entry("Sway speed (ms/step):", sway_speed_min, sway_speed_max)

# Checkboxes
tk.Label(root, text="Enable/Disable Features", font=("Arial", 10, "bold")).pack(pady=5)
auto_move_var = tk.BooleanVar(value=True)
auto_click_var = tk.BooleanVar(value=True)
mouse_sway_var = tk.BooleanVar(value=True)

tk.Checkbutton(root, text="Enable Auto-Move (W/S)", variable=auto_move_var).pack()
tk.Checkbutton(root, text="Enable Auto-Click", variable=auto_click_var).pack()
tk.Checkbutton(root, text="Enable Mouse Sway", variable=mouse_sway_var).pack()

def safe_int(entry, default):
    """Safely parse integer from entry with fallback."""
    try:
        return int(entry.get())
    except ValueError:
        return default

def update_values():
    global w_time_min, w_time_max, s_time_min, s_time_max
    global click_interval_min, click_interval_max
    global sway_offset_min, sway_offset_max
    global sway_speed_min, sway_speed_max
    global auto_move_enabled, auto_click_enabled, mouse_sway_enabled
    global click_button_type

    # Update ranges with validation
    w_time_min = max(0, safe_int(entry_w_min, 0))
    w_time_max = max(w_time_min, safe_int(entry_w_max, 2000))
    
    s_time_min = max(0, safe_int(entry_s_min, 0))
    s_time_max = max(s_time_min, safe_int(entry_s_max, 2000))
    
    click_interval_min = max(50, safe_int(entry_click_min, 500))
    click_interval_max = max(click_interval_min, safe_int(entry_click_max, 1000))
    
    sway_offset_min = max(0, safe_int(entry_sway_min, 0))
    sway_offset_max = max(sway_offset_min, safe_int(entry_sway_max, 100))
    
    sway_speed_min = max(0, safe_int(entry_sway_speed_min, 0))
    sway_speed_max = max(sway_speed_min, safe_int(entry_sway_speed_max, 10))

    auto_move_enabled = auto_move_var.get()
    auto_click_enabled = auto_click_var.get()
    mouse_sway_enabled = mouse_sway_var.get()
    click_button_type = click_type_var.get()
    
    # Update display to show corrected values
    entry_w_min.delete(0, tk.END)
    entry_w_min.insert(0, str(w_time_min))
    entry_w_max.delete(0, tk.END)
    entry_w_max.insert(0, str(w_time_max))
    
    entry_s_min.delete(0, tk.END)
    entry_s_min.insert(0, str(s_time_min))
    entry_s_max.delete(0, tk.END)
    entry_s_max.insert(0, str(s_time_max))
    
    entry_click_min.delete(0, tk.END)
    entry_click_min.insert(0, str(click_interval_min))
    entry_click_max.delete(0, tk.END)
    entry_click_max.insert(0, str(click_interval_max))
    
    entry_sway_min.delete(0, tk.END)
    entry_sway_min.insert(0, str(sway_offset_min))
    entry_sway_max.delete(0, tk.END)
    entry_sway_max.insert(0, str(sway_offset_max))
    
    entry_sway_speed_min.delete(0, tk.END)
    entry_sway_speed_min.insert(0, str(sway_speed_min))
    entry_sway_speed_max.delete(0, tk.END)
    entry_sway_speed_max.insert(0, str(sway_speed_max))

tk.Button(root, text="Update Values", command=update_values, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(pady=10)
tk.Button(root, text="Start/Stop (F6)", command=toggle_running, bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack()

status_label = tk.Label(root, text="Status: STOPPED", fg="red", font=("Arial", 12, "bold"))
status_label.pack(pady=15)

tk.Label(root, text="Press F6 to toggle bot on/off", fg="gray").pack()

# Start threads
threading.Thread(target=movement_loop, daemon=True).start()
threading.Thread(target=auto_click_loop, daemon=True).start()

listener = KeyListener(on_press=on_press)
listener.start()

root.mainloop()