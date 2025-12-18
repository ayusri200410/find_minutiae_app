import os
import re
import sqlite3

# ==== KONFIGURASI PATH ====
BASE_DIR = r"C:\00. USER\AYU SRI\Aplikasi\APLIKASI ONGOING\find_minutiae_app\data_kasus"
MENTAH_DIR = os.path.join(BASE_DIR, "mentah")
EKSTRAKSI_DIR = os.path.join(BASE_DIR, "ekstraksi")

# Path ke database
DB_PATH = r"C:\00. USER\AYU SRI\Aplikasi\APLIKASI ONGOING\find_minutiae_app\minutiae_app_fixed.db"

# ==== REGEX FORMAT NAMA FILE ====
# Contoh: 20251122_232235_1_mentah.png


MENTAH_PATTERN = re.compile(
    r"^(?P<tanggal>\d{8})_(?P<waktu>\d{6})_(?P<nomor>\d+)(?:__?[A-Za-z]+)?_mentah\.png$",
    re.IGNORECASE
)

EKSTRAKSI_PATTERN = re.compile(
    r"^(?P<tanggal>\d{8})_(?P<waktu>\d{6})_(?P<nomor>\d+)(?:__?[A-Za-z]+)?_ekstraksi\.png$",
    re.IGNORECASE
)

# MENTAH_PATTERN = re.compile(r"^(?P<tanggal>\d{8})_(?P<waktu>\d{6})_(?P<nomor>\d+)_mentah\.png$")
# EKSTRAKSI_PATTERN = re.compile(r"^(?P<tanggal>\d{8})_(?P<waktu>\d{6})_(?P<nomor>\d+)_ekstraksi\.png$")

def build_nomor_lp(nomor_str: str) -> str:
    # Sesuai aturanmu: LP/B/<nomor>/XI/2025
    return f"LP/B/{nomor_str}/XI/2025"

def format_tanggal(tanggal_str: str) -> str:
    # YYYYMMDD -> YYYY-MM-DD
    return f"{tanggal_str[0:4]}-{tanggal_str[4:6]}-{tanggal_str[6:8]}"

def main():
    # Cek database
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database tidak ditemukan: {DB_PATH}")

    # Ambil daftar file mentah & ekstraksi
    mentah_files = [f for f in os.listdir(MENTAH_DIR) if f.lower().endswith("_mentah.png")]
    ekstraksi_files = [f for f in os.listdir(EKSTRAKSI_DIR) if f.lower().endswith("_ekstraksi.png")]

    # Index ekstraksi berdasarkan (tanggal, waktu, nomor) agar mudah dicocokkan
    ekstraksi_index = {}
    for fname in ekstraksi_files:
        m = EKSTRAKSI_PATTERN.match(fname)
        if not m:
            print(f"[SKIP EKS] Nama file ekstraksi tidak sesuai pola: {fname}")
            continue
        key = (m.group("tanggal"), m.group("waktu"), m.group("nomor"))
        ekstraksi_index[key] = fname

    # Koneksi ke DB
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Cek kolom di history biar yakin
    cur.execute("PRAGMA table_info(history);")
    cols = [row[1] for row in cur.fetchall()]
    expected = {
        "id",
        "judul_kasus",
        "nomor_lp",
        "tanggal_kejadian",
        "path_mentah",
        "path_ekstraksi",
        "user_id",
        "timestamp",
        "minutiae_count",
    }
    if not expected.issubset(set(cols)):
        raise RuntimeError(f"Struktur tabel 'history' tidak sesuai. Kolom sekarang: {cols}")

    # Optional: hindari duplikasi berdasarkan path_mentah
    cur.execute("SELECT path_mentah FROM history;")
    existing_mentah = {row[0] for row in cur.fetchall()}

    inserted = 0
    skipped_no_pair = 0
    skipped_existing = 0

    for fname in mentah_files:
        m = MENTAH_PATTERN.match(fname)
        if not m:
            print(f"[SKIP MENTAH] Nama file mentah tidak sesuai pola: {fname}")
            continue

        tanggal = m.group("tanggal")
        waktu = m.group("waktu")
        nomor = m.group("nomor")

        key = (tanggal, waktu, nomor)
        if key not in ekstraksi_index:
            print(f"[NO PAIR] Tidak ada pasangan ekstraksi untuk: {fname}")
            skipped_no_pair += 1
            continue

        ekstraksi_fname = ekstraksi_index[key]

        path_mentah = os.path.join(MENTAH_DIR, fname)
        path_ekstraksi = os.path.join(EKSTRAKSI_DIR, ekstraksi_fname)

        # Hindari insert data yang sudah ada
        if path_mentah in existing_mentah:
            skipped_existing += 1
            continue

        judul_kasus = nomor            # sesuai permintaanmu
        nomor_lp = build_nomor_lp(nomor)
        tanggal_kejadian = format_tanggal(tanggal)
        user_id = 1
        minutiae_count = 0

        cur.execute(
            """
            INSERT INTO history (
                judul_kasus,
                nomor_lp,
                tanggal_kejadian,
                path_mentah,
                path_ekstraksi,
                user_id,
                timestamp,
                minutiae_count
            )
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?)
            """,
            (
                judul_kasus,
                nomor_lp,
                tanggal_kejadian,
                path_mentah,
                path_ekstraksi,
                user_id,
                minutiae_count,
            ),
        )
        inserted += 1

    conn.commit()
    conn.close()

    print(f"Selesai.")
    print(f"Berhasil insert baru  : {inserted}")
    print(f"Skip (sudah ada)      : {skipped_existing}")
    print(f"Skip (tanpa pasangan) : {skipped_no_pair}")

if __name__ == "__main__":
    main()
