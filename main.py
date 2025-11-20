import customtkinter as ctk
import os
from tkinter import messagebox

# Import modul yang sudah dipisahkan
from db_manager import init_db
from components.sidebar import Sidebar
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.cari_minutiae import CariMinutiaePage, HasilEkstraksiPage
from pages.riwayat_page import RiwayatPencarianPage, DetailPage, EditPage
from pages.register_page import RegisterPage
from pages.user_management import UserManagementPage, UserDetailPage, UserEditPage


# --- KONFIGURASI APLIKASI ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

APP_NAME = "Find Minutiae"
# Rasio 16:9 (HD)
WIDTH = 1280
HEIGHT = 720
ICON_PATH = "assets/icon.png"
DUMMY_IMAGE_PATH = "assets/fingerprint_dummy.jpg"

# Pastikan folder assets dan images ada
os.makedirs("images", exist_ok=True)
os.makedirs("assets", exist_ok=True) 

# --- FRAME UTAMA: APP (Controller) ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # INISIALISASI FONT
        self.FONT_UTAMA = ctk.CTkFont(family="Arial", size=14)
        self.FONT_JUDUL = ctk.CTkFont(family="Arial", size=20, weight="bold")
        self.FONT_SUBJUDUL = ctk.CTkFont(family="Arial", size=16, weight="bold")
        
        init_db() # Inisialisasi Database
        # --- TAMBAHAN: DAFTARKAN USER ADMIN PERTAMA (Jalankan hanya sekali!) ---
        from db_manager import register_user
        
        # Coba daftarkan user 'admin' dengan password '123'
        if register_user("admin", "123"):
            print("User 'admin' berhasil didaftarkan.")
        else:
            print("User 'admin' sudah ada atau gagal didaftarkan.")
        self.title(APP_NAME)
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Inisialisasi state aplikasi
        self.frames = {}
        self.current_sidebar = None
        self.current_frame = None
        self.logged_in_user_id = None 

        
        
        # Inisialisasi container frame
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.show_frame("Login")

    def show_frame(self, page_name, data=None):
        
        if page_name not in self.frames:
            # Peta Halaman: Membuat instance frame jika belum ada
            if page_name == "Login":
                frame = LoginPage(parent=self.container, controller=self)
            elif page_name == "Register":
                frame = RegisterPage(parent=self.container, controller=self)
            elif page_name == "Home":
                frame = HomePage(parent=self.container, controller=self)
            elif page_name == "CariMinutiae":
                frame = CariMinutiaePage(parent=self.container, controller=self)
            elif page_name == "HasilEkstraksi":
                frame = HasilEkstraksiPage(parent=self.container, controller=self)
            elif page_name == "RiwayatPencarian":
                frame = RiwayatPencarianPage(parent=self.container, controller=self)
            elif page_name == "DetailPage":
                frame = DetailPage(parent=self.container, controller=self)
            elif page_name == "EditPage":
                frame = EditPage(parent=self.container, controller=self)
            elif page_name == "UserManagement":
                frame = UserManagementPage(parent=self.container, controller=self)
            elif page_name == "UserDetail":
                frame = UserDetailPage(parent=self.container, controller=self)
            elif page_name == "UserEdit":
                frame = UserEditPage(parent=self.container, controller=self)
            else:
                return 
            
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        frame = self.frames[page_name]

        # Konfigurasi Sidebar dan Grid Utama
        if page_name not in ("Login", "Register") and getattr(self, "logged_in_user_id", None) is not None:
            if self.current_sidebar is None:
                self.current_sidebar = Sidebar(self, self)
                self.current_sidebar.grid(row=0, column=0, sticky="ns", padx=(10, 0), pady=10)
                
                # PERBAIKAN GRID WEIGHT UNTUK MENGHILANGKAN JARAK:
                self.grid_columnconfigure(0, weight=0) # Sidebar (Kolom 0) tidak perlu mengambil ruang tambahan (lebar tetap)
                self.grid_columnconfigure(1, weight=1) # Container/Dashboard (Kolom 1) ambil semua sisa ruang
            
            self.container.grid_forget()
            self.container.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
            
            self.current_sidebar.set_active(page_name.replace("Page", ""))
            
            # Memuat data jika halaman memiliki fungsi load_data/refresh_data
            if hasattr(frame, 'refresh_data'):
                 frame.refresh_data()
            if hasattr(frame, 'load_data') and data is not None:
                frame.load_data(data)
            
        else: # Halaman Login
            # Sembunyikan sidebar dan atur container agar menempati seluruh window
            if self.current_sidebar:
                self.current_sidebar.grid_forget()
                self.current_sidebar = None
                self.container.grid_forget()
                self.container.grid(row=0, column=0, sticky="nsew")
        
        self.current_frame = frame
        frame.tkraise() 

    def login_success(self, user_id):
        """Dipanggil setelah login berhasil."""
        self.logged_in_user_id = user_id
        print("[DEBUG] login_success: logged_in_user_id =", self.logged_in_user_id)

        # cek user dari DB
        try:
            from db_manager import get_user_by_id
            u = get_user_by_id(user_id)
            print("[DEBUG] login_success: user from db =", u)
        except Exception as e:
            print("[DEBUG] login_success: get_user_by_id error:", e)

        # refresh sidebar jika ada
        if self.current_sidebar:
            try:
                print("[DEBUG] login_success: refreshing sidebar")
                self.current_sidebar.refresh()
            except Exception as e:
                print("[DEBUG] login_success: sidebar.refresh() failed:", e)

        self.show_frame("Home")
        
        
    def logout(self):
        """Log out user dan kembali ke halaman login."""
        # Pindah ke Login dan hapus sidebar
        self.logged_in_user_id = None # Hapus ID user
        self.show_frame("Login")
        
        if self.current_sidebar:
            self.current_sidebar.grid_forget()
            self.current_sidebar = None
        
        messagebox.showinfo("Logout", "Anda telah berhasil logout.")


# --- Jalankan Aplikasi ---
if __name__ == "__main__":
    app = App()
    app.mainloop()