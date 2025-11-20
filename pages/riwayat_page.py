# riwayat_page.py
import customtkinter as ctk
import os
from tkinter import messagebox
from PIL import Image
from db_manager import get_history_data, fetch_history_by_id, update_history_data, delete_history

# ---------------------------
# Helper: potong teks dengan ellipsis
# ---------------------------
def cut_text(text, limit):
    if text is None:
        return "-"
    text = str(text)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."

# ===========================
# HALAMAN 4A: RIWAYAT PENCARIAN
# ===========================
class RiwayatPencarianPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="gray17")
        self.controller = controller

        # Pagination & state
        self.page = 1
        self.page_size = 15
        self.total_items = 0

        # Fixed column widths (pixel-like units)
        # NOTE: CTk width isn't a strict pixel in all setups, but this enforces consistent sizing
        self.COL_WIDTH = {
            "id": 70,
            "judul": 340,
            "lp": 140,
            "tanggal": 140,
            "tipe": 120,
            "aksi": 90
        }

        # layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # content area grows

        # header + filters
        self._setup_header()

        # table area (header + rows inside)
        self._setup_table_frame()

        # pagination controls
        self._setup_pagination_controls()

        # data rows container
        self.data_rows = []

    # ---------------- header & filters ----------------
    def _setup_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header_frame, text="Riwayat Pencarian Kasus", font=self.controller.FONT_JUDUL).grid(
            row=0, column=0, sticky="w"
        )

        control_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        control_frame.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(control_frame, text="Tampilkan:", font=self.controller.FONT_UTAMA).pack(side="left", padx=(0, 6))

        self.riwayat_mode = ctk.StringVar(value="Umum")
        ctk.CTkSegmentedButton(
            control_frame,
            variable=self.riwayat_mode,
            values=["Umum", "Lokal"],
            command=self._on_mode_change,
            font=self.controller.FONT_UTAMA
        ).pack(side="left")

    def _on_mode_change(self, *args):
        # reset page when filter changes
        self.page = 1
        self.refresh_data()

    # ---------------- table frame ----------------
    def _setup_table_frame(self):
        # Outer frame holds header and scroll area
        self.table_outer = ctk.CTkFrame(self, fg_color="gray15")
        self.table_outer.grid(row=1, column=0, sticky="nsew", padx=12, pady=(6, 6))
        self.table_outer.grid_columnconfigure(0, weight=1)
        self.table_outer.grid_rowconfigure(1, weight=1)

        # Table header row
        header = ctk.CTkFrame(self.table_outer, fg_color="gray20", height=36)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # Create header labels with fixed widths
        titles = [("No", self.COL_WIDTH["id"]),
                  ("Judul Kasus", self.COL_WIDTH["judul"]),
                  ("Nomor LP", self.COL_WIDTH["lp"]),
                  ("Tanggal", self.COL_WIDTH["tanggal"]),
                  ("Tipe", self.COL_WIDTH["tipe"]),
                  ("Aksi", self.COL_WIDTH["aksi"])]

        for idx, (txt, w) in enumerate(titles):
            lbl = ctk.CTkLabel(header, text=txt, font=self.controller.FONT_SUBJUDUL, anchor="center")
            lbl.grid(row=0, column=idx, padx=4, pady=6, sticky="nsew")
            lbl.configure(width=w)

        # Scrollable area for rows
        # Use CTkScrollableFrame so content can scroll when many rows
        self.scroll_area = ctk.CTkScrollableFrame(self.table_outer, fg_color="gray15", label_text="", corner_radius=6, height=500)
        self.scroll_area.grid(row=1, column=0, sticky="nsew", pady=(6, 6))
        self.scroll_area.grid_columnconfigure(0, weight=1)

        # Container: we'll place row frames inside this
        self.rows_container = ctk.CTkFrame(self.scroll_area, fg_color="transparent")
        self.rows_container.grid(row=0, column=0, sticky="nsew")
        self.rows_container.grid_columnconfigure(0, weight=1)

    # ---------------- pagination ----------------
    def _setup_pagination_controls(self):
        pag_frame = ctk.CTkFrame(self, fg_color="transparent")
        pag_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        pag_frame.grid_columnconfigure(1, weight=1)

        # left: prev button
        self.btn_prev = ctk.CTkButton(pag_frame, text="◀ Sebelumnya", width=90, command=self.prev_page)
        self.btn_prev.grid(row=0, column=0, padx=(0, 8))

        # center: page info
        self.page_label = ctk.CTkLabel(pag_frame, text=f"Halaman {self.page}", font=self.controller.FONT_UTAMA)
        self.page_label.grid(row=0, column=1)

        # right: next button
        self.btn_next = ctk.CTkButton(pag_frame, text="Selanjutnya ▶", width=90, command=self.next_page)
        self.btn_next.grid(row=0, column=2, padx=(8, 0))

    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.refresh_data()

    def next_page(self):
        if self.page * self.page_size < self.total_items:
            self.page += 1
            self.refresh_data()

    # ---------------- draw rows ----------------
    def _clear_rows(self):
        for r in self.data_rows:
            try:
                r.destroy()
            except:
                pass
        self.data_rows = []

    def refresh_data(self, *args):
        """
        Ambil data dari DB (get_history_data) lalu tampilkan slice berdasarkan pagination.
        Pastikan data selalu ditumpuk ulang (clear -> build).
        """
        self._clear_rows()

        # Ambil semua data (filter mode dapat diterapkan di db_manager jika perlu)
        # Jika kamu ingin filter "Lokal" vs "Umum" di sisi UI, tambahkan logika di sini
        try:
                    # Mode filter: 'Umum' => tampilkan semua, 'Lokal' => tampilkan hanya data user yang login
            mode = (self.riwayat_mode.get() or "Umum").lower()
            if mode == 'lokal' and getattr(self.controller, 'logged_in_user_id', None) is not None:
                raw = get_history_data(user_id=self.controller.logged_in_user_id)
            else:
                raw = get_history_data(user_id=None)

        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data riwayat: {e}")
            raw = []

        self.total_items = len(raw)
        # calculate slice
        start = (self.page - 1) * self.page_size
        end = start + self.page_size
        page_data = raw[start:end]

        # Update page label & prev/next active state
        self.page_label.configure(text=f"Halaman {self.page}, Total Keseluruhan Data: {self.total_items} Data")
        self.btn_prev.configure(state="normal" if self.page > 1 else "disabled")
        self.btn_next.configure(state="normal" if self.page * self.page_size < self.total_items else "disabled")

        # Build rows
        for i, row in enumerate(page_data):
            # expected row format: (row_id, judul, nomor_lp, tanggal, timestamp, username)
            try:
                row_id, judul, nomor_lp, tanggal, timestamp, username = row
            except Exception:
                # fallback if different structure
                # try to be robust: unpack minimal fields
                row_id = row[0] if len(row) > 0 else ""
                judul = row[1] if len(row) > 1 else ""
                nomor_lp = row[2] if len(row) > 2 else ""
                tanggal = row[3] if len(row) > 3 else ""
                username = row[5] if len(row) > 5 else ""

            # create row frame
            bg_color = "gray18" if (i % 2 == 0) else "gray17"
            row_frame = ctk.CTkFrame(self.rows_container, fg_color=bg_color, height=42, corner_radius=4)
            row_frame.grid(row=i, column=0, sticky="ew", padx=(4, 4), pady=(2, 2))
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

            # underline effect: a bottom border using a thin frame
            underline = ctk.CTkFrame(row_frame, fg_color="gray12", height=1)
            underline.grid(row=1, column=0, columnspan=6, sticky="ew", pady=(0, 0))
            underline.grid_rowconfigure(0, weight=0)

            # HOVER: change background on enter/leave
            def on_enter(e, f=row_frame):
                f.configure(fg_color="gray25")
            def on_leave(e, f=row_frame, orig=bg_color):
                f.configure(fg_color=orig)

            # bind enter/leave to row and to children to be reliable
            row_frame.bind("<Enter>", on_enter)
            row_frame.bind("<Leave>", on_leave)

            # Column 0: ID
            # Column 0: NO URUT (ganti ID di tabel)
            nomor_urut = start + i + 1
            lbl_id = ctk.CTkLabel(row_frame, text=str(nomor_urut), font=self.controller.FONT_UTAMA)
            lbl_id.grid(row=0, column=0, sticky="w", padx=(8, 4))
            lbl_id.configure(width=self.COL_WIDTH["id"])

            # Column 1: Judul (truncate)
            cut_judul = cut_text(judul or "-", 60)  # allow longer then shorten visually
            lbl_judul = ctk.CTkLabel(row_frame, text=cut_judul, font=ctk.CTkFont(family="Arial", size=13, weight="bold"), anchor="w")
            lbl_judul.grid(row=0, column=1, sticky="w", padx=(6, 4))
            lbl_judul.configure(width=self.COL_WIDTH["judul"], wraplength=self.COL_WIDTH["judul"])

            # Column 2: Nomor LP
            lbl_lp = ctk.CTkLabel(row_frame, text=cut_text(nomor_lp or "-", 24), font=self.controller.FONT_UTAMA)
            lbl_lp.grid(row=0, column=2, sticky="w", padx=4)
            lbl_lp.configure(width=self.COL_WIDTH["lp"])

            # Column 3: Tanggal
            lbl_tanggal = ctk.CTkLabel(row_frame, text=cut_text(tanggal or "-", 20), font=self.controller.FONT_UTAMA)
            lbl_tanggal.grid(row=0, column=3, sticky="w", padx=4)
            lbl_tanggal.configure(width=self.COL_WIDTH["tanggal"])

            # Column 4: Tipe / Username
            lbl_tipe = ctk.CTkLabel(row_frame, text=cut_text(username or "-", 18), font=self.controller.FONT_UTAMA)
            lbl_tipe.grid(row=0, column=4, sticky="w", padx=4)
            lbl_tipe.configure(width=self.COL_WIDTH["tipe"])

            # Column 5: Actions (Detail button with icon)
            action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            action_frame.grid(row=0, column=5, sticky="w", padx=(4, 8))

            # Try to load icon (if missing, button is text-only)
            icon_eye = None
            try:
                eye_img_path = os.path.join("icons", "eye.png")  # expected path
                if os.path.exists(eye_img_path):
                    pil = Image.open(eye_img_path)
                    icon_eye = ctk.CTkImage(light_image=pil, dark_image=pil, size=(18, 18))
            except Exception:
                icon_eye = None

            btn_detail = ctk.CTkButton(
                action_frame,
                text="",
                width=36,
                height=28,
                image=icon_eye,
                fg_color="#1f6aa5",
                hover_color="#18537a",
                command=lambda rid=row_id: self.show_detail(rid)
            )
            btn_detail.pack(side="right")

            # add to list to manage cleanup later
            self.data_rows.append(row_frame)

    # ---------------- navigation to detail ----------------
    def show_detail(self, row_id):
        # maintain API from original code: controller.show_frame("DetailPage", data={'id': row_id})
        self.controller.show_frame("DetailPage", data={'id': row_id})


# --- HALAMAN 4B: DETAIL RIWAYAT ---
class DetailPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="gray17")
        self.controller = controller
        self.record_id = None
        self.record_paths = {} # Menyimpan path mentah dan ekstraksi

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._setup_ui()
    
    def _setup_ui(self):
        # Header (Judul dan Tombol Aksi)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(header_frame, text="Detail Kasus:", font=self.controller.FONT_JUDUL)
        self.title_label.grid(row=0, column=0, sticky="w")
        
        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.grid(row=0, column=1, sticky="e")
        
        self.btn_edit = ctk.CTkButton(action_frame, text="Edit Data", command=self.go_to_edit, fg_color="gray40", hover_color="gray25", width=80)
        self.btn_edit.pack(side="left", padx=5)
        self.btn_delete = ctk.CTkButton(action_frame, text="Hapus", command=self.delete_record, fg_color="#cc3300", hover_color="#992600", width=80)
        self.btn_delete.pack(side="left", padx=5)
        self.btn_back = ctk.CTkButton(action_frame, text="Kembali", command=lambda: self.controller.show_frame("RiwayatPencarian"), width=80)
        self.btn_back.pack(side="left", padx=5)


        # Konten Utama
        self.content_frame = ctk.CTkFrame(self, fg_color="gray15")
        self.content_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.content_frame.grid_columnconfigure((0, 1), weight=1)
        
        self._setup_info_panel(self.content_frame, 0)
        self._setup_image_panel(self.content_frame, 1)

    def _setup_info_panel(self, parent, col):
        info_panel = ctk.CTkFrame(parent, fg_color="transparent")
        info_panel.grid(row=0, column=col, sticky="nwe", padx=30, pady=20)
        
        # Data Kasus
        ctk.CTkLabel(info_panel, text="Data Kasus:", font=self.controller.FONT_SUBJUDUL, text_color="#1f6aa5").pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(info_panel, text="ID Kasus:", font=self.controller.FONT_UTAMA, anchor="w").pack(fill="x", pady=(5, 0))
        self.lbl_id = ctk.CTkLabel(info_panel, text="", font=self.controller.FONT_UTAMA, anchor="w")
        self.lbl_id.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(info_panel, text="Judul Kasus:", font=self.controller.FONT_UTAMA, anchor="w").pack(fill="x", pady=(5, 0))
        self.lbl_judul = ctk.CTkLabel(info_panel, text="", font=ctk.CTkFont(family="Arial", size=14, weight="bold"), anchor="w", wraplength=400)
        self.lbl_judul.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(info_panel, text="Nomor LP:", font=self.controller.FONT_UTAMA, anchor="w").pack(fill="x", pady=(5, 0))
        self.lbl_lp = ctk.CTkLabel(info_panel, text="", font=self.controller.FONT_UTAMA, anchor="w")
        self.lbl_lp.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(info_panel, text="Tanggal Kejadian:", font=self.controller.FONT_UTAMA, anchor="w").pack(fill="x", pady=(5, 0))
        self.lbl_tanggal = ctk.CTkLabel(info_panel, text="", font=self.controller.FONT_UTAMA, anchor="w")
        self.lbl_tanggal.pack(fill="x", pady=(0, 20))
        
        # Path File
        ctk.CTkLabel(info_panel, text="Path File Mentah:", font=self.controller.FONT_UTAMA, anchor="w").pack(fill="x", pady=(5, 0))
        self.lbl_path_mentah = ctk.CTkLabel(info_panel, text="", font=self.controller.FONT_UTAMA, anchor="w", wraplength=400, text_color="gray")
        self.lbl_path_mentah.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(info_panel, text="Path File Ekstraksi:", font=self.controller.FONT_UTAMA, anchor="w").pack(fill="x", pady=(5, 0))
        self.lbl_path_ekstraksi = ctk.CTkLabel(info_panel, text="", font=self.controller.FONT_UTAMA, anchor="w", wraplength=400, text_color="gray")
        self.lbl_path_ekstraksi.pack(fill="x", pady=(0, 10))

    def _setup_image_panel(self, parent, col):
        image_panel = ctk.CTkFrame(parent, fg_color="transparent")
        image_panel.grid(row=0, column=col, sticky="nsew", padx=30, pady=20)
        image_panel.grid_rowconfigure(2, weight=1)
        image_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(image_panel, text="Visualisasi:", font=self.controller.FONT_SUBJUDUL, text_color="#1f6aa5").grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Image Type Selector
        type_frame = ctk.CTkFrame(image_panel, fg_color="transparent")
        type_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.image_type_var = ctk.StringVar(value="Mentah")
        self.radio_mentah = ctk.CTkRadioButton(type_frame, text="Mentah", variable=self.image_type_var, value="Mentah", command=self.display_image, font=self.controller.FONT_UTAMA)
        self.radio_mentah.pack(side="left", padx=10)
        self.radio_ekstraksi = ctk.CTkRadioButton(type_frame, text="Ekstraksi", variable=self.image_type_var, value="Ekstraksi", command=self.display_image, font=self.controller.FONT_UTAMA)
        self.radio_ekstraksi.pack(side="left", padx=10)

        # Image Holder
        self.image_holder = ctk.CTkLabel(image_panel, text="[Gambar]", corner_radius=10, fg_color="gray25")
        self.image_holder.grid(row=2, column=0, sticky="nsew")

    def load_data(self, data_dict):
        # Fungsi ini dipanggil oleh controller untuk memuat data spesifik
        self.record_id = data_dict['id']
        record = fetch_history_by_id(self.record_id)
        
        if record:
            self.title_label.configure(text=f"Detail Kasus ID: {self.record_id}")
            self.lbl_id.configure(text=self.record_id)
            self.lbl_judul.configure(text=record['judul_kasus'])
            self.lbl_lp.configure(text=record['nomor_lp'] if record['nomor_lp'] else "-")
            self.lbl_tanggal.configure(text=record['tanggal_kejadian'] if record['tanggal_kejadian'] else "-")
            self.lbl_path_mentah.configure(text=record['path_mentah'])
            self.lbl_path_ekstraksi.configure(text=record['path_ekstraksi'])
            
            self.record_paths = {
                "Mentah": record['path_mentah'],
                "Ekstraksi": record['path_ekstraksi']
            }
            # Tampilkan gambar awal (Mentah)
            self.image_type_var.set("Mentah")
            self.display_image()
        else:
             messagebox.showerror("Error", "Data kasus tidak ditemukan.")
             self.controller.show_frame("RiwayatPencarian")


    def display_image(self):
        img_type = self.image_type_var.get()
        img_path = self.record_paths.get(img_type)

        if not img_path or not os.path.exists(img_path):
            self.image_holder.configure(text=f"File {img_type} tidak ditemukan!", image=None)
            return

        try:
            original_image = Image.open(img_path)
            # Resize gambar agar sesuai
            original_image.thumbnail((450, 450))
            
            ctk_image = ctk.CTkImage(light_image=original_image, dark_image=original_image, size=original_image.size)
            
            self.image_holder.configure(text="", image=ctk_image)
            self.image_holder.image = ctk_image
        except Exception as e:
            self.image_holder.configure(text=f"Gagal memuat gambar: {e}", image=None)

    def go_to_edit(self):
        if self.record_id:
            self.controller.show_frame("EditPage", data={'id': self.record_id})

    def delete_record(self):
        if not self.record_id:
            return

        confirm = messagebox.askyesno(
            "Konfirmasi Hapus", 
            f"Anda yakin ingin menghapus Kasus ID {self.record_id}? Tindakan ini tidak dapat dibatalkan!"
        )

        if confirm:
            path_mentah = self.record_paths.get("Mentah")
            path_ekstraksi = self.record_paths.get("Ekstraksi")
            
            if delete_history(self.record_id, path_mentah, path_ekstraksi):
                messagebox.showinfo("Sukses", "Data dan file kasus berhasil dihapus.")
                self.controller.show_frame("RiwayatPencarian")
            else:
                messagebox.showerror("Error", "Gagal menghapus data.")

# --- HALAMAN 4C: EDIT RIWAYAT ---
class EditPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="gray17")
        self.controller = controller
        self.record_id = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(self, text="Edit Data Kasus", font=controller.FONT_JUDUL).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.edit_card = ctk.CTkFrame(self, fg_color="gray15", corner_radius=10)
        self.edit_card.grid(row=1, column=0, padx=20, pady=10, sticky="nwe")
        self.edit_card.grid_columnconfigure(0, weight=1)
        
        self._setup_edit_form()

    def _setup_edit_form(self):
        controller = self.controller
        
        # ID Kasus
        ctk.CTkLabel(self.edit_card, text="ID Kasus:", font=controller.FONT_UTAMA, anchor="w").grid(row=0, column=0, padx=30, pady=(20, 0), sticky="ew")
        self.lbl_id = ctk.CTkLabel(self.edit_card, text="", font=controller.FONT_SUBJUDUL, anchor="w")
        self.lbl_id.grid(row=1, column=0, padx=30, pady=(5, 10), sticky="ew")

        # Judul Kasus
        ctk.CTkLabel(self.edit_card, text="Judul Kasus:", font=controller.FONT_UTAMA, anchor="w").grid(row=2, column=0, padx=30, pady=(20, 0), sticky="ew")
        self.entry_judul = ctk.CTkEntry(self.edit_card, font=controller.FONT_UTAMA)
        self.entry_judul.grid(row=3, column=0, padx=30, pady=(5, 10), sticky="ew")
        
        # Nomor LP
        ctk.CTkLabel(self.edit_card, text="Nomor LP:", font=controller.FONT_UTAMA, anchor="w").grid(row=4, column=0, padx=30, pady=(10, 0), sticky="ew")
        self.entry_lp = ctk.CTkEntry(self.edit_card, font=controller.FONT_UTAMA)
        self.entry_lp.grid(row=5, column=0, padx=30, pady=(5, 10), sticky="ew")
        
        # Tanggal Kejadian
        ctk.CTkLabel(self.edit_card, text="Tanggal Kejadian:", font=controller.FONT_UTAMA, anchor="w").grid(row=6, column=0, padx=30, pady=(10, 0), sticky="ew")
        self.entry_tanggal = ctk.CTkEntry(self.edit_card, font=controller.FONT_UTAMA)
        self.entry_tanggal.grid(row=7, column=0, padx=30, pady=(5, 20), sticky="ew")
        
        # Tombol Aksi
        action_frame = ctk.CTkFrame(self.edit_card, fg_color="transparent")
        action_frame.grid(row=8, column=0, padx=30, pady=30, sticky="e")
        
        btn_simpan = ctk.CTkButton(action_frame, text="Simpan Perubahan", command=self.save_changes, height=40, fg_color="#1f6aa5", hover_color="#18537a")
        btn_simpan.pack(side="left", padx=10)
        
        btn_batal = ctk.CTkButton(action_frame, text="Batal", command=lambda: self.controller.show_frame("DetailPage", data={'id': self.record_id}), height=40, fg_color="gray40", hover_color="gray25")
        btn_batal.pack(side="left")


    def load_data(self, data_dict):
        # Fungsi ini dipanggil oleh controller untuk memuat data spesifik ke form edit
        self.record_id = data_dict['id']
        record = fetch_history_by_id(self.record_id)
        
        if record:
            self.lbl_id.configure(text=str(self.record_id))
            
            # Isi form dengan data yang ada
            self.entry_judul.delete(0, ctk.END)
            self.entry_judul.insert(0, record['judul_kasus'])
            
            self.entry_lp.delete(0, ctk.END)
            self.entry_lp.insert(0, record['nomor_lp'] if record['nomor_lp'] else "")
            
            self.entry_tanggal.delete(0, ctk.END)
            self.entry_tanggal.insert(0, record['tanggal_kejadian'] if record['tanggal_kejadian'] else "")
        else:
             messagebox.showerror("Error", "Data kasus tidak ditemukan.")
             self.controller.show_frame("RiwayatPencarian")

    def save_changes(self):
        judul = self.entry_judul.get()
        nomor_lp = self.entry_lp.get()
        tanggal = self.entry_tanggal.get()

        if not judul:
            messagebox.showerror("Validasi", "Judul Kasus tidak boleh kosong!")
            return

        try:
            update_history_data(self.record_id, judul, nomor_lp, tanggal)
            messagebox.showinfo("Sukses", "Data kasus berhasil diperbarui.")
            # Kembali ke halaman detail setelah menyimpan
            self.controller.show_frame("DetailPage", data={'id': self.record_id}) 
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan perubahan: {e}")