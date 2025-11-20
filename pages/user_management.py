
import customtkinter as ctk
import os
from tkinter import messagebox
from PIL import Image
from db_manager import get_all_users, get_user_by_id, update_user, delete_user_and_history

def cut_text(text, limit):
    if text is None:
        return "-"
    text = str(text)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."

# ---------------------------
# HALAMAN: USER MANAGEMENT (Daftar)
# ---------------------------
class UserManagementPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="gray17")
        self.controller = controller

        # Pagination & state
        self.page = 1
        self.page_size = 15
        self.total_items = 0

        # Column widths
        self.COL_WIDTH = {
            "id": 70,
            "nama": 360,
            "nrp": 160,
            "username": 200,
            "aksi": 100
        }

        # layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # header
        self._setup_header()

        # table area
        self._setup_table_frame()

        # pagination
        self._setup_pagination_controls()

        self.data_rows = []

    def _setup_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12,6))
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header_frame, text="Manajemen User", font=self.controller.FONT_JUDUL, text_color="#1e90ff").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header_frame, text="Kelola akun terdaftar", font=self.controller.FONT_SUBJUDUL).grid(row=1, column=0, sticky="w", pady=(2,0))

    def _setup_table_frame(self):
        self.table_outer = ctk.CTkFrame(self, fg_color="gray15")
        self.table_outer.grid(row=1, column=0, sticky="nsew", padx=12, pady=(6,6))
        self.table_outer.grid_columnconfigure(0, weight=1)
        self.table_outer.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self.table_outer, fg_color="gray20", height=36)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure((0,1,2,3,4), weight=1)

        titles = [("No", self.COL_WIDTH["id"]),
                  ("Nama Lengkap", self.COL_WIDTH["nama"]),
                  ("NRP", self.COL_WIDTH["nrp"]),
                  ("Username", self.COL_WIDTH["username"]),
                  ("Aksi", self.COL_WIDTH["aksi"])]
        for idx, (txt, w) in enumerate(titles):
            lbl = ctk.CTkLabel(header, text=txt, font=self.controller.FONT_SUBJUDUL, anchor="center")
            lbl.grid(row=0, column=idx, padx=4, pady=6, sticky="nsew")
            lbl.configure(width=w)

        # Scrollable area for rows
        self.scroll_area = ctk.CTkScrollableFrame(self.table_outer, fg_color="gray15", height=500)
        self.scroll_area.grid(row=1, column=0, sticky="nsew", pady=(6,6))
        self.scroll_area.grid_columnconfigure(0, weight=1)

        self.rows_container = ctk.CTkFrame(self.scroll_area, fg_color="transparent")
        self.rows_container.grid(row=0, column=0, sticky="nsew")
        self.rows_container.grid_columnconfigure(0, weight=1)

    def _setup_pagination_controls(self):
        pag_frame = ctk.CTkFrame(self, fg_color="transparent")
        pag_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(0,12))
        pag_frame.grid_columnconfigure(1, weight=1)

        self.btn_prev = ctk.CTkButton(pag_frame, text="◀ Sebelumnya", width=90, command=self.prev_page)
        self.btn_prev.grid(row=0, column=0, padx=(0,8))

        self.page_label = ctk.CTkLabel(pag_frame, text=f"Halaman {self.page}", font=self.controller.FONT_UTAMA)
        self.page_label.grid(row=0, column=1)

        self.btn_next = ctk.CTkButton(pag_frame, text="Selanjutnya ▶", width=90, command=self.next_page)
        self.btn_next.grid(row=0, column=2, padx=(8,0))

    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.refresh_data()

    def next_page(self):
        if self.page * self.page_size < self.total_items:
            self.page += 1
            self.refresh_data()

    def _clear_rows(self):
        for r in self.data_rows:
            try:
                r.destroy()
            except:
                pass
        self.data_rows = []

    def refresh_data(self, *args):
        self._clear_rows()

        try:
            raw = get_all_users()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data user: {e}")
            raw = []

        self.total_items = len(raw)
        start = (self.page - 1) * self.page_size
        end = start + self.page_size
        page_data = raw[start:end]

        self.page_label.configure(text=f"Halaman {self.page}, Total User: {self.total_items}")
        self.btn_prev.configure(state="normal" if self.page > 1 else "disabled")
        self.btn_next.configure(state="normal" if self.page * self.page_size < self.total_items else "disabled")

        for i, u in enumerate(page_data):
            bg_color = "gray18" if (i % 2 == 0) else "gray17"
            row_frame = ctk.CTkFrame(self.rows_container, fg_color=bg_color, height=42, corner_radius=4)
            row_frame.grid(row=i, column=0, sticky="ew", padx=(4,4), pady=(2,2))
            row_frame.grid_columnconfigure((0,1,2,3,4), weight=1)

            underline = ctk.CTkFrame(row_frame, fg_color="gray12", height=1)
            underline.grid(row=1, column=0, columnspan=5, sticky="ew", pady=(0,0))
            underline.grid_rowconfigure(0, weight=0)

            def on_enter(e, f=row_frame):
                f.configure(fg_color="gray25")
            def on_leave(e, f=row_frame, orig=bg_color):
                f.configure(fg_color=orig)
            row_frame.bind("<Enter>", on_enter)
            row_frame.bind("<Leave>", on_leave)

            nomor_urut = start + i + 1
            lbl_no = ctk.CTkLabel(row_frame, text=str(nomor_urut), font=self.controller.FONT_UTAMA)
            lbl_no.grid(row=0, column=0, sticky="w", padx=(8,4))
            lbl_no.configure(width=self.COL_WIDTH["id"])

            lbl_name = ctk.CTkLabel(row_frame, text=cut_text(u.get("full_name") or "-", 40), font=ctk.CTkFont(family="Arial", size=13, weight="bold"), anchor="w")
            lbl_name.grid(row=0, column=1, sticky="w", padx=(6,4))
            lbl_name.configure(width=self.COL_WIDTH["nama"], wraplength=self.COL_WIDTH["nama"])

            lbl_nrp = ctk.CTkLabel(row_frame, text=cut_text(u.get("nrp") or "-", 18), font=self.controller.FONT_UTAMA)
            lbl_nrp.grid(row=0, column=2, sticky="w", padx=4)
            lbl_nrp.configure(width=self.COL_WIDTH["nrp"])

            lbl_user = ctk.CTkLabel(row_frame, text=cut_text(u.get("username") or "-", 18), font=self.controller.FONT_UTAMA)
            lbl_user.grid(row=0, column=3, sticky="w", padx=4)
            lbl_user.configure(width=self.COL_WIDTH["username"])

            action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            action_frame.grid(row=0, column=4, sticky="w", padx=(4,8))

            icon_eye = None
            try:
                eye_img_path = os.path.join("icons", "eye.png")
                if os.path.exists(eye_img_path):
                    pil = Image.open(eye_img_path)
                    icon_eye = ctk.CTkImage(light_image=pil, dark_image=pil, size=(18,18))
            except Exception:
                icon_eye = None

            # only eye button as requested; clicking navigates to detail frame within this file
            btn_view = ctk.CTkButton(action_frame, text="", width=36, height=28, image=icon_eye, fg_color="#1f6aa5", hover_color="#18537a", command=lambda uid=u['id']: self.show_detail(uid))
            btn_view.pack(side="right", padx=4)

            self.data_rows.append(row_frame)

    def show_detail(self, user_id):
        # navigate to detail page within controller, pass data dict
        try:
            data = get_user_by_id(user_id)
            if data is None:
                messagebox.showerror("Error", "User tidak ditemukan.")
                return
            self.controller.show_frame("UserDetail", data)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menampilkan detail: {e}")


# ---------------------------
# HALAMAN: USER DETAIL (di dalam file yang sama)
# ---------------------------
class UserDetailPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="gray17")
        self.controller = controller
        self.user_id = None
        self.user_data = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20,10))
        header_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(header_frame, text="Detail User", font=self.controller.FONT_JUDUL)
        self.title_label.grid(row=0, column=0, sticky="w")

        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.grid(row=0, column=1, sticky="e")

        self.btn_edit = ctk.CTkButton(action_frame, text="Edit Data", command=self.enter_edit, fg_color="gray40", hover_color="gray25", width=90)
        self.btn_edit.pack(side="left", padx=6)
        self.btn_delete = ctk.CTkButton(action_frame, text="Hapus", command=self._delete, fg_color="#cc3300", hover_color="#992600", width=90)
        self.btn_delete.pack(side="left", padx=6)
        self.btn_back = ctk.CTkButton(action_frame, text="Kembali", command=lambda: self.controller.show_frame("UserManagement"), width=90)
        self.btn_back.pack(side="left", padx=6)

        # Content area
        self.content_frame = ctk.CTkFrame(self, fg_color="gray15")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=12)
        self.content_frame.grid_columnconfigure((0,1), weight=1)

        # left info panel
        self._setup_info_panel(self.content_frame, 0)
        # right panel (could be for metadata)
        self._setup_meta_panel(self.content_frame, 1)

    def _setup_info_panel(self, parent, col):
        info_panel = ctk.CTkFrame(parent, fg_color="transparent")
        info_panel.grid(row=0, column=col, sticky="nwe", padx=30, pady=20)

        ctk.CTkLabel(info_panel, text="Data Akun:", font=self.controller.FONT_SUBJUDUL, text_color="#1f6aa5").pack(fill="x", pady=(0,10))

        ctk.CTkLabel(info_panel, text="Nama Lengkap:", font=self.controller.FONT_UTAMA, anchor="w").pack(fill="x", pady=(5,0))
        self.lbl_full = ctk.CTkLabel(info_panel, text="-", font=self.controller.FONT_UTAMA, anchor="w")
        self.lbl_full.pack(fill="x", pady=(0,10))

        ctk.CTkLabel(info_panel, text="NRP:", font=self.controller.FONT_UTAMA, anchor="w").pack(fill="x", pady=(5,0))
        self.lbl_nrp = ctk.CTkLabel(info_panel, text="-", font=self.controller.FONT_UTAMA, anchor="w")
        self.lbl_nrp.pack(fill="x", pady=(0,10))

        ctk.CTkLabel(info_panel, text="No HP:", font=self.controller.FONT_UTAMA, anchor="w").pack(fill="x", pady=(5,0))
        self.lbl_nohp = ctk.CTkLabel(info_panel, text="-", font=self.controller.FONT_UTAMA, anchor="w")
        self.lbl_nohp.pack(fill="x", pady=(0,10))

        ctk.CTkLabel(info_panel, text="Username:", font=self.controller.FONT_UTAMA, anchor="w").pack(fill="x", pady=(5,0))
        self.lbl_user = ctk.CTkLabel(info_panel, text="-", font=self.controller.FONT_UTAMA, anchor="w")
        self.lbl_user.pack(fill="x", pady=(0,10))

        ctk.CTkLabel(info_panel, text="Email:", font=self.controller.FONT_UTAMA, anchor="w").pack(fill="x", pady=(5,0))
        self.lbl_email = ctk.CTkLabel(info_panel, text="-", font=self.controller.FONT_UTAMA, anchor="w")
        self.lbl_email.pack(fill="x", pady=(0,10))

        ctk.CTkLabel(info_panel, text="Jabatan:", font=self.controller.FONT_UTAMA, anchor="w").pack(fill="x", pady=(5,0))
        self.lbl_jabatan = ctk.CTkLabel(info_panel, text="-", font=self.controller.FONT_UTAMA, anchor="w")
        self.lbl_jabatan.pack(fill="x", pady=(0,10))

        ctk.CTkLabel(info_panel, text="Nomor HP:", font=self.controller.FONT_UTAMA, anchor="w").pack(fill="x", pady=(5,0))
        self.lbl_hp = ctk.CTkLabel(info_panel, text="-", font=self.controller.FONT_UTAMA, anchor="w")
        self.lbl_hp.pack(fill="x", pady=(0,10))

    def _setup_meta_panel(self, parent, col):
        meta_panel = ctk.CTkFrame(parent, fg_color="transparent")
        meta_panel.grid(row=0, column=col, sticky="nwe", padx=30, pady=20)
        ctk.CTkLabel(meta_panel, text="Metadata:", font=self.controller.FONT_SUBJUDUL, text_color="#1f6aa5").pack(fill="x", pady=(0,10))

        ctk.CTkLabel(meta_panel, text="Dibuat pada:", font=self.controller.FONT_UTAMA, anchor="w").pack(fill="x", pady=(5,0))
        self.lbl_created = ctk.CTkLabel(meta_panel, text="-", font=self.controller.FONT_UTAMA, anchor="w")
        self.lbl_created.pack(fill="x", pady=(0,10))

    def load_data(self, data):
        # data is a dict containing user info (id, username, full_name, nrp, jabatan, nomor_hp, email, created_at)
        self.user_id = data.get("id")
        self.user_data = data
        self._render()

    def _render(self):
        m = self.user_data or {}
        self.lbl_full.configure(text=m.get("full_name") or "-")
        self.lbl_nrp.configure(text=m.get("nrp") or "-")
        self.lbl_nohp.configure(text=m.get("nomor_hp") or "-")
        self.lbl_user.configure(text=m.get("username") or "-")
        self.lbl_email.configure(text=m.get("email") or "-")
        self.lbl_jabatan.configure(text=m.get("jabatan") or "-")
        self.lbl_hp.configure(text=m.get("nomor_hp") or "-")
        self.lbl_created.configure(text=m.get("created_at") or "-")

    def enter_edit(self):
        # navigate to edit page within same file
        try:
            self.controller.show_frame("UserEdit", data={"id": self.user_id})
        except Exception:
            pass

    def _delete(self):
        if not self.user_id:
            return
        if messagebox.askyesno("Konfirmasi Hapus", "Hapus user ini dan semua data yang pernah diinputkan?"):
            ok = delete_user_and_history(self.user_id)
            if ok:
                messagebox.showinfo("Sukses", "User dan data terkait dihapus.")
                self.controller.show_frame("UserManagement")
            else:
                messagebox.showerror("Gagal", "Gagal menghapus user.")

# ---------------------------
# HALAMAN: USER EDIT (di file yang sama)
# ---------------------------
class UserEditPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="gray17")
        self.controller = controller
        self.record_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Edit Data User", font=controller.FONT_JUDUL).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.edit_card = ctk.CTkFrame(self, fg_color="gray15", corner_radius=10)
        self.edit_card.grid(row=1, column=0, padx=20, pady=10, sticky="nwe")
        self.edit_card.grid_columnconfigure(0, weight=1)

        self._setup_edit_form()

    def _setup_edit_form(self):
        controller = self.controller

        # Nama Lengkap
        ctk.CTkLabel(self.edit_card, text="Nama Lengkap:", font=controller.FONT_UTAMA, anchor="w").grid(row=0, column=0, padx=30, pady=(20, 0), sticky="ew")
        self.entry_full = ctk.CTkEntry(self.edit_card, font=controller.FONT_UTAMA)
        self.entry_full.grid(row=1, column=0, padx=30, pady=(5, 10), sticky="ew")

        # NRP
        ctk.CTkLabel(self.edit_card, text="NRP:", font=controller.FONT_UTAMA, anchor="w").grid(row=2, column=0, padx=30, pady=(10, 0), sticky="ew")
        self.entry_nrp = ctk.CTkEntry(self.edit_card, font=controller.FONT_UTAMA)
        self.entry_nrp.grid(row=3, column=0, padx=30, pady=(5, 10), sticky="ew")

        # Email
        ctk.CTkLabel(self.edit_card, text="Email:", font=controller.FONT_UTAMA, anchor="w").grid(row=4, column=0, padx=30, pady=(10, 0), sticky="ew")
        self.entry_email = ctk.CTkEntry(self.edit_card, font=controller.FONT_UTAMA)
        self.entry_email.grid(row=5, column=0, padx=30, pady=(5, 10), sticky="ew")

        # Jabatan
        ctk.CTkLabel(self.edit_card, text="Jabatan:", font=controller.FONT_UTAMA, anchor="w").grid(row=6, column=0, padx=30, pady=(10, 0), sticky="ew")
        self.entry_jabatan = ctk.CTkEntry(self.edit_card, font=controller.FONT_UTAMA)
        self.entry_jabatan.grid(row=7, column=0, padx=30, pady=(5, 20), sticky="ew")

        # Nomor HP
        ctk.CTkLabel(self.edit_card, text="Nomor HP:", font=controller.FONT_UTAMA, anchor="w").grid(row=8, column=0, padx=30, pady=(10, 0), sticky="ew")
        self.entry_hp = ctk.CTkEntry(self.edit_card, font=controller.FONT_UTAMA)
        self.entry_hp.grid(row=9, column=0, padx=30, pady=(5, 10), sticky="ew")

        # Action buttons
        action_frame = ctk.CTkFrame(self.edit_card, fg_color="transparent")
        action_frame.grid(row=10, column=0, padx=30, pady=30, sticky="e")

        btn_simpan = ctk.CTkButton(action_frame, text="Simpan Perubahan", command=self.save_changes, height=40, fg_color="#1f6aa5", hover_color="#18537a")
        btn_simpan.pack(side="left", padx=10)

        btn_batal = ctk.CTkButton(action_frame, text="Batal", command=lambda: self.controller.show_frame("UserDetail", data={"id": self.record_id}), height=40, fg_color="gray40", hover_color="gray25")
        btn_batal.pack(side="left")

    def load_data(self, data_dict):
        self.record_id = data_dict.get("id")
        data = get_user_by_id(self.record_id)
        if not data:
            messagebox.showerror("Error", "User tidak ditemukan.")
            self.controller.show_frame("UserManagement")
            return
        # fill entries
        self.entry_full.delete(0, ctk.END)
        self.entry_full.insert(0, data.get("full_name") or "")
        self.entry_nrp.delete(0, ctk.END)
        self.entry_nrp.insert(0, data.get("nrp") or "")
        self.entry_email.delete(0, ctk.END)
        self.entry_email.insert(0, data.get("email") or "")
        self.entry_jabatan.delete(0, ctk.END)
        self.entry_jabatan.insert(0, data.get("jabatan") or "")
        self.entry_hp.delete(0, ctk.END)
        self.entry_hp.insert(0, data.get("nomor_hp") or "")

    def save_changes(self):
        if not self.record_id:
            return
        ok = update_user(self.record_id,
                         full_name=self.entry_full.get().strip(),
                         nrp=self.entry_nrp.get().strip(),
                         jabatan=self.entry_jabatan.get().strip(),
                         email=self.entry_email.get().strip(),
                         nomor_hp=self.entry_hp.get().strip())
        if ok:
            messagebox.showinfo("Sukses", "Perubahan disimpan.")
            self.controller.show_frame("UserDetail", data={"id": self.record_id})
        else:
            messagebox.showerror("Gagal", "Gagal menyimpan perubahan.")
