buatkan saya sebuah aplikasi desktop menggunakan Tkinter beserta desain yang memanjakan mata dengan tema dark dengan kententuan sebagai berikut:

jadi singkatnya saya membuat sebuah aplikasi yang dapat melakukan ekstraksi minutiae pada sidik jari, dengan memanfaatkan model yang saya kembangkan, dan dalam aplikasi ini juga dapat menyimpan hasil atau Riwayat hasil dari sidik jari yang sudah diekstraksi sebelumnnya dengan bantuan dari database SQL Lite

1. Halaman Login:
- berbentuk card
- isi: 
	+ Judul: Sistem Ekstraksi Minutiae Find Minutiae
	+ Label: Username
	+ input kolom username
	+ Label: Password
	+ input kolom password

2. Halaman Home User
- berisikan Side Bar dengan isi:
	+ Judul: Find Minutiae
	+ Menu "Home" (active)
	+ Menu "Cari Minutiae"
	+ Menu "Riwayat Pencarian"

- Dashboard yang menampilkan:
	+ Jumlah Pencarian Umum (dibungkus Card)
	+ Jumlah Pencarian Lokal (dibungkus Card)

- Terdapat Tombol Logout pada Pojok Kanan Atas layar

3. Halaman Cari Minutiae
- berisikan Side Bar dengan isi:
	+ Judul: Find Minutiae
	+ Menu "Home" 
	+ Menu "Cari Minutiae" (Active)
	+ Menu "Riwayat Pencarian"
- Dashboard yang menampilkan:
	+ Form (dibungkus Card) dengan isi:
		- Label "Judul Kasus:"
		- Input Text Kolom 
		- Label "Nomor LP:"
		- Input Text Kolom
		- Label "Tanggal Kejadian:"
		- Input Text Kolom 
		- Label "Upload Sidik Jari" (bertujuan untuk fungsi Upload Gambar Sidik Jari mentah tanpa titik minutiae dari device)
		- Tombol "Lanjut"
	+ Setelah Tombol Lanjut Di klik maka:
		- Akan menjalankan fungsi model yang sudah saya buat dengan memproses gambar dari hasil upload untuk menemukan titik minutiaenya dan kemudian gambar tersebut akan ditampilkan pada halaman hasil ekstraksi minutiae
		- akan masuk ke halaman hasil ekstraksi minutiae yang berisikan:
			+ Label "Judul Kasus:"
			+ Input Text Kolom dengan valuenya
			+ Label "Nomor LP:"
			+ Input Text Kolom dengan valuenya
			+ Label "Tanggal Kejadian:"
			+ Input Text Kolom dengan valuenya
			+ Label "Hasil Ekstraksi minutiae" Memunculkan Gambar hasil ekstraksi minutiae
		
		- dan akan menyimpan data pencarian Minutiae tersebut dengan ketentuan:
			+ gambar Sidik Jari mentah disimpan pada folder Image/"Judul kasus yang telah dimasukkan"/SJ-mentah.jpg 
			+ gambar Hasil Ekstraksi Sidik Jari  disimpan pada folder Image/"Judul kasus yang telah dimasukkan"/SJ-extracted.jpg 
			+ data selain gambar disimpan pada database

4. Halaman Riwayat Pencarian, berisikan:
 - berisikan Side Bar dengan isi:
	+ Judul: Find Minutiae
	+ Menu "Home" 
	+ Menu "Cari Minutiae" 
	+ Menu "Riwayat Pencarian" (Active)
- Dashboard yang menampilkan:
	+ Menu Pencarian Umum (dibungkus dalam tombol berbentuk card)
		yang jika di klik maka akan masuk ke layer "Pencarian Umum" dengan isi:
		- Judul "Pencarian Lokal"
		- Search bar 
		- Tabel dengan kolom:
			+ No
			+ Judul kasus
			+ Nomor LP
			+ Tanggal Kejadian
			+ Aksi
				pada kolom aksi terdapat 3 menu dengan icon:
					- icon mata 
						yang jika diklik maka akan masuk ke layer "Detail pencarian" yang berisikan:
							+ Label "Judul Kasus:"
							+ Input Text Kolom dengan valuenya
							+ Label "Nomor LP:"
							+ Input Text Kolom dengan valuenya
							+ Label "Tanggal Kejadian:"
							+ Input Text Kolom dengan valuenya
							+ Label "SJ Mentah" dibawahya Memunculkan Gambar Sidik Jari Mentah
							+ Label "Hasil Ekstraksi minutiae" dibawahnya Memunculkan Gambar hasil ekstraksi minutiae
					- icon pensil
						yang jika diklik maka akan masuk ke layer "Edit Pencarian" yang berisikan: 
							+ Label "Judul Kasus:"
							+ Input Text Kolom dengan valuenya yang dapat diedit
							+ Label "Nomor LP:"
							+ Input Text Kolom dengan valuenya yang dapat diedit
							+ Label "Tanggal Kejadian:"
							+ Input Text Kolom dengan valuenya yang dapat diedit
							+ Label "SJ Mentah" dibawahya Memunculkan Gambar Sidik Jari Mentah (ini tidak dapat diedit)
							+ Label "Hasil Ekstraksi minutiae" dibawahnya Memunculkan Gambar hasil ekstraksi minutiae (ini tidak dapat diedit)
							+ Tombol "Ubah"
								yang jika diklik akan mengubah data pencarian tersebut pada database
					- icon tong sampah 
						yang jika diklik memunculkan modal atau validasi "yakin menghapus data ini?" kemudian terdapat tombol "Iya " dan "Tidak" jika iya di klik maka data pencarian tersebut akan dihaopus dari database

	+ Menu Pencarian Lokal (dibungkus dalam tombol berbentuk card)
		yang jika di klik maka akan masuk ke layer "Pencarian Lokal" dengan isi:
		- Judul "Pencarian Lokal"
		- Search bar 
		- Tabel dengan kolom:
			+ No
			+ Judul kasus
			+ Nomor LP
			+ Tanggal Kejadian
			+ Aksi
				pada kolom aksi terdapat 3 menu dengan icon:
					- icon mata 
						yang jika diklik maka akan masuk ke layer "Detail pencarian" yang berisikan:
							+ Label "Judul Kasus:"
							+ Input Text Kolom dengan valuenya
							+ Label "Nomor LP:"
							+ Input Text Kolom dengan valuenya
							+ Label "Tanggal Kejadian:"
							+ Input Text Kolom dengan valuenya
							+ Label "SJ Mentah" dibawahya Memunculkan Gambar Sidik Jari Mentah
							+ Label "Hasil Ekstraksi minutiae" dibawahnya Memunculkan Gambar hasil ekstraksi minutiae
					- icon pensil
						yang jika diklik maka akan masuk ke layer "Edit Pencarian" yang berisikan: 
							+ Label "Judul Kasus:"
							+ Input Text Kolom dengan valuenya yang dapat diedit
							+ Label "Nomor LP:"
							+ Input Text Kolom dengan valuenya yang dapat diedit
							+ Label "Tanggal Kejadian:"
							+ Input Text Kolom dengan valuenya yang dapat diedit
							+ Label "SJ Mentah" dibawahya Memunculkan Gambar Sidik Jari Mentah (ini tidak dapat diedit)
							+ Label "Hasil Ekstraksi minutiae" dibawahnya Memunculkan Gambar hasil ekstraksi minutiae (ini tidak dapat diedit)
							+ Tombol "Ubah"
								yang jika diklik akan mengubah data pencarian tersebut pada database
					- icon tong sampah 
						yang jika diklik memunculkan modal atau validasi "yakin menghapus data ini?" kemudian terdapat tombol "Iya " dan "Tidak" jika iya di klik maka data pencarian tersebut akan dihaopus dari database

tolong buatkan secara bertahap, halaman per halaman agar kamu juga membuat secara detail, saya akan perintahkan untuk lanjutkan baru anda lanjutkan pada kode halaman selanjutnya yaa, serta sebelum itu berikan dulu saya apa saja yang perlu disiapkan seperti package yang perlu di install, aplikasi yang perlu di install dll, setiap mau lanjut ke Langkah selanjutnya selalu tanya saya "apakah kita bisa lanjut pada tahap selanjutnya?" seperti itu ya. sebelumnya dari penjelasan saya apakah ada yang perlu kamu tanyakan?

find_minutiae_app/
├── main.py              # Titik masuk aplikasi (Controller utama / Class App)
├── db_manager.py        # Semua fungsi interaksi database SQLite
├── pages/
│   ├── __init__.py      # Menjadikan 'pages' sebagai package
│   ├── login_page.py    # Class LoginPage
│   ├── home_page.py     # Class HomePage
│   ├── cari_minutiae.py # Class CariMinutiaePage & HasilEkstraksiPage
│   ├── riwayat_page.py  # Class RiwayatPencarianPage dan sub-halamannya
├── components/
│   ├── __init__.py
│   └── sidebar.py       # Class Sidebar
└── assets/
    └── ... (gambar)


untuk fungsi pada halaman cari minutiae memang belum bisa yaa?, ohh iya saya lupa memberikan kode model pemroresan dari model saya maaf ya , sekarang saya berikan



pip install fingerflow

import cv2
import matplotlib.pyplot as plt

import numpy as np

from fingerflow.extractor import Extractor

extractor = Extractor("models/CoarseNet.h5", "models/FineNet.h5", "models/ClassifyNet_6_classes.h5", "models/CoreNet.weights")

image = cv2.imread("images/2.png")

extracted_minutiae = extractor.extract_minutiae(image)

print(extracted_minutiae)

# tampilkan gambar fingerprint
plt.imshow(image, cmap="gray")

# ambil dataframe minutiae
minutiae_df = extracted_minutiae["minutiae"]

# tampilkan gambar fingerprint
plt.imshow(image, cmap="gray")

# gambar titik minutiae
plt.scatter(minutiae_df["x"], minutiae_df["y"], c="red", s=20, marker="o")

plt.title("Detected Minutiae Points")
plt.show()

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


enang mendengar aplikasi Anda akhirnya berjalan! Untuk menjalankan aplikasi Anda di laptop baru, Anda harus mereplikasi persis lingkungan yang telah kita perjuangkan.

Langkah-langkah berikut adalah rangkuman dari solusi yang terbukti berhasil, memastikan Anda menghindari semua konflik dependency yang telah kita perbaiki.

🛠️ Langkah-Langkah Wajib untuk Laptop Baru
Anda akan memerlukan Python 3.7 dan file requirements.txt yang Anda buat. Jika Anda belum membuat file tersebut, gunakan perintah ini di lingkungan lama Anda: pip freeze > requirements.txt.

Langkah 1: Instal Python 3.7
Instal versi Python yang sama persis yang terbukti bekerja (Python 3.7) untuk memastikan kompatibilitas SciPy 1.2.1.

Instal Python 3.7.9 (64-bit): Unduh dan instal versi ini dari situs web Python (pilih Windows x86-64 executable installer). Pastikan instalasi diatur ke jalur yang mudah diingat (misalnya, C:\Python37).

Langkah 2: Buat Virtual Environment Baru
Buat virtual environment menggunakan instalasi Python 3.7 yang baru.

Buka Terminal/CMD di folder aplikasi Anda.

Buat Venv: Ganti C:\Path\To\Python37\python.exe dengan jalur instalasi Python 3.7 Anda.

Bash

"C:\Path\To\Python37\python.exe" -m venv venv_fingerflow_37_new
Aktifkan Venv:

Bash

venv_fingerflow_37_new\Scripts\activate
🔑 Langkah 3: Instalasi Dependency Krusial (Memperbaiki Konflik Lama)
Kita akan menginstal paket secara terpisah untuk memastikan kita mengunci versi yang benar-benar krusial sebelum yang lain.

Instal TensorFlow dan Protobuf: Ini memperbaiki konflik Protobuf yang kita temui.

Bash

pip install tensorflow==2.5.0 protobuf==3.20.3
Instal SciPy dan NumPy: Ini memperbaiki error multichannel dan typeDict.

Bash

pip install scipy==1.2.1 numpy==1.19.5
Langkah 4: Instal Sisa Dependencies
Daripada menggunakan requirements.txt sepenuhnya, kita akan menginstal sisa library yang kita temukan hilang satu per satu, dengan menambahkan flag --no-deps pada fingerflow untuk menjaga SciPy 1.2.1 tetap aman.

Instal Fingerflow dan Sisanya dengan Perlindungan:

Bash

pip install fingerflow --no-deps
pip install scikit-image pandas pytz keras-applications customtkinter opencv-python matplotlib
Langkah 5: Uji Coba
Jalankan aplikasi Anda:

Bash

python main.py
Dengan mengikuti langkah-langkah ini, Anda menduplikasi lingkungan kerja yang proven dan menghindari semua jebakan dependency yang sudah kita selesaikan bersama. Selamat!
