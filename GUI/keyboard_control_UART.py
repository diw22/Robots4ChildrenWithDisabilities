import tkinter as tk
import serial

# === UART Setup for Raspberry Pi ===
try:
    ser = serial.Serial('/dev/serial0', 9600, timeout=1)
    print("[UART] Serial connection established on /dev/serial0")
except Exception as e:
    ser = None
    print(f"[UART ERROR] Could not open serial port: {e}")

# === GUI Setup ===
root = tk.Tk()
root.title("Morse Code XAC Simulator")
root.geometry("500x250")

morse_input = ""
label = tk.Label(root, text="Morse Code: ", font=("Helvetica", 20))
label.pack(pady=20)

status = tk.Label(root, text="Waiting for input...", font=("Helvetica", 16))
status.pack(pady=10)

# Morse code to action map
morse_command_map = {
    '.': "Wave",
    '-': "Fetch Toy",
    '.-': "Play Music",
    '--': "Rest Pose",
    '-.': "Spin Around",
    '..': "Clap",
    '-.-': "Blink Lights"
}

# UART sender
def send_uart(message):
    if ser:
        try:
            ser.write((message + '\n').encode())
            print(f"[UART] Sent: {message}")
        except Exception as e:
            print(f"[UART ERROR] {e}")
    else:
        print(f"[UART] (skipped) {message}")

# Key input handling
def key_press(event):
    global morse_input

    key = event.keysym.lower()

    if key == 'space':
        morse_input += '.'
        label.config(text=f"Morse Code: {morse_input}")
        status.config(text="Typing...")
    elif key == 'shift_l' or key == 'shift_r':
        morse_input += '-'
        label.config(text=f"Morse Code: {morse_input}")
        status.config(text="Typing...")
    elif key == 'return':  # Submit Morse
        action = morse_command_map.get(morse_input.strip(), "Unknown Command")
        status.config(text=f"Action: {action}")
        print(f"[INFO] Morse '{morse_input}' → {action}")
        send_uart(action)
        morse_input = ""  # Reset input
        label.config(text="Morse Code: ")
    elif key == 'escape':  # Exit
        print("[INFO] Exit key pressed. Closing window.")
        root.destroy()

# Bind key presses
root.bind("<KeyPress>", key_press)

# Start GUI loop
root.mainloop()
