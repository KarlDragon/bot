import threading
import time
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
auto_click_enabled = True
mouse_sway_enabled = True
hold_shift_enabled = True

click_interval = 500
sway_offset = 50
sway_speed = 5
sway_interval = 2000

click_button_type = "left"  # "left" or "right"

# ============================================================
# SHIFT HOLD LOOP
# ============================================================

def shift_hold_loop():
    """Continuously hold left shift when running and enabled."""
    global running
    shift_held = False
    
    while True:
        if running and hold_shift_enabled:
            if not shift_held:
                keyboard.press(Key.shift)
                shift_held = True
            time.sleep(0.1)
        else:
            if shift_held:
                keyboard.release(Key.shift)
                shift_held = False
            time.sleep(0.1)

# ============================================================
# MOUSE SWAY LOOP (separate thread)
# ============================================================

def sway_loop():
    """Independent mouse sway loop with fixed timing."""
    global running
    while True:
        if running and mouse_sway_enabled:
            if sway_offset > 0:
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
            
            # Wait before next sway
            time.sleep(sway_interval / 1000)
        else:
            time.sleep(0.1)

# ============================================================
# AUTO CLICK LOOP
# ============================================================

def auto_click_loop():
    global running
    while True:
        if running and auto_click_enabled:
            # Click based on button type
            if click_button_type == "left":
                mouse.click(Button.left)
            else:
                mouse.click(Button.right)
            
            time.sleep(click_interval / 1000)
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
root.title("Minecraft Bot - Click & Sway")
root.geometry("380x450")

def build_entry(label, default):
    frame = tk.Frame(root)
    frame.pack(pady=3)
    tk.Label(frame, text=label, width=25, anchor='w').pack(side=tk.LEFT)
    
    entry = tk.Entry(frame, width=10)
    entry.insert(0, str(default))
    entry.pack(side=tk.LEFT, padx=2)
    
    return entry

tk.Label(root, text="Click Settings", font=("Arial", 10, "bold")).pack(pady=5)
entry_click = build_entry("Click interval (ms):", click_interval)

# Click button type selection
click_frame = tk.Frame(root)
click_frame.pack(pady=5)
tk.Label(click_frame, text="Click button type:").pack(side=tk.LEFT, padx=5)
click_type_var = tk.StringVar(value="left")
tk.Radiobutton(click_frame, text="Left Click", variable=click_type_var, value="left").pack(side=tk.LEFT)
tk.Radiobutton(click_frame, text="Right Click", variable=click_type_var, value="right").pack(side=tk.LEFT)

tk.Label(root, text="Mouse Sway Settings", font=("Arial", 10, "bold")).pack(pady=5)
entry_sway = build_entry("Sway offset (px):", sway_offset)
entry_sway_speed = build_entry("Sway speed (ms/step):", sway_speed)
entry_sway_interval = build_entry("Sway interval (ms):", sway_interval)

# Checkboxes
tk.Label(root, text="Enable/Disable Features", font=("Arial", 10, "bold")).pack(pady=5)
auto_click_var = tk.BooleanVar(value=True)
mouse_sway_var = tk.BooleanVar(value=True)
hold_shift_var = tk.BooleanVar(value=True)

tk.Checkbutton(root, text="Enable Auto-Click", variable=auto_click_var).pack()
tk.Checkbutton(root, text="Enable Mouse Sway", variable=mouse_sway_var).pack()
tk.Checkbutton(root, text="Enable Hold Left Shift", variable=hold_shift_var).pack()

def safe_int(entry, default):
    """Safely parse integer from entry with fallback."""
    try:
        return int(entry.get())
    except ValueError:
        return default

def update_values():
    global click_interval
    global sway_offset
    global sway_speed
    global sway_interval
    global auto_click_enabled, mouse_sway_enabled, hold_shift_enabled
    global click_button_type

    # Update values with validation
    click_interval = max(50, safe_int(entry_click, 500))
    
    sway_offset = max(0, safe_int(entry_sway, 50))
    
    sway_speed = max(0, safe_int(entry_sway_speed, 5))
    
    sway_interval = max(0, safe_int(entry_sway_interval, 2000))

    auto_click_enabled = auto_click_var.get()
    mouse_sway_enabled = mouse_sway_var.get()
    hold_shift_enabled = hold_shift_var.get()
    click_button_type = click_type_var.get()
    
    # Update display to show corrected values
    entry_click.delete(0, tk.END)
    entry_click.insert(0, str(click_interval))
    
    entry_sway.delete(0, tk.END)
    entry_sway.insert(0, str(sway_offset))
    
    entry_sway_speed.delete(0, tk.END)
    entry_sway_speed.insert(0, str(sway_speed))
    
    entry_sway_interval.delete(0, tk.END)
    entry_sway_interval.insert(0, str(sway_interval))

tk.Button(root, text="Update Values", command=update_values, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(pady=10)
tk.Button(root, text="Start/Stop (F6)", command=toggle_running, bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack()

status_label = tk.Label(root, text="Status: STOPPED", fg="red", font=("Arial", 12, "bold"))
status_label.pack(pady=15)

tk.Label(root, text="Press F6 to toggle bot on/off", fg="gray").pack()

# Start threads
threading.Thread(target=shift_hold_loop, daemon=True).start()
threading.Thread(target=sway_loop, daemon=True).start()
threading.Thread(target=auto_click_loop, daemon=True).start()

listener = KeyListener(on_press=on_press)
listener.start()

root.mainloop()