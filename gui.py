import tkinter as tk
from tkinter import ttk, messagebox
from logic import clear_input_call, process_input_call

root = tk.Tk()
root.title("SP-IAD NOTES Scraper by P001289")
root.geometry("550x550")
root.resizable(0, 0)

# Configure root grid
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Main frame
main = ttk.Frame(root, padding=10)
main.grid(sticky="nsew")

# Configure main frame grid
main.columnconfigure(0, weight=1)
main.rowconfigure(1, weight=1) 
main.rowconfigure(2, weight=1)
main.rowconfigure(3, weight=0)
main.rowconfigure(4, weight=0)

# Header
header_txt = ttk.Label(
    main,
    text="SP-IAD NOTES SCRAPPER",
    font=("Segoe UI", 15, "bold")
)
header_txt.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

# Instructions label
instructions = ttk.Label(
    main,
    text="Paste HTML table below, then click Submit to extract SR data.",
    font=("Segoe UI", 9)
)
instructions.grid(row=0, column=0, sticky="w", pady=(30, 5))

# Header Button
header_bttn = ttk.Frame(main)
header_bttn.grid(row=0, column=1, sticky="se", pady=(0, 15))

header_bttn_terms = ttk.Button(header_bttn, text="Software Use")
header_bttn_terms.grid(row=0, column=0, padx=(0, 5))

header_bttn_dev = ttk.Button(header_bttn, text="About")
header_bttn_dev.grid(row=0, column=1)

def append_log(message):
    error_output_text.config(state="normal")
    error_output_text.insert(tk.END, message + "\n")
    error_output_text.see(tk.END)
    error_output_text.config(state="disabled")

def process_submit():
    user_text = user_input_text.get("1.0", "end-1c")
    if (len(user_text.strip()) == 0):
        print("User no input!")
        return
    error_output_text.delete(1.0, tk.END)
    output_arr = process_input_call(user_text, append_log)

# User Input Frame
user_input_frame = ttk.LabelFrame(main, text="User Input", padding=10)
user_input_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
user_input_frame.columnconfigure(0, weight=1)
user_input_frame.rowconfigure(0, weight=1)

user_input_text = tk.Text(user_input_frame, height=8, wrap="word")
user_input_text.grid(row=0, column=0, sticky="nsew")

# Add scrollbar for user input
input_scrollbar = ttk.Scrollbar(user_input_frame, orient="vertical",
                                command=user_input_text.yview)
input_scrollbar.grid(row=0, column=1, columnspan=2, sticky="ns")
user_input_text.configure(yscrollcommand=input_scrollbar.set)

# Error Output Frame
error_output_frame = ttk.LabelFrame(main, text="Progress Log", padding=10)
error_output_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
error_output_frame.columnconfigure(0, weight=1)
error_output_frame.rowconfigure(0, weight=1)

error_output_text = tk.Text(
    error_output_frame,
    height=6,
    fg="red",
    bg="#f8f8f8",
    state="disabled",
    wrap="word"
)
error_output_text.grid(row=0, column=0, columnspan=2, sticky="nsew")

# Add scrollbar for error output
error_scrollbar = ttk.Scrollbar(error_output_frame, orient="vertical",
                                command=error_output_text.yview)
error_scrollbar.grid(row=0, column=1, columnspan=2, sticky="ns")
error_output_text.configure(yscrollcommand=error_scrollbar.set)

# Progress Bar Frame
progress_bar_frame = ttk.LabelFrame(main, text="Progress", padding=10)
progress_bar_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))
progress_bar_frame.columnconfigure(0, weight=1)

progress_bar = ttk.Progressbar(progress_bar_frame, mode="determinate", length=400)
progress_bar.grid(row=0, column=0, sticky="ew")

progress_label = ttk.Label(progress_bar_frame, text="Ready")
progress_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))

# Button Frame
button_frame = ttk.Frame(main)
button_frame.grid(row=4, column=0, columnspan=2, sticky="e", pady=(5, 0))

clear_btn = ttk.Button(button_frame, text="Clear", command=clear_input_call)
clear_btn.grid(row=0, column=0, padx=(0, 10))

submit_btn = ttk.Button(button_frame, text="Submit", command=process_submit)
submit_btn.grid(row=0, column=1)

root.mainloop()
