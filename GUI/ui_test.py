import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from datetime import datetime
from pymongo import MongoClient

from utilz.openssl_utils import encrypt_file_aes
from utilz.openssl_utils import encrypt_file_rsa
from utilz.openssl_utils import encrypt_file_hybrid

client = MongoClient("mongodb://localhost:27017/")
db = client["CryptoFileDB"]
files_collection = db["EncryptedFiles"]

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class EncryptorUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Criptare Fișier")
        self.geometry("600x400")

        self.input_file = None
        self.output_file = None

        self.select_input_btn = ctk.CTkButton(self, text="Selectează fișier", command=self.select_input_file)
        self.select_input_btn.pack(pady=10)

        self.select_output_btn = ctk.CTkButton(self, text="Selectează locația de ieșire", command=self.select_output_file)
        self.select_output_btn.pack(pady=10)

        self.algorithm_var = ctk.StringVar(value="AES")
        self.algorithm_menu = ctk.CTkOptionMenu(self, values=["AES", "RSA", "HYBRID"], variable=self.algorithm_var)
        self.algorithm_menu.pack(pady=10)

        self.encrypt_btn = ctk.CTkButton(self, text="Criptează", command=self.encrypt_file)
        self.encrypt_btn.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.pack(pady=10)

    def select_input_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.input_file = path
            self.status_label.configure(text=f"Fișier selectat: {os.path.basename(path)}")

    def select_output_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".enc", filetypes=[("Encrypted Files", "*.enc")])
        if path:
            self.output_file = path
            self.status_label.configure(text=f"Ieșire: {os.path.basename(path)}")

    def encrypt_file(self):
        if not self.input_file or not self.output_file:
            messagebox.showerror("Eroare", "Selectează fișierul de intrare și ieșire.")
            return

        algorithm = self.algorithm_var.get()
        try:
            if algorithm == "AES":
                result = encrypt_file_aes(self.input_file, self.output_file)
            elif algorithm == "RSA":
                result = encrypt_file_rsa(self.input_file, self.output_file)
            elif algorithm == "HYBRID":
                result = encrypt_file_hybrid(self.input_file, self.output_file)
            else:
                raise ValueError("Algoritm necunoscut.")

            self.save_metadata(result, algorithm)
            messagebox.showinfo("Succes", f"Fișier criptat cu {algorithm}!")
            self.status_label.configure(text=f"✅ Criptat: {os.path.basename(self.output_file)}")

        except Exception as e:
            messagebox.showerror("Eroare la criptare", str(e))

    def save_metadata(self, result, algorithm):
        name = os.path.basename(self.input_file)
        extension = os.path.splitext(name)[1]
        metadata = {
            "name": name,
            "path": self.output_file,
            "extension": extension,
            "encryptionType": algorithm,
            "algorithmName": result.get("algorithmName"),
            "executionTime": result.get("executionTime"),
            "memoryUsage": result.get("memoryUsage"),
            "uploadDate": datetime.now()
        }
        files_collection.insert_one(metadata)

if __name__ == "__main__":
    app = EncryptorUI()
    app.mainloop()
