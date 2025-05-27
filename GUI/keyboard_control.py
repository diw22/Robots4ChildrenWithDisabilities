import tkinter as tk

# GUI setup
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
    elif key == 'return':  # Enter key to submit
        action = morse_command_map.get(morse_input.strip(), "Unknown Command")
        status.config(text=f"Action: {action}")
        print(f"[INFO] Morse '{morse_input}' → {action}")
        morse_input = ""  # Reset after submission
        label.config(text="Morse Code: ")
    elif key == 'escape':
        print("[INFO] Exit key pressed. Closing window.")
        root.destroy()
    

root.bind("<KeyPress>", key_press)
root.mainloop()
