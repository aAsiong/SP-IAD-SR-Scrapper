import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logic
import queue
import os
import sys

class NotesScraper:
    def __init__(self, root):
        self.root = root
        self.root.title("SignBox Scraper")
        self.root.geometry("550x550")
        self.root.resizable(0, 0)
        self.user_text = ""
        self.full_path = ""
        self.folder_name = "outlk-signbox-report"

        # Create Queue
        self.log_queue = queue.Queue()

        # Create GUI
        self.create_interface()

        # Check/Create DL Folder
        self.check_file_folder("")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def check_file_folder(self, filename):
        try:
            if (filename == ""):
                document_path = os.path.join(
                    os.path.expanduser('~'),
                    'Documents'
                )
                self.full_path = os.path.join(
                    document_path,
                    self.folder_name
                )
                if os.path.isdir(self.full_path):
                    return True, self.full_path
                else:
                    self.log_queue.put(
                        ("INFO",
                        f"Created {self.folder_name} in {document_path}",
                        "")
                    )
                    # Create Download Folder
                    os.makedirs(self.full_path)
                    return True, self.full_path
            else:
                format_path = os.path.join(
                    self.full_path,
                    filename
                )
                return True, format_path
        except Exception as e:
            self.log_queue.put(
                ("ERROR",
                f"{str(e)} - Try Again",
                "")
            )


    def create_interface(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main = ttk.Frame(self.root, padding=10)
        main.grid(sticky="nsew")

        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1) 
        main.rowconfigure(2, weight=1)
        main.rowconfigure(3, weight=0)
        main.rowconfigure(4, weight=0)

        header_txt = ttk.Label(
            main,
            text="Outlook SignBox SCRAPER",
            font=("Segoe UI", 15, "bold")
        )
        header_txt.grid(row=0, column=0, sticky="w", pady=(0, 30))

        instructions = ttk.Label(
            main,
            text="Paste HTML <Table> below, then click Submit to extract SignBox data.",
            font=("Segoe UI", 9)
        )
        instructions.grid(row=0, column=0, columnspan=2, sticky="w", pady=(30, 5))

        # Find first a Terms & Condition for an offline py app
        # For future use
        
        header_bttn = ttk.Frame(main)
        header_bttn.grid(row=0, column=1, sticky="se", pady=(0, 15))
        """
        header_bttn_terms = ttk.Button(header_bttn, text="Software Use")
        header_bttn_terms.grid(row=0, column=0, padx=(0, 5))
        """
        header_bttn_dev = ttk.Button(header_bttn, text="Contact", command=self.show_about)
        header_bttn_dev.grid(row=0, column=1)
        

        user_input_frame = ttk.LabelFrame(main, text="User Input", padding=10)
        user_input_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        user_input_frame.columnconfigure(0, weight=1)
        user_input_frame.rowconfigure(0, weight=1)

        self.user_input_text = tk.Text(user_input_frame, height=8, wrap="word")
        self.user_input_text.grid(row=0, column=0, sticky="nsew")

        input_scrollbar = ttk.Scrollbar(user_input_frame, orient="vertical",
                                        command=self.user_input_text.yview)
        input_scrollbar.grid(row=0, column=1, columnspan=2, sticky="ns")
        self.user_input_text.configure(yscrollcommand=input_scrollbar.set)

        progress_output_frame = ttk.LabelFrame(main, text="Progress Log", padding=10)
        progress_output_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        progress_output_frame.columnconfigure(0, weight=1)
        progress_output_frame.rowconfigure(0, weight=1)

        self.progess_output_text = tk.Text(
            progress_output_frame,
            height=6,
            fg="black",
            bg="#f8f8f8",
            state="disabled",
            wrap="word"
        )
        self.progess_output_text.grid(row=0, column=0, columnspan=2, sticky="nsew")

        progress_scrollbar = ttk.Scrollbar(progress_output_frame, orient="vertical",
                                        command=self.progess_output_text.yview)
        progress_scrollbar.grid(row=0, column=1, columnspan=2, sticky="ns")
        self.progess_output_text.configure(yscrollcommand=progress_scrollbar.set)

        progress_bar_frame = ttk.LabelFrame(main, text="Progress", padding=10)
        progress_bar_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        progress_bar_frame.columnconfigure(0, weight=1)

        self.progress_bar = ttk.Progressbar(progress_bar_frame, mode="determinate", length=400)
        self.progress_bar.grid(row=0, column=0, sticky="ew")

        progress_label = ttk.Label(progress_bar_frame, text="Ready")
        progress_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))

        button_frame = ttk.Frame(main)
        button_frame.grid(row=4, column=0, columnspan=2, sticky="e", pady=(5, 0))

        self.clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_all)
        self.clear_btn.grid(row=0, column=0, padx=(0, 10))

        self.submit_btn = ttk.Button(button_frame, text="Submit", command=self.process_submit)
        self.submit_btn.grid(row=0, column=1)
        
        self.root.after(100, self.check_queue)

    def on_closing(self):
        if messagebox.askokcancel(
            title="NOTICE",
            message="Do you want to exit application?"
        ):
            self.root.destroy()
    
    def show_about(self):
        messagebox.showinfo(
            title="CONTACT",
            message="This application was created to extract the vital information\n" \
            "inside the <Table> tag coming from SignBox daily email\n\n" \
            "For any concern or suggestion, please contact:\n" \
            "P001289 - Jonas Anthony Adaoag\n" \
            "jonas_adaoag@sercomm.com / P001289@sercomm.com\n\n" \
            "License: Freeware\n" \
            "License: LGPL"
        )

    def append_log(self, stat, message):
        if (stat == '1'):
            self.progess_output_text.tag_config("scs_text", foreground="green")
            self.progess_output_text.insert(tk.END, message + "\n", "scs_text")
        elif (stat == '2'):
            self.progess_output_text.tag_config("err_text", foreground="red")
            self.progess_output_text.insert(tk.END, message + "\n", "err_text")
        self.progess_output_text.see(tk.END)

    def check_queue(self):
        try:
            while not self.log_queue.empty():
                stat, msg, value = self.log_queue.get()
                self.progess_output_text.config(state="normal")
                if (stat == "SET_MAX"):
                    self.progess_output_text.tag_config(
                        "scs_sys", 
                        foreground="yellow",
                        background="#333333")
                    self.progess_output_text.insert(tk.END, msg + "\n", "scs_sys")
                    self.progress_bar["maximum"] = value
                    self.progress_bar["value"] = 0
                elif (stat == "INFO"):
                    self.progess_output_text.tag_config("info_text", foreground="gray")
                    self.progess_output_text.insert(tk.END, msg + "\n", "info_text")
                elif (stat == "SUCCESS"):
                    self.progess_output_text.tag_config("scs_text", foreground="green")
                    self.progess_output_text.insert(tk.END, msg + "\n", "scs_text")
                elif (stat == "ROW_DONE"):
                    self.progess_output_text.tag_config(
                        "scs_append", 
                        foreground="#00FF00",
                        background="#333333")
                    self.progess_output_text.insert(tk.END, msg + "\n", "scs_append")
                    self.progress_bar["value"] = value
                elif (stat == "FULL_DONE"):
                    self.progess_output_text.tag_config(
                        "scs_sys", 
                        foreground="yellow",
                        background="#333333")
                    self.progess_output_text.insert(tk.END, msg + "\n", "scs_sys")
                    self.progress_bar["value"] = self.progress_bar["maximum"]
                elif (stat == "ERROR"):
                    self.progess_output_text.tag_config("err_text", foreground="red")
                    self.progess_output_text.insert(tk.END, msg + "\n", "err_text")
                self.progess_output_text.see(tk.END)
                self.progess_output_text.config(state="disabled")
                self.log_queue.task_done()
        except self.log_queue.empty():
            pass
        finally:
            self.root.after(100, self.check_queue)

    def clear_all(self):
        self.user_input_text.delete(1.0, tk.END)
        self.progess_output_text.config(state="normal")
        self.progess_output_text.delete(1.0, tk.END)
        self.progess_output_text.config(state="disabled")
        self.progress_bar["value"] = 0

    def process_submit(self):
        self.user_text = self.user_input_text.get("1.0", "end-1c")
        if (len(self.user_text.strip()) == 0):
            self.log_queue.put(
                ("ERROR",
                f"No User Input Detected!",
                "")
            )
            return
        
        self.clear_btn.config(state="disabled")
        self.submit_btn.config(state="disabled")

        self.progess_output_text.config(state="normal")
        self.progess_output_text.delete(1.0, tk.END)
        self.append_log("1", "Processing <Table> Data...")
        self.progess_output_text.config(state="disabled")

        thread = threading.Thread(
            target = self.task_on_background_thread,
            daemon = True
        )
        thread.start()
    
    def task_on_background_thread(self):
        try:
            result = logic.process_input_call(self.user_text, self.log_queue, self.check_file_folder)
            self.root.after(
                0,
                self.update_ui_success,
                result
            )
        except Exception as e:
            self.root.after(
                0,
                self.update_ui_error,
                str(e)
            )

    def update_ui_success(self, result):
        self.log_queue.put(
            ("FULL_DONE",
            f"Excel Exported in {result}",
            "")
        )
        self.clear_btn.config(state="normal")
        self.submit_btn.config(state="normal")

    def update_ui_error(self, error_msg):
        print(f"Error: {error_msg}")
        self.clear_btn.config(state="normal")
        self.submit_btn.config(state="normal")

def get_path(resource_path):
    # attempt to run with biticon
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, resource_path)

def main():
    root = tk.Tk()

    # ctypes for handling taskbar icon change
    import ctypes
    spappid = 'mycompany.myproduct.subproduct.version'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(spappid)

    root.iconbitmap(get_path("app-logo.ico"))

    app = NotesScraper(root)
    root.mainloop()

if (__name__ == "__main__"):
    print("\nSignBox Scrapper Application")
    print("The application window will open shortly...")
    main()
