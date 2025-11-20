
import customtkinter as ctk
from tkinter import messagebox
from db_manager import register_user

REGISTER_KEY_REQUIRED = "siidentregisterakunfindminutiae"

class RegisterPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        scroll = ctk.CTkScrollableFrame(self, width=500, height=650, corner_radius=0, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        scroll.grid_columnconfigure(0, weight=1)
        self.controller = controller

        # Layout grid like login page
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Card (centered)
        card = ctk.CTkFrame(scroll, width=420, height=620, corner_radius=12, fg_color="gray15")
        card.grid(row=0, column=0, padx=20, pady=20)
        card.grid_columnconfigure(0, weight=1)

        # Title (blue) and subtitle (white)
        title = ctk.CTkLabel(card, text="Sistem Ekstraksi Minutiae", font=controller.FONT_JUDUL, text_color="#1e90ff")
        title.grid(row=0, column=0, pady=(24, 4))

        subtitle = ctk.CTkLabel(card, text="Register Akun", font=controller.FONT_SUBJUDUL, text_color="white")
        subtitle.grid(row=1, column=0, pady=(0, 12))

        # Form frame with labels above entries
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.grid(row=2, column=0, padx=24, pady=(6, 6), sticky="nsew")
        form.grid_columnconfigure(0, weight=1)

        # Helper to create label + entry (label on top)
        def add_field(row, label_text, placeholder="", show=None):
            lbl = ctk.CTkLabel(form, text=label_text, anchor="w")
            lbl.grid(row=row*2, column=0, sticky="w", pady=(8, 4))
            ent = ctk.CTkEntry(form, placeholder_text=placeholder, show=show)
            ent.grid(row=row*2+1, column=0, sticky="ew", ipady=6)
            return ent

        idx = 0
        self.fullname_entry = add_field(idx, "Nama Lengkap:", "Masukkan nama lengkap"); idx += 1
        self.nrp_entry = add_field(idx, "Pangkat:", "Masukkan nrp"); idx += 1
        self.jabatan_entry = add_field(idx, "Jabatan:", "Masukkan jabatan"); idx += 1
        self.nomor_entry = add_field(idx, "Nomor HP:", "Masukkan nomor HP"); idx += 1
        self.email_entry = add_field(idx, "Email:", "Masukkan email"); idx += 1
        self.username_entry = add_field(idx, "Username:", "Masukkan username"); idx += 1
        self.password_entry = add_field(idx, "Password:", "Masukkan password", show="*"); idx += 1
        self.confirm_entry = add_field(idx, "Confirm Password:", "Masukkan konfirmasi password", show="*"); idx += 1
        self.regkey_entry = add_field(idx, "Register_Key:", "Masukkan Register Key"); idx += 1

        # Message label
        self.message = ctk.CTkLabel(card, text="", anchor="w")
        self.message.grid(row=3, column=0, padx=24, pady=(6,0), sticky="w")

        # Buttons: Register (blue) and Masuk Akun (grey, like login)
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=4, column=0, pady=18, padx=24, sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        register_btn = ctk.CTkButton(btn_frame, text="REGISTER", width=200, height=40, command=self.on_register)
        register_btn.grid(row=0, column=0, padx=(0,8), sticky="ew")

        masuk_btn = ctk.CTkButton(btn_frame, text="MASUK AKUN", width=200, height=40, fg_color="gray30", hover_color="gray35", command=self.go_login)
        masuk_btn.grid(row=0, column=1, padx=(8,0), sticky="ew")

        # Make register button stand out as blue by setting default color theme
        # (customtkinter uses default color theme; rely on theme to show primary button as blue)

    def go_login(self):
        try:
            self.controller.show_frame("Login")
        except Exception:
            self.controller.show_frame("Login")

    def on_register(self):
        nama = self.fullname_entry.get().strip()
        nrp = self.nrp_entry.get().strip()
        jabatan = self.jabatan_entry.get().strip()
        nomor = self.nomor_entry.get().strip()
        email = self.email_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        reg_key = self.regkey_entry.get().strip()

        # Basic validation
        if not all([nama, nrp, jabatan, nomor, email, username, password, confirm, reg_key]):
            self.message.configure(text="Semua kolom harus diisi!")
            return

        if password != confirm:
            self.message.configure(text="Password dan Konfirmasi tidak cocok.")
            return

        if reg_key != REGISTER_KEY_REQUIRED:
            self.message.configure(text="Register_Key salah. Tidak bisa mendaftar.")
            return

        # Call register_user to save into DB (we updated db_manager to accept these fields)
        success = register_user(username=username, password=password,
                                full_name=nama, nrp=nrp, jabatan=jabatan,
                                nomor_hp=nomor, email=email)
        if success:
            messagebox.showinfo("Sukses", "Pendaftaran berhasil. Silakan login.")
            # Clear form
            for e in [self.fullname_entry, self.nrp_entry, self.jabatan_entry,
                      self.nomor_entry, self.email_entry, self.username_entry,
                      self.password_entry, self.confirm_entry, self.regkey_entry]:
                e.delete(0, ctk.END)
            self.go_login()
        else:
            self.message.configure(text="Username sudah digunakan. Pilih username lain.")
