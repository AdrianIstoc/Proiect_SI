import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from datetime import datetime
import time
import psutil
from bson.objectid import ObjectId

#project imports
from mongo import MongoDBConnection
from crud.crud_files import CRUDFiles
from crud.crud_keys import CRUDKeys
from crud.crut_performances import CRUDPerformances
from crud.raw_algorithm import CRUDAlgorithm
from utilz.openssl_utils import (
    calculate_hash,
    get_file_metadata,
    generate_rsa_keypair,
    encrypt_symmetric,
    decrypt_symmetric,
    encrypt_asymmetric,
    decrypt_asymmetric,
    encrypt_hybrid,
    decrypt_hybrid
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class EncryptorUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CryptoFile Manager")
        self.geometry("900x700")

        #connection to database
        self.db_connection = MongoDBConnection()
        self.alg_conn = CRUDAlgorithm(self.db_connection)
        self.key_conn = CRUDKeys(self.db_connection)
        self.fle_conn = CRUDFiles(self.db_connection)
        self.prf_conn = CRUDPerformances(self.db_connection)

        self.input_file = None
        self.output_file_encrypted = None
        self.output_file_decrypted = None

        #dynamic file paths for keys
        self.input_file_directory = None
        self.private_key_file = None
        self.public_key_file = None
        self.rsa_key_length = 2048 #standard

        self.tabview = ctk.CTkTabview(self, width=850, height=650)
        self.tabview.pack(pady=20, padx=20, fill="both", expand=True)

        self.encryption_tab = self.tabview.add("Criptare / Decriptare")
        self.data_history_tab = self.tabview.add("Istoric Date")

        self._setup_encryption_decryption_tab()
        self._setup_data_history_tab()

        self._reset_ui_fields()

    def _setup_encryption_decryption_tab(self):
        """Elementele UI pentru tab-ul de criptare/decriptare."""
        tab = self.encryption_tab

        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=0)
        tab.grid_rowconfigure(1, weight=0)
        tab.grid_rowconfigure(2, weight=0)
        tab.grid_rowconfigure(3, weight=0)
        tab.grid_rowconfigure(4, weight=0)
        tab.grid_rowconfigure(5, weight=0)
        tab.grid_rowconfigure(6, weight=1)

        self.input_file_frame = ctk.CTkFrame(tab)
        self.input_file_frame.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        self.input_file_frame.grid_columnconfigure(0, weight=1)
        self.input_file_label = ctk.CTkLabel(self.input_file_frame, text="Fisier de intrare: Niciun fisier selectat")
        self.input_file_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.select_input_btn = ctk.CTkButton(self.input_file_frame, text="Selecteaza Fisier", command=self.select_input_file)
        self.select_input_btn.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        self.output_enc_file_frame = ctk.CTkFrame(tab)
        self.output_enc_file_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        self.output_enc_file_frame.grid_columnconfigure(0, weight=1)
        self.output_enc_file_label = ctk.CTkLabel(self.output_enc_file_frame, text="Fisier criptat iesire: Niciun fisier selectat")
        self.output_enc_file_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.select_output_enc_btn = ctk.CTkButton(self.output_enc_file_frame, text="Locatie Iesire Criptare", command=self.select_output_file_encryption)
        self.select_output_enc_btn.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        self.output_dec_file_frame = ctk.CTkFrame(tab)
        self.output_dec_file_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        self.output_dec_file_frame.grid_columnconfigure(0, weight=1)
        self.output_dec_file_label = ctk.CTkLabel(self.output_dec_file_frame, text="Fisier decriptat iesire: Niciun fisier selectat")
        self.output_dec_file_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.select_output_dec_btn = ctk.CTkButton(self.output_dec_file_frame, text="Locatie Iesire Decriptare", command=self.select_output_file_decryption)
        self.select_output_dec_btn.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        self.algorithm_label = ctk.CTkLabel(tab, text="Selecteaza Algoritm:")
        self.algorithm_label.grid(row=3, column=0, pady=5, padx=10, sticky="w")
        self.algorithm_var = ctk.StringVar(value="AES")
        self.algorithm_menu = ctk.CTkOptionMenu(tab, values=["AES", "RSA", "HYBRID"], variable=self.algorithm_var,
                                                command=self._on_algorithm_change)
        self.algorithm_menu.grid(row=3, column=1, pady=5, padx=10, sticky="ew")

        self.aes_password_label = ctk.CTkLabel(tab, text="Parola AES:")
        self.aes_password_label.grid(row=4, column=0, pady=5, padx=10, sticky="w")
        self.aes_password_entry = ctk.CTkEntry(tab, placeholder_text="Introdu parola pentru AES")
        self.aes_password_entry.grid(row=4, column=1, pady=5, padx=10, sticky="ew")
        self.aes_password_label.grid_remove()
        self.aes_password_entry.grid_remove()

        self.encrypt_btn = ctk.CTkButton(tab, text="Cripteaza Fisier", command=self.encrypt_file)
        self.encrypt_btn.grid(row=5, column=0, pady=20, padx=10, sticky="ew")

        self.decrypt_btn = ctk.CTkButton(tab, text="Decripteaza Fisier", command=self.decrypt_file)
        self.decrypt_btn.grid(row=5, column=1, pady=20, padx=10, sticky="ew")

        self.status_label = ctk.CTkLabel(tab, text="", wraplength=800)
        self.status_label.grid(row=6, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        self._on_algorithm_change("AES")

    def _setup_data_history_tab(self):
        """Elementele UI pentru tab-ul de istoric date."""
        tab = self.data_history_tab
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=0)
        tab.grid_rowconfigure(1, weight=1)

        self.refresh_data_btn = ctk.CTkButton(tab, text="Reactualizeaza Datele", command=self.view_stored_data)
        self.refresh_data_btn.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

        self.scrollable_data_frame = ctk.CTkScrollableFrame(tab)
        self.scrollable_data_frame.grid(row=1, column=0, pady=10, padx=10, sticky="nsew")
        self.scrollable_data_frame.grid_columnconfigure(0, weight=1)


    def _reset_ui_fields(self):
        """Resetarea campurilor UI la starea initiala."""
        self.input_file = None
        self.output_file_encrypted = None
        self.output_file_decrypted = None
        self.input_file_directory = None 
        self.private_key_file = None 
        self.public_key_file = None

        self.input_file_label.configure(text="Fisier de intrare: Niciun fisier selectat")
        self.output_enc_file_label.configure(text="Fisier criptat iesire: Niciun fisier selectat")
        self.output_dec_file_label.configure(text="Fisier decriptat iesire: Niciun fisier selectat")
        self.status_label.configure(text="")
        self.aes_password_entry.delete(0, ctk.END)
        self.algorithm_var.set("AES")
        self._on_algorithm_change("AES")

        for widget in self.scrollable_data_frame.winfo_children():
            widget.destroy()


    def _on_algorithm_change(self, algorithm_name):
        """In functie de algortim, afiseaza campul de parola pentru AES sau nu."""
        if algorithm_name == "AES":
            self.aes_password_label.grid()
            self.aes_password_entry.grid()
        else:
            self.aes_password_label.grid_remove()
            self.aes_password_entry.grid_remove()

    def select_input_file(self):
        """Selectarea fisierului de intrare."""
        path = filedialog.askopenfilename()
        if path:
            self.input_file = path
            self.input_file_label.configure(text=f"Fisier de intrare: {os.path.basename(path)}")
            self.status_label.configure(text=f"Fisier selectat: {os.path.basename(path)}")

            self.input_file_directory = os.path.dirname(path)
            self.private_key_file = os.path.join(self.input_file_directory, "private.pem")
            self.public_key_file = os.path.join(self.input_file_directory, "public.pem")

    def select_output_file_encryption(self):
        """Selectarea fisierului de iesire."""
        path = filedialog.asksaveasfilename(defaultextension=".enc", filetypes=[("Encrypted Files", "*.enc"), ("All Files", "*.*")])
        if path:
            self.output_file_encrypted = path
            self.output_enc_file_label.configure(text=f"Fisier criptat iesire: {os.path.basename(path)}")
            self.status_label.configure(text=f"Locatie iesire criptare: {os.path.basename(path)}")

    def select_output_file_decryption(self):
        """Selectarea fisierului de intrare pentru decriptare."""
        path = filedialog.asksaveasfilename(defaultextension="", filetypes=[("All Files", "*.*")])
        if path:
            self.output_file_decrypted = path
            self.output_dec_file_label.configure(text=f"Fisier decriptat iesire: {os.path.basename(path)}")
            self.status_label.configure(text=f"Locatie iesire decriptare: {os.path.basename(path)}")

    def encrypt_file(self):
        """Exceptii posibile."""
        if not self.input_file:
            messagebox.showerror("Eroare", "Selecteaza fisierul de intrare pentru criptare.")
            return
        if not self.input_file_directory:
            messagebox.showerror("Eroare", "Directorul fisierului de intrare nu a fost stabilit. Selecteaza un fisier.")
            return
        if not self.output_file_encrypted:
            messagebox.showerror("Eroare", "Selecteaza locatia de iesire pentru fisierul criptat.")
            return


        algorithm = self.algorithm_var.get()
        algorithm_name = ""
        key_length_bits = None
        alg_id = None
        key_id = None

        process = psutil.Process(os.getpid())
        start_time = time.perf_counter()
        mem_before = process.memory_info().rss

        try:
            hash_original = calculate_hash(self.input_file)
            meta_original = get_file_metadata(self.input_file)
            file_size_bytes = meta_original["size"]

            if algorithm == "AES":
                password = self.aes_password_entry.get()
                if not password:
                    messagebox.showerror("Eroare", "Lipsa parolei pentru criptarea AES.")
                    return
                key_length_bits = 256
                algorithm_name = "AES-256-CBC"

                encrypt_symmetric(self.input_file, password, output_file=self.output_file_encrypted)

                alg_id = self.alg_conn.create_algorithm(algorithm_name, "symmetric", key_length_bits, mode="CBC")
                fle_id = self.fle_conn.create_file(
                    os.path.basename(self.input_file),
                    file_size_bytes,
                    self.output_file_encrypted,
                    alg_id,
                    None,
                    status="encrypted",
                    file_hash=hash_original
                )

            elif algorithm == "RSA":
                key_length_bits = self.rsa_key_length
                algorithm_name = "RSA"

                #generare de chei RSA in directorul fisierului de intrare
                if not os.path.exists(self.public_key_file) or not os.path.exists(self.private_key_file):
                    messagebox.showinfo("Generare Chei RSA", f"Generare pereche de chei RSA ({key_length_bits} biti: public.pem, private.pem) in directorul fisierului de intrare...")
                    generate_rsa_keypair(self.private_key_file, self.public_key_file, key_size=key_length_bits)
                    messagebox.showinfo("Generare Chei RSA", "Cheile RSA au fost generate.")

                #citirea cheilor din fisier
                with open(self.private_key_file, 'r') as f:
                    private_key_content = f.read()
                with open(self.public_key_file, 'r') as f:
                    public_key_content = f.read()

                alg_id = self.alg_conn.create_algorithm(algorithm_name, "asymmetric", key_length_bits)
                key_id = self.key_conn.create_key(alg_id, key_type="asymmetric",
                                                  public_key=public_key_content, private_key=private_key_content)

                encrypt_asymmetric(self.input_file, self.public_key_file, output_file=self.output_file_encrypted)

                fle_id = self.fle_conn.create_file(
                    os.path.basename(self.input_file),
                    file_size_bytes,
                    self.output_file_encrypted,
                    alg_id,
                    key_id,
                    status="encrypted",
                    file_hash=hash_original
                )

            elif algorithm == "HYBRID":
                key_length_bits = self.rsa_key_length
                algorithm_name = "HYBRID (AES+RSA)"

                #se verifica existenta cheilor RSA in directorul fisierului de intrare
                if not os.path.exists(self.public_key_file) or not os.path.exists(self.private_key_file):
                    messagebox.showinfo("Generare Chei RSA", f"Generare pereche de chei RSA ({key_length_bits} biți: public.pem, private.pem) în directorul fisierului de intrare...")
                    generate_rsa_keypair(self.private_key_file, self.public_key_file, key_size=key_length_bits)
                    messagebox.showinfo("Generare Chei RSA", "Cheile RSA au fost generate.")

                with open(self.private_key_file, 'r') as f:
                    private_key_content = f.read()
                with open(self.public_key_file, 'r') as f:
                    public_key_content = f.read()

                alg_id = self.alg_conn.create_algorithm("RSA", "asymmetric", key_length_bits)
                key_id = self.key_conn.create_key(alg_id, key_type="asymmetric",
                                                  public_key=public_key_content, private_key=private_key_content)
            
                encrypted_file, encrypted_key_file = encrypt_hybrid(
                    self.input_file,
                    self.public_key_file,
                    encrypted_file=self.output_file_encrypted
                )

                fle_id = self.fle_conn.create_file(
                    os.path.basename(self.input_file),
                    file_size_bytes,
                    encrypted_file,
                    alg_id,
                    key_id,
                    status="encrypted",
                    file_hash=hash_original
                )

            else:
                messagebox.showerror("Eroare", "Algoritm de criptare necunoscut sau neimplementat.")
                return

            #parametri de performanta
            end_time = time.perf_counter()
            mem_after = process.memory_info().rss
            execution_time = round(end_time - start_time, 3)
            memory_used = round((mem_after - mem_before) / (1024 * 1024), 2)

            self.prf_conn.create_performance(
                fle_id,
                alg_id,
                "encrypt",
                execution_time,
                memory_used,
                file_size_bytes
            )

            messagebox.showinfo("Succes", f"Fisier criptat cu {algorithm} in {execution_time} secunde.")
            self.status_label.configure(text=f"Criptat: {os.path.basename(self.output_file_encrypted)} (Timp: {execution_time}s, Memorie: {memory_used} MB)")

        except Exception as e:
            messagebox.showerror("Eroare la criptare", f"A aparut o eroare: {str(e)}")
            self.status_label.configure(text=f"Eroare la criptare: {str(e)}")

    def decrypt_file(self):
        """Decriptarea fisierului."""
        if not self.input_file:
            messagebox.showerror("Eroare", "Selecteaza fisierul criptat de intrare pentru decriptare.")
            return
        if not self.output_file_decrypted:
            messagebox.showerror("Eroare", "Selecteaza locatia de iesire pentru fisierul decriptat.")
            return
        
        if not self.input_file_directory:
            messagebox.showerror("Eroare", "Directorul fisierului criptat nu a fost stabilit. Te rog sa selectezi un fisier.")
            return

        algorithm = self.algorithm_var.get()

        process = psutil.Process(os.getpid())
        start_time = time.perf_counter()
        mem_before = process.memory_info().rss

        try:
            original_file_entry = self.fle_conn.get_collection().find_one({"encrypted_filename": self.input_file})
            if not original_file_entry:
                messagebox.showwarning("Avertisment", "Nu s-a gasit nicio inregistrare de criptare pentru acest fisier. Decriptarea va continua, dar performanta nu va fi legata de o inregistrare existenta si hash-ul nu poate fi verificat.")
                original_alg_id = None
                original_key_id = None
                hash_original = None
            else:
                original_alg_id = original_file_entry.get("algorithm_id")
                original_key_id = original_file_entry.get("key_id")
                hash_original = original_file_entry.get("file_hash")


            if algorithm == "AES":
                password = self.aes_password_entry.get()
                if not password:
                    messagebox.showerror("Eroare", "Introdu parola pentru decriptarea AES.")
                    return

                decrypt_symmetric(self.input_file, password, output_file=self.output_file_decrypted)

            elif algorithm == "RSA":            
                if not os.path.exists(self.private_key_file):
                    messagebox.showerror("Eroare", f"Cheia privata RSA ({os.path.basename(self.private_key_file)}) nu a fost gasita in directorul fisierului de intrare. Este necesara pentru decriptarea RSA.")
                    return
                
                decrypt_asymmetric(self.input_file, self.private_key_file, output_file=self.output_file_decrypted)

            elif algorithm == "HYBRID":
                encrypted_key_file = os.path.join(self.input_file_directory, "key.enc")
                if not os.path.exists(encrypted_key_file):
                    messagebox.showerror("Eroare", f"Fisierul cheii criptate ('key.enc') nu a fost gasit in directorul fisierului de intrare: {self.input_file_directory}. Asigura-te ca este prezent.")
                    return
                if not os.path.exists(self.private_key_file):
                    messagebox.showerror("Eroare", f"Cheia privata RSA ({os.path.basename(self.private_key_file)}) nu a fost gasita in directorul fisierului de intrare. Este necesara pentru decriptarea Hibrid.")
                    return
                
                decrypt_hybrid(self.input_file, encrypted_key_file, self.private_key_file, self.output_file_decrypted)

            else:
                messagebox.showerror("Eroare", "Algoritm de decriptare necunoscut sau neimplementat.")
                return

            end_time = time.perf_counter()
            mem_after = process.memory_info().rss
            execution_time = round(end_time - start_time, 3)
            memory_used = round((mem_after - mem_before) / (1024 * 1024), 2)

            meta_decrypted = get_file_metadata(self.output_file_decrypted)
            hash_decrypted = calculate_hash(self.output_file_decrypted)
            file_size_bytes_dec = meta_decrypted["size"]

            fle_dec_id = self.fle_conn.create_file(
                os.path.basename(self.output_file_decrypted),
                file_size_bytes_dec,
                self.output_file_decrypted,
                original_alg_id,
                original_key_id,
                status="decrypted",
                file_hash=hash_decrypted
            )

            self.prf_conn.create_performance(
                fle_dec_id,
                original_alg_id,
                "decrypt",
                execution_time,
                memory_used,
                file_size_bytes_dec
            )

            if hash_original and hash_original == hash_decrypted:
                messagebox.showinfo("Succes", f"Fisier decriptat cu {algorithm} si verificat! Hash-urile corespund.")
                self.status_label.configure(text=f"Decriptat si verificat: {os.path.basename(self.output_file_decrypted)} (Timp: {execution_time}s, Memorie: {memory_used} MB)")
            else:
                messagebox.showwarning("Atenție", f"Fisier decriptat cu {algorithm}. Hash-ul original nu a fost gasit sau nu corespunde.")
                self.status_label.configure(text=f"Decriptat: {os.path.basename(self.output_file_decrypted)} (Timp: {execution_time}s, Memorie: {memory_used} MB)")

        except Exception as e:
            messagebox.showerror("Eroare la decriptare", f"A aparut o eroare: {str(e)}")
            self.status_label.configure(text=f"Eroare la decriptare: {str(e)}")

    def view_stored_data(self):
        """Reformatare tab-ul de istoric date intr-o forma mai usor de citit."""
        for widget in self.scrollable_data_frame.winfo_children():
            widget.destroy()

        row_idx = 0

        def add_section_title(title):
            nonlocal row_idx
            ctk.CTkLabel(self.scrollable_data_frame, text=title, font=ctk.CTkFont(weight="bold", size=16), text_color="cyan").grid(row=row_idx, column=0, pady=(15, 5), sticky="w")
            row_idx += 1
            ctk.CTkFrame(self.scrollable_data_frame, height=2, fg_color="gray").grid(row=row_idx, column=0, sticky="ew", pady=(0,10))
            row_idx += 1

        def add_record(record_dict):
            nonlocal row_idx
            formatted_record = {k: str(v) if isinstance(v, ObjectId) or isinstance(v, datetime) else v for k, v in record_dict.items()}

            record_text = []
            for key, value in formatted_record.items():
                record_text.append(f"• {key}: {value}")

            ctk.CTkLabel(self.scrollable_data_frame, text="\n".join(record_text), justify="left", wraplength=780).grid(row=row_idx, column=0, padx=5, pady=2, sticky="ew")
            row_idx += 1
            ctk.CTkFrame(self.scrollable_data_frame, height=1, fg_color="darkgray").grid(row=row_idx, column=0, sticky="ew", pady=5)
            row_idx += 1

        add_section_title("Algoritmi:")
        algorithms = self.alg_conn.get_all_algorithms()
        if algorithms:
            for alg in algorithms:
                add_record(alg)
        else:
            ctk.CTkLabel(self.scrollable_data_frame, text="Niciun algoritm inregistrat.").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
            row_idx += 1

        add_section_title("Chei:")
        keys = self.key_conn.get_all_keys()
        if keys:
            for key in keys:
                display_key = {k: v for k, v in key.items() if k != "private_key"}
                add_record(display_key)
        else:
            ctk.CTkLabel(self.scrollable_data_frame, text="Nicio cheie inregistrata.").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
            row_idx += 1

        add_section_title("Fișiere:")
        files = self.fle_conn.get_all_files()
        if files:
            for f in files:
                add_record(f)
        else:
            ctk.CTkLabel(self.scrollable_data_frame, text="Niciun fisier inregistrat.").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
            row_idx += 1

        add_section_title("Performante:")
        performances = self.prf_conn.get_all_performances()
        if performances:
            for p in performances:
                add_record(p)
        else:
            ctk.CTkLabel(self.scrollable_data_frame, text="Nicio performanta inregistrata.").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
            row_idx += 1

if __name__ == "__main__":
    app = EncryptorUI()
    app.mainloop()