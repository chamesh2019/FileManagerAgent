import customtkinter
import logging
import os

# Suppress all verbose logging
logging.basicConfig(level=logging.ERROR)
os.environ['GRPC_VERBOSITY'] = 'ERROR'

# Set appearance mode
customtkinter.set_appearance_mode("dark")

# Create the main window
app = customtkinter.CTk()
app.geometry("700x50")
app.title("File Manager")
app.configure(fg_color="#000000")
app.resizable(False, False)

# Remove title bar and set transparency
app.overrideredirect(True)
app.attributes("-topmost", True)
app.attributes("-transparentcolor", "#000000")

# Create input frame with border
input_frame = customtkinter.CTkFrame(
    app,
    fg_color="#2a2a2a",
    corner_radius=10,
    border_width=1,
    border_color="#3a3a3a"
)
input_frame.pack(fill="both", expand=True)

# Create the entry field
command_entry = customtkinter.CTkEntry(
    input_frame,
    placeholder_text="Search for apps and commands...",
    font=("Segoe UI", 15),
    fg_color="#2a2a2a",
    border_width=1,
    placeholder_text_color="#6a6a6a",
    text_color="#ffffff",
    height=50
)
command_entry.pack(fill="both", expand=True, padx=0, pady=0)

# Right side info (like "Tab" hint in Raycast)
info_frame = customtkinter.CTkFrame(input_frame, fg_color="#2a2a2a")
info_frame.pack(side="right", padx=0, pady=0)

def handle_command(event=None):
    command = command_entry.get().strip()
    if command.lower() == "q":
        app.quit()
    elif command:
        print(f"Command: {command}")
        command_entry.delete(0, 'end')

def handle_escape(event=None):
    app.quit()

# Bind events
command_entry.bind("<Return>", handle_command)
command_entry.bind("<Escape>", handle_escape)

# Focus on entry
command_entry.focus()

# Center window on screen
app.update_idletasks()
screen_width = app.winfo_screenwidth()
x = (screen_width - 700) // 2
app.geometry(f"+{x+100}+100")

app.mainloop()
