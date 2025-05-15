import sys
import os

# Add the project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from tkinter import filedialog
from utilz.openssl_utils import *

import customtkinter as ctk
import os

desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

class DB_App:
    def __init__(self, root):
        self.root = root
        self.root.title("DB App SI")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        #file to be encrypted
        self.encrypt_button = ctk.CTkButton(self.root, text="Encrypt File", command=self.encrypting_file)
        self.encrypt_button.pack(pady=20)

        self.status_label = ctk.CTkLabel(self.root, text="", text_color="white")
        self.status_label.pack(pady=20)

        self.create_ui()
    
    def create_ui(self):
        #TBA
        return

    def load_file(self):
        if os.path.exists(self.encryption_file):
            try:
                with open(self.encryption_file, "r") as f:
                    data = f.read()
            except:
                return {}
            return {}
        
    def encrypting_file(self):
        file_path = filedialog.askopenfilename(title="Select file to encrypt")
        if file_path:
            try:
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                encrypt_file(file_path, file_name, "password")
                self.status_label.configure(text="File encrypted successfully", text_color="green")
            except Exception as e:
                print(f"Error encrypting file: {e}")
        else:
            self.status_label.configure(text="No file selected", text_color="red")

if __name__ == "__main__":
    app = ctk.CTk()
    db_app = DB_App(app)
    app.mainloop()