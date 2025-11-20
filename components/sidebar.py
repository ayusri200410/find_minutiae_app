import customtkinter as ctk
from db_manager import get_user_by_id

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=180, corner_radius=0, fg_color="gray17")
        self.controller = controller

        # reserve many rows so logout sticks to bottom
        for r in range(0, 100):
            self.grid_rowconfigure(r, weight=0)
        self.grid_rowconfigure(98, weight=1)  # spacer row

        # ----- TITLE (lebar disamakan dengan tombol logout) -----
        ctk.CTkLabel(
            self, text="Find Minutiae",
            font=controller.FONT_JUDUL,
            text_color="#1f6aa5",
            anchor="center"
        ).grid(row=0, column=0, sticky="ew", padx=10, pady=(20, 10))

        ctk.CTkFrame(self, height=1, fg_color="gray30") \
            .grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 20))

        # ----- MENU CONTAINER (full width, padding disamakan) -----
        self.menu_container = ctk.CTkFrame(self, fg_color="transparent")
        self.menu_container.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
        self.menu_container.grid_columnconfigure(0, weight=1)

        self.menus = {}
        self.admin_menu_key = "Manajemen User"

        self._build_static_menus()
        self._maybe_add_admin_menu()

        # ----- LOGOUT BUTTON (standar width) -----
        self.logout_btn = ctk.CTkButton(
            self,
            text="Logout",
            corner_radius=7,
            fg_color="#b33030",      # merah
            hover_color="#8b2626",   # merah gelap saat hover
            text_color="white",
            command=self._on_logout,
            font=controller.FONT_UTAMA,
            anchor="center"
        )
        self.logout_btn.grid(row=99, column=0, sticky="ew", padx=10, pady=(6, 16))

    # -----------------------
    # MENU BUILDER
    # -----------------------
    def _build_static_menus(self):
        for w in self.menu_container.winfo_children():
            w.destroy()
        self.menus.clear()

        row_counter = 0

        def add(key, text, cmd):
            nonlocal row_counter
            btn = ctk.CTkButton(
                self.menu_container,
                text=text,
                corner_radius=7,
                fg_color="transparent",
                hover_color="gray25",
                command=cmd,
                font=self.controller.FONT_UTAMA,
                anchor="center"
            )
            # padding disamakan seperti logout_btn
            btn.grid(row=row_counter, column=0, sticky="ew", padx=10, pady=(6, 6))
            self.menus[key] = btn
            row_counter += 1

        add("Home", "Home", lambda: self.controller.show_frame("Home"))
        add("CariMinutiae", "Cari Minutiae", lambda: self.controller.show_frame("CariMinutiae"))
        add("RiwayatPencarian", "Riwayat Pencarian", lambda: self.controller.show_frame("RiwayatPencarian"))

    # -----------------------
    # ADMIN BUTTON
    # -----------------------
    def _maybe_add_admin_menu(self):
        uid = getattr(self.controller, "logged_in_user_id", None)
        show_admin = False

        if uid is not None:
            try:
                user = get_user_by_id(uid)
                if user and str(user.get("username")).lower() == "admin":
                    show_admin = True
            except Exception:
                show_admin = False

        if show_admin and self.admin_menu_key not in self.menus:
            current_rows = len(self.menu_container.grid_slaves())

            btn = ctk.CTkButton(
                self.menu_container,
                text="Manajemen User",
                corner_radius=7,
                fg_color="transparent",
                hover_color="gray25",
                command=lambda: self.controller.show_frame("UserManagement"),
                font=self.controller.FONT_UTAMA,
                anchor="center"
            )
            btn.grid(row=current_rows, column=0, sticky="ew", padx=10, pady=(6, 6))
            self.menus[self.admin_menu_key] = btn

        if not show_admin and self.admin_menu_key in self.menus:
            self.menus[self.admin_menu_key].destroy()
            del self.menus[self.admin_menu_key]

    def refresh(self):
        self._build_static_menus()
        self._maybe_add_admin_menu()

    # -----------------------
    # ACTIVE MENU HIGHLIGHT
    # -----------------------
    def set_active(self, key):
        for btn in self.menus.values():
            btn.configure(fg_color="transparent")

        if key in self.menus:
            self.menus[key].configure(fg_color="#1f6aa5")

    # -----------------------
    # LOGOUT
    # -----------------------
    def _on_logout(self):
        if hasattr(self.controller, "logout"):
            self.controller.logout()
        else:
            try:
                self.controller.logged_in_user_id = None
            except Exception:
                pass
            self.refresh()
