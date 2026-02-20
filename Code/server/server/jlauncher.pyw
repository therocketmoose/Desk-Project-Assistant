import tkinter as tk
import subprocess
import sys
import os
import time
import signal

# --- CONFIGURATION ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_SCRIPT = os.path.join(CURRENT_DIR, "server.py")
CLIENT_SCRIPT = os.path.join(CURRENT_DIR, "client.py")

# Global variables to hold the running AI
server_process = None
client_process = None

def start_jarvis():
    global server_process, client_process
    
    # Don't start if already running
    if server_process or client_process:
        status_label.config(text="Jarvis is already running!", fg="orange")
        return

    # 1. Start Server
    status_label.config(text="Starting Core...", fg="blue")
    root.update()
    
    try:
        server_process = subprocess.Popen(
            [sys.executable, SERVER_SCRIPT],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        # Wait a moment for the brain to load
        status_label.config(text="Waiting for Core...", fg="blue")
        root.update()
        time.sleep(2) 

        # 2. Start Client
        client_process = subprocess.Popen(
            [sys.executable, CLIENT_SCRIPT],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        status_label.config(text="Jarvis is Online", fg="green")
        start_btn.config(state=tk.DISABLED)
        stop_btn.config(state=tk.NORMAL)
        
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")

def stop_jarvis():
    global server_process, client_process
    
    # Kill the processes if they exist
    if server_process:
        server_process.kill()
        server_process = None
        
    if client_process:
        client_process.kill()
        client_process = None
        
    status_label.config(text="Offline", fg="red")
    start_btn.config(state=tk.NORMAL)
    stop_btn.config(state=tk.DISABLED)

def on_closing():
    stop_jarvis()
    root.destroy()

# --- GUI SETUP ---
root = tk.Tk()
root.title("J.A.R.V.I.S Launcher")
root.geometry("300x150")

# Label
status_label = tk.Label(root, text="Offline", font=("Arial", 14), fg="red")
status_label.pack(pady=20)

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

start_btn = tk.Button(btn_frame, text="START", width=10, command=start_jarvis, bg="#dddddd")
start_btn.pack(side=tk.LEFT, padx=10)

stop_btn = tk.Button(btn_frame, text="STOP", width=10, command=stop_jarvis, bg="#ffcccc", state=tk.DISABLED)
stop_btn.pack(side=tk.LEFT, padx=10)

# Handle the "X" button on the window
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()