"""Delivery folder for Google Drive: everything the client and printer need, nothing internal
(no scripts, generated assets, references, Team B drafts or archives). Re-run after any revision;
files are overwritten in place.

  CGSO2026_Cadangan_Kulit_Buku/
    BACA_SAYA.txt                 contents + print and image notes (BM)
    01_Pembentangan/              pitch deck
    02_Pratonton_JPG/             full covers trimmed to A5, 300 ppi
    03_Mockup/                    book mockups
    04_PDF_Cetakan_CMYK/          press files (A5 + 3 mm bleed, FOGRA39)
    05_PSD_Berlapis/              live layered PSDs
    06_Pruf_Warna/                soft proofs

Run: venv python -I _scripts/package.py <workspace>
"""
import hashlib
import os
import shutil
import sys

from PIL import Image

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, "CGSO2026_Cadangan_Kulit_Buku")
B = round(3 * 300 / 25.4)                         # 3 mm bleed at 300 ppi
CONCEPTS = [("C1", "Konsep1_Alam_Sekitar", "CGSO2026_C1_Alam_Sekitar.psd"),
            ("C2", "Konsep2_Keselamatan_Dokumen", "CGSO2026_C2_Keselamatan_Dokumen.psd"),
            ("C3", "Konsep3_Ekonomi", "CGSO2026_C3_Ekonomi.psd")]

README = """CGSO 2026 - CADANGAN REKA BENTUK KULIT BUKU (3 KONSEP)
Pejabat Ketua Pegawai Keselamatan Kerajaan Malaysia, Jabatan Perdana Menteri
Saiz A5 (148 x 210 mm)

KONSEP
  1. Alam Sekitar          - Langit Biru, Negara Terpelihara
  2. Keselamatan Dokumen   - Daulat Terpelihara, Rahsia Terjaga
  3. Ekonomi (Tenaga)      - Berhemah Hari Ini, Teguh Esok

KANDUNGAN FOLDER
  01_Pembentangan       Deck cadangan (5 slaid): konsep, rasional, elemen wajib, spesifikasi.
  02_Pratonton_JPG      Kulit penuh saiz A5 (dipotong pada garis potong), 300 ppi.
                        Untuk dilihat di skrin atau dihantar melalui WhatsApp.
  03_Mockup             Mockup buku A5 bagi setiap konsep, dan ketiga-tiga konsep bersama.
  04_PDF_Cetakan_CMYK   Fail untuk pencetak: A5 + bleed 3 mm setiap sisi, CMYK FOGRA39, 300 ppi.
                        Jata Negara, teks dan logo "Rahsiakan Rahsia Kerajaan" dalam bentuk vektor.
  05_PSD_Berlapis       Fail Photoshop boleh sunting (RGB, 300 ppi, termasuk bleed).
                        Setiap elemen pada lapisan sendiri dengan layer mask; Jata, teks dan logo
                        dalam kumpulan berasingan; garis panduan bleed / potong / kawasan selamat
                        pada lapisan tersembunyi.
  06_Pruf_Warna         Pruf lembut FOGRA39 (rupa jangkaan di atas kertas bersalut) dan
                        perbandingan skrin berbanding cetakan.

NOTA UNTUK PENCETAK
  - Fail dibina untuk FOGRA39 (offset, kertas bersalut). Jika pencetak menggunakan keadaan
    cetakan lain (contohnya Japan Color 2001), fail boleh dibina semula.
  - Had dakwat 300% (maksimum sebenar 285%). Hitam Jata Negara 100% K.
  - Sudut buku bulat: dianggarkan ~6 mm. Semua elemen penting berada dalam kawasan selamat
    10 mm dari garis potong.
  - Teks putih kecil pada blok alamat (7.5 - 8.5 pt) adalah knockout empat warna; minta
    pencetak menyemak registration.
  - Pruf fizikal (contract proof atau press proof) disyorkan sebelum cetakan penuh.
  - Fail dibina mengikut keperluan PDF/X-4 tetapi belum disahkan oleh alat preflight.

NOTA IMEJ
  - Foto sebenar: Istana Negara, pegawai ATM (Konsep 1) dan PDRM (Konsep 2) [cadangan sahaja: perlu kebenaran ATM/PDRM], pesawat C-130H
    (Pangalau, CC BY-SA 4.0) dan Su-30MKM (Tentera Udara AS, domain awam), jerebu KL (Renek78,
    CC0), hutan Taman Negara (Vyacheslav Argenberg, CC BY 4.0), pakis dan krew minyak & gas
    (Pexels), dan semua elemen tenaga Konsep 3.
  - Domain awam (kerajaan AS): anggota ATM Konsep 2, Kol. Mohd Azral Manan, 10 Briged Para, pada
    majlis pembukaan Latihan Tiger Strike 2024 (DVIDS 8439351, Kpl. Aidan Hekker, USMC), dan kapal
    peronda TLDM KD Kelantan (175) di Selat Melaka, Konsep 3 (US Navy 110126-N-6320L-821, Oscar Sosa).
  - Pelajar Konsep 2 (wanita India Malaysia dengan telefon berkunci) ialah visual cadangan (AI),
    dipilih supaya ketiga-tiga kaum utama diwakili. Untuk cetakan akhir, gantikan dengan foto rasmi
    CGSO atau foto berlesen. Individu lain ialah foto sebenar.
  - Foto penganalisis siber, penyelidik dan belia menanam pokok dibekalkan untuk cadangan sahaja: untuk cetakan akhir, lesen setiap foto perlu disahkan (atau diganti dengan foto
    rasmi CGSO), dan individu yang boleh dikenal pasti memerlukan kebenaran. Pegawai PDRM dan ATM
    ialah individu sebenar: gunakan foto rasmi dengan kebenaran.
  - Istana Negara ialah foto sebenar: CEphoto, Uwe Aranas (CC BY-SA 3.0). Untuk cetakan akhir,
    foto ini boleh diganti dengan foto rasmi atau foto berlesen.
  - Konsep 3: langit ialah foto sebenar pesisir Malaysia waktu senja (dibekalkan untuk cadangan; lesen
    perlu disahkan). Ladang solar di bahagian bawah masih visual cadangan (AI).
  - Konsep 3 (Tenaga): semua elemen tenaga ialah foto sebenar (Wikimedia Commons).
    Kapal tangki "Eagle San Diego" (Jordanroderick, CC0, nama kapal dipadam), menara TNB 275 kV
    dan padang lalang (Wiki Farazi, CC0), Stesen Janakuasa Sultan Salahuddin Abdul Aziz, Kapar
    (Chongkian, CC BY-SA 4.0), tangki simpanan Pengerang (Encik Tekateki, CC BY-SA 4.0, tulisan
    dipadam), permukaan laut (Jules Verne Times Two, CC BY-SA 4.0).
  - Logo TNB ialah tanda dagangan Tenaga Nasional Berhad. Untuk cetakan akhir, kelulusan TNB
    atau CGSO diperlukan.
  - Pelantar minyak dan gas PETRONAS Dulang B (Konsep 3) ialah foto yang dibekalkan. Untuk
    cetakan akhir, kelulusan PETRONAS atau CGSO diperlukan.
  - Jata Negara pada fail sulit (Konsep 2) dibina daripada fail vektor rasmi yang dibekalkan,
    dalam satu warna (kesan kerajang emas). Jata utama di atas kulit kekal berwarna penuh.
  - Jalur Gemilang dibina semula secara vektor mengikut ukuran rasmi.
  - Lencana pada anggota keselamatan ialah lencana sebenar: lambang PDRM pada topi dan kolar
    polis, dan lencana beret 10 Briged Para pada anggota beret merah marun. Untuk produksi akhir,
    mohon CGSO sahkan atau bekalkan fail rasmi lencana ini.

27 Oktober 2026
"""


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def put(src, folder, name):
    d = os.path.join(OUT, folder)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, name)
    shutil.copy2(os.path.join(ROOT, src), dst)
    assert sha(os.path.join(ROOT, src)) == sha(dst), f"copy mismatch: {src}"


os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "BACA_SAYA.txt"), "w", encoding="utf-8", newline="\r\n") as f:
    f.write(README)

put("05_Presentation/CGSO2026_Cadangan_Kulit_Buku.pdf", "01_Pembentangan", "CGSO2026_Cadangan_Kulit_Buku.pdf")
put("05_Presentation/mockup_trio.jpg", "03_Mockup", "CGSO2026_Mockup_3_Konsep.jpg")
for key, name, psd in CONCEPTS:
    # preview trimmed to A5 (the bleed is only for the printer)
    os.makedirs(os.path.join(OUT, "02_Pratonton_JPG"), exist_ok=True)
    im = Image.open(os.path.join(ROOT, f"04_Final/{key}/CGSO2026_{key}_preview.jpg"))
    im.crop((B, B, B + 1748, B + 2480)).save(os.path.join(OUT, "02_Pratonton_JPG", f"CGSO2026_{name}.jpg"),
                                             quality=95, subsampling=0, dpi=(300, 300))
    put(f"05_Presentation/mockup_{key}.jpg", "03_Mockup", f"CGSO2026_Mockup_{name}.jpg")
    put(f"06_Print/CGSO2026_{key}_PRINT_CMYK_FOGRA39.pdf", "04_PDF_Cetakan_CMYK", f"CGSO2026_{name}_CETAK_CMYK.pdf")
    put(f"04_Final/{key}/{psd}", "05_PSD_Berlapis", f"CGSO2026_{name}.psd")
    put(f"06_Print/{key}_softproof_FOGRA39.jpg", "06_Pruf_Warna", f"{name}_Pruf_FOGRA39.jpg")
    put(f"06_Print/{key}_screen_vs_print.jpg", "06_Pruf_Warna", f"{name}_Skrin_vs_Cetakan.jpg")

total = 0
for dp, _, fs in sorted(os.walk(OUT)):
    for fn in sorted(fs):
        p = os.path.join(dp, fn)
        total += os.path.getsize(p)
        print(f"{os.path.getsize(p) / 1e6:8.1f} MB  {os.path.relpath(p, OUT)}")
print(f"{total / 1e6:8.1f} MB  total")
