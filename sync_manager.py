# sync_manager.py
import os
import requests
import time
from supabase import create_client, Client
from db_manager import get_unsynced_history, mark_history_synced
from db_manager import DB_PATH  # optional, kalau perlu path
from pathlib import Path

# Konfigurasi via env vars
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_BUCKET = os.environ.get("SUPABASE_BUCKET", "minutiae")  # nama bucket default

# Supabase client (lazy init)
_supabase: Client | None = None
def get_supabase():
    global _supabase
    if _supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("SUPABASE_URL atau SUPABASE_KEY belum di-set di environment.")
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase

# -----------------------
# Utility: cek koneksi
# -----------------------
def is_online(test_url="https://www.google.com", timeout=3):
    try:
        requests.get(test_url, timeout=timeout)
        return True
    except Exception:
        return False

# -----------------------
# Upload file ke Supabase Storage
# -----------------------
def upload_file_to_storage(local_path: str, dest_filename: str):
    """
    Upload file lokal ke Supabase Storage bucket SUPABASE_BUCKET.
    Mengembalikan public URL (jika sukses) atau None.
    """
    supabase = get_supabase()
    bucket = supabase.storage.from_(SUPABASE_BUCKET)

    # Pastikan file ada
    if not os.path.exists(local_path):
        raise FileNotFoundError(local_path)

    # Baca biner
    with open(local_path, "rb") as f:
        data = f.read()

    # Gunakan upsert=True supaya bisa replace
    res = bucket.upload(dest_filename, data, {"upsert": True})
    # res akan berisi metadata jika sukses atau error
    if res and isinstance(res, dict) and res.get("error"):
        raise RuntimeError(f"Upload error: {res['error']}")
    # ambil public URL
    url_res = bucket.get_public_url(dest_filename)
    if isinstance(url_res, dict):
        # supabase-py mungkin kembalikan dict with 'publicURL' or 'public_url'
        # handle common keys
        return url_res.get("publicURL") or url_res.get("public_url")
    # atau jika object
    return url_res

# -----------------------
# Upload 1 record: file mentah + ekstraksi + insert ke tabel cloud
# -----------------------
def upload_history_row_to_cloud(row):
    """
    row = sqlite3.Row object
    Proses:
     - upload file mentah -> url_mentah
     - upload file ekstraksi -> url_ekstraksi
     - insert record ke supabase table 'history' (sesuaikan schema)
     - update local as synced with cloud_id & urls
    """
    supabase = get_supabase()
    bucket_prefix = "minutiae"  # folder di bucket
    history_id = row["id"]
    judul = row["judul_kasus"]
    nomor_lp = row["nomor_lp"]
    tanggal = row["tanggal_kejadian"]
    path_mentah = row["path_mentah"]
    path_ekstraksi = row["path_ekstraksi"]
    user_id = row["user_id"]

    # build dest filenames (unik)
    timestamp = int(time.time())
    mentah_name = f"{bucket_prefix}/{timestamp}_{history_id}_mentah.png"
    ekstraksi_name = f"{bucket_prefix}/{timestamp}_{history_id}_ekstraksi.png"

    # upload files
    url_mentah = upload_file_to_storage(path_mentah, mentah_name)
    url_ekstraksi = upload_file_to_storage(path_ekstraksi, ekstraksi_name)

    # insert to supabase table 'history' - table should exist in Supabase
    payload = {
        "judul_kasus": judul,
        "nomor_lp": nomor_lp,
        "tanggal_kejadian": tanggal,
        "url_mentah": url_mentah,
        "url_ekstraksi": url_ekstraksi,
        "local_history_id": history_id,
        "user_id": user_id
    }
    insert_res = supabase.table("history").insert(payload).execute()
    # check error
    if insert_res.error:
        raise RuntimeError(f"Supabase insert error: {insert_res.error.message if insert_res.error else insert_res}")

    # get cloud id from returned data (assume insert_res.data[0]['id'])
    cloud_id = None
    try:
        cloud_id = insert_res.data[0].get("id")
    except Exception:
        cloud_id = None

    # update local db as synced
    mark_history_synced(history_id, cloud_id, url_mentah, url_ekstraksi)

    return True

# -----------------------
# Sync pending rows (loop)
# -----------------------
def sync_pending_records(limit: int = 10):
    """
    Sinkronisasi semua record dengan is_synced = 0.
    Mengembalikan tuple (synced_count, failed_list)
    """
    if not is_online():
        return 0, []

    rows = get_unsynced_history()
    synced = 0
    failed = []
    for r in rows[:limit]:
        try:
            upload_history_row_to_cloud(r)
            synced += 1
        except Exception as e:
            failed.append((r["id"], str(e)))
    return synced, failed

# -----------------------
# Fetch online history (ambil dari cloud)
# -----------------------
def fetch_online_history(limit=100, offset=0):
    """
    Mengambil data 'history' dari supabase.
    Kembalikan list of dict.
    """
    if not is_online():
        return []
    supabase = get_supabase()
    res = supabase.table("history").select("*").order("created_at", {"ascending": False}).limit(limit).offset(offset).execute()
    if res.error:
        raise RuntimeError(f"Fetch error: {res.error.message}")
    return res.data or []
