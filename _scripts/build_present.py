"""Pitch deck (16:9 PDF) in Bahasa Malaysia: title, one slide per concept
(flat cover + rationale + mandatory-element checklist + mockup), specs/credits."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pymupdf
from PIL import Image

from typeset import FONT_DIR

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, "05_Presentation")
PW, PH = 1600, 900
NAVY, GOLD, WHITE, MUTED = (0.043, 0.078, 0.188), (0.886, 0.737, 0.31), (1, 1, 1), (0.72, 0.76, 0.86)
F = {k: os.path.join(FONT_DIR, f"Roboto-{k}.ttf") for k in ("Regular", "Medium", "Bold", "Black")}

CONCEPTS = [
    dict(key="C1", no="KONSEP 1", theme="ALAM SEKITAR", title="Langit Biru, Negara Terpelihara",
         accent=(0.56, 0.84, 1.0),
         body=("Jerebu bukan sekadar isu cuaca. Ia menjejaskan kesihatan rakyat, ekonomi dan imej negara. "
               "Langit yang beralih daripada jerebu kepada biru di atas Istana Negara melambangkan usaha bersama "
               "memulihkan alam sekitar sebagai aset negara.\n\n"
               "Pesawat C-130H TUDM dalam operasi pembenihan awan meninggalkan jejak yang membuka laluan langit biru "
               "menembusi jerebu, dan anggota ATM yang memberi tabik hormat mewakili pasukan keselamatan. Penyelidik dengan alat pemantau kualiti udara mewakili penyelidikan, "
               "manakala anak muda "
               "yang menanam pokok melambangkan tanggungjawab rakyat. Hutan hujan tropika menjadi asas: alam yang "
               "dilindungi hari ini ialah warisan generasi akan datang. Corak guilloche dan teks mikro "
               "\"Rahsiakan Rahsia Kerajaan\" di sekeliling kulit ialah ciri keselamatan dokumen."),
         checks=["Istana Negara, Jalan Duta", "Pegawai keselamatan: anggota ATM + pesawat C-130H TUDM",
                 "Rakyat / anak muda: belia menanam pokok", "Penyelidikan: penyelidik kualiti udara",
                 "Jalur Gemilang", "Ciri keselamatan: corak guilloche + teks mikro"]),
    dict(key="C2", no="KONSEP 2", theme="KESELAMATAN DOKUMEN", title="Daulat Terpelihara, Rahsia Terjaga",
         accent=(0.886, 0.737, 0.31),
         body=("Kedaulatan negara bermula dengan maklumat yang terpelihara. Corak guilloche keemasan, iaitu teknik "
               "keselamatan pada pasport dan wang kertas, membentuk lingkaran pelindung di belakang Istana Negara, "
               "lengkap dengan teks mikro \"Rahsiakan Rahsia Kerajaan\" dan nama Pejabat Ketua Pegawai Keselamatan "
               "Kerajaan Malaysia.\n\n"
               "Fail sulit berlambang Jata Negara bercetak kerajang emas, dimeterai dengan logo \"Rahsiakan Rahsia "
               "Kerajaan\", melambangkan dokumen rasmi kerajaan yang wajib dilindungi. "
               "Anggota PDRM dan ATM berkawal, pesawat "
               "Su-30MKM TUDM mengawal ruang udara, penyelidik keselamatan siber memantau ancaman digital, dan seorang "
               "pelajar menunjukkan telefon berkunci: setiap rakyat bertanggungjawab tidak berkongsi maklumat rasmi."),
         checks=["Istana Negara, Jalan Duta", "Pegawai keselamatan: PDRM + ATM + Su-30MKM TUDM",
                 "Rakyat / anak muda: pelajar universiti", "Penyelidikan: penyelidik keselamatan siber",
                 "Jalur Gemilang", "Ciri keselamatan: guilloche, teks mikro, Jata kerajang emas"]),
    dict(key="C3", no="KONSEP 3", theme="EKONOMI", title="Berhemah Hari Ini, Teguh Esok",
         accent=(1.0, 0.54, 0.24),
         body=("Konflik di Timur Tengah menjejaskan bekalan dan harga tenaga dunia. Bekalan minyak, gas asli, arang batu "
               "dan grid elektrik negara ialah aset yang mesti dilindungi, dan langkah penjimatan menjadi tanggungjawab "
               "bersama. Kapal tangki minyak belayar dengan selamat di bawah matahari terbit, dengan tangki simpanan gas "
               "dan stesen janakuasa arang batu TNB di pesisir. Menara grid TNB menyalurkan tenaga ke seluruh negara.\n\n"
               "Graf emas yang menurun seketika sebelum meningkat semula melambangkan ekonomi yang pulih melalui langkah "
               "berhemah. Pelantar minyak dan gas di luar pesisir, krew minyak dan gas yang memantau keselamatan bekalan, "
               "ladang solar sebagai langkah penjimatan tenaga, kapal peronda TLDM KD Kelantan yang mengiringi kapal tangki, "
               "dan Su-30MKM TUDM yang mengawal laluan tenaga negara. "
               "Corak guilloche dan teks mikro \"Rahsiakan Rahsia Kerajaan\" ialah ciri keselamatan dokumen."),
         checks=["Tenaga: kapal tangki, pelantar minyak & gas, tangki gas, arang batu, grid TNB",
                 "Pegawai keselamatan: kapal peronda TLDM + Su-30MKM TUDM",
                 "Rakyat: krew minyak dan gas", "Penjimatan tenaga: ladang solar",
                 "Jalur Gemilang", "Ciri keselamatan: corak guilloche + teks mikro"]),
]


def fonts(page):
    for k, f in F.items():
        page.insert_font(fontname=f"rb{k}", fontfile=f)


def bg(page):
    page.draw_rect(page.rect, color=None, fill=NAVY)


def text(page, rect, s, size, weight="Regular", color=WHITE, align=0, lh=1.25):
    x0, y0, x1, y1 = rect
    # dry-run on a scratch page so a too-short box grows instead of silently clipping
    scratch = pymupdf.open().new_page(width=PW, height=PH)
    while scratch.insert_textbox(pymupdf.Rect(x0, y0, x1, y1), s, fontsize=size, fontname=f"rb{weight}",
                                 fontfile=F[weight], lineheight=lh) < 0:
        y1 += 10
        assert y1 < PH + 400, f"text overflow: {s[:40]}"
    page.insert_textbox(pymupdf.Rect(x0, y0, x1, y1), s, fontsize=size, fontname=f"rb{weight}", fontfile=F[weight],
                        color=color, align=align, lineheight=lh)
    return y1


def image(page, rect, path):
    page.insert_image(pymupdf.Rect(*rect), filename=path, keep_proportion=True)


def cover_jpg(key):
    """Trimmed, downsized cover for the deck (keeps the PDF light)."""
    p = os.path.join(OUT, f"_deck_{key}.jpg")
    im = Image.open(os.path.join(ROOT, f"04_Final/{key}/CGSO2026_{key}_preview.jpg"))
    b = round(3 * 300 / 25.4)
    im = im.crop((b, b, b + 1748, b + 2480)).resize((1166, 1654), Image.LANCZOS)
    im.save(p, quality=90)
    return p


doc = pymupdf.open()

# ---- title
pg = doc.new_page(width=PW, height=PH)
fonts(pg)
bg(pg)
trio = os.path.join(OUT, "_deck_trio.jpg")
Image.open(os.path.join(OUT, "mockup_trio.jpg")).resize((1900, 850), Image.LANCZOS).save(trio, quality=88)
image(pg, (0, 300, PW, 900), trio)
pg.draw_rect(pymupdf.Rect(80, 96, 86, 236), color=None, fill=GOLD)
text(pg, (110, 86, 1500, 150), "CADANGAN REKA BENTUK KULIT BUKU 2026", 46, "Black", GOLD)
text(pg, (110, 150, 1500, 200), "Pejabat Ketua Pegawai Keselamatan Kerajaan Malaysia  ·  Jabatan Perdana Menteri", 22,
     "Medium", WHITE)
text(pg, (110, 196, 1500, 240), "3 konsep  ·  Saiz A5  ·  \"Lindungi Aset Negara, Tanggungjawab Bersama\"", 20,
     "Regular", MUTED)

# ---- concepts
for c in CONCEPTS:
    pg = doc.new_page(width=PW, height=PH)
    fonts(pg)
    bg(pg)
    cj = cover_jpg(c["key"])
    pg.draw_rect(pymupdf.Rect(70, 60, 70 + 548, 60 + 778), color=None, fill=(0.02, 0.04, 0.1))
    image(pg, (60, 50, 60 + 548, 50 + 778), cj)
    x0 = 680
    text(pg, (x0, 58, 1540, 90), f"{c['no']}  ·  {c['theme']}", 18, "Bold", c["accent"])
    text(pg, (x0, 88, 1540, 160), c["title"], 40, "Black", WHITE)
    pg.draw_rect(pymupdf.Rect(x0, 162, x0 + 70, 166), color=None, fill=c["accent"])
    text(pg, (x0, 186, 1180, 640), c["body"], 17, "Regular", (0.88, 0.9, 0.95), lh=1.42)
    text(pg, (x0, 650, 1180, 680), "ELEMEN WAJIB", 15, "Bold", c["accent"])
    y = 682
    for item in c["checks"]:
        pg.draw_circle(pymupdf.Point(x0 + 8, y + 10), 7, color=None, fill=c["accent"])
        y = text(pg, (x0 + 24, y, 1180, y + 26), item, 15, "Medium", WHITE) + 4      # a wrapped item pushes the next down
    mk = os.path.join(OUT, f"_deck_mock_{c['key']}.jpg")
    Image.open(os.path.join(OUT, f"mockup_{c['key']}.jpg")).resize((900, 675), Image.LANCZOS).save(mk, quality=88)
    image(pg, (1210, 330, 1560, 600), mk)
    text(pg, (1210, 606, 1560, 630), "Mockup buku A5", 12, "Regular", MUTED, align=1)

# ---- specs & credits
pg = doc.new_page(width=PW, height=PH)
fonts(pg)
bg(pg)
text(pg, (110, 86, 1500, 150), "SPESIFIKASI & NOTA", 40, "Black", GOLD)
specs = [
    ("Saiz", "A5 (148 × 210 mm) + bleed 3 mm setiap sisi, resolusi 300 ppi."),
    ("Fail diserahkan", "PDF cetakan CMYK (logo Jata Negara, teks dan logo \"Rahsiakan Rahsia Kerajaan\" dalam bentuk vektor), "
                        "PSD berlapis boleh sunting, JPG pratonton, pruf warna dan mockup."),
    ("Tipografi & logo", "Roboto; tajuk utama Roboto Black. Saiz teks mengikut sampel kulit 2024. Jata Negara 33 mm, logo "
                         "\"Rahsiakan Rahsia Kerajaan\" 29 mm (lebih kecil daripada Jata), sejajar dengan tajuk."),
    ("Ciri keselamatan", "Setiap konsep: corak guilloche (teknik keselamatan wang kertas dan pasport) dan teks mikro "
                         "\"Rahsiakan Rahsia Kerajaan\" di sekeliling kulit. K2: lingkaran guilloche dan Jata kerajang emas pada fail sulit."),
    ("Jalur Gemilang", "Dibina semula secara vektor mengikut ukuran rasmi (14 jalur, bintang 14 bucu, kanton 8 jalur)."),
    ("Warna", "CMYK FOGRA39 (offset, kertas bersalut), had dakwat 300% (maks. sebenar 285%). Jata: hitam 100% K, warna pepejal bersih; "
              "merah logo kekal CMYK asal (M90.5 Y96.1). Pruf lembut disertakan; pruf fizikal disyorkan bersama pencetak."),
    ("Sudut buku", "Elemen penting berada dalam kawasan selamat 10 mm untuk sudut bulat (~6 mm, tertakluk kepada pencetak)."),
    ("Kredit foto", "Istana Negara: CEphoto, Uwe Aranas (CC BY-SA 3.0). C-130H: Pangalau (CC BY-SA 4.0). Su-30MKM: Tentera Udara AS; "
                    "Kol. Mohd Azral Manan (K2): DVIDS 8439351, Kpl. Aidan Hekker, USMC; KD Kelantan (K3): Tentera Laut AS, Oscar Sosa "
                    "(domain awam). Jerebu KL: Renek78 (CC0). Hutan Taman Negara: Vyacheslav Argenberg (CC BY 4.0). Pakis dan krew minyak "
                    "& gas: Pexels. K3: Stesen Janakuasa Sultan Salahuddin Abdul Aziz: Chongkian; tangki: Encik Tekateki; laut: Jules "
                    "Verne Times Two (CC BY-SA 4.0); kapal tangki dan menara TNB: CC0."),
    ("Sumber imej", "Semua individu ialah foto sebenar kecuali pelajar K2 (visual cadangan AI). Foto yang dibekalkan (penganalisis siber, "
                    "penyelidik, belia menanam pokok, langit K3, pelantar PETRONAS) serta pegawai PDRM dan ATM: lesen dan kebenaran perlu "
                    "disahkan sebelum cetakan. Ladang solar K3 masih visual cadangan (AI). Logo TNB dan PETRONAS memerlukan kelulusan."),
]
y = 176
for k, v in specs:
    text(pg, (110, y, 400, y + 24), k.upper(), 14, "Bold", GOLD)
    y = max(text(pg, (400, y - 2, 1500, y + 24), v, 16, "Regular", WHITE, lh=1.3), y + 26) + 14   # wrapped items push down
assert y < PH - 20, f"specs overflow the slide: {y}"

path = os.path.join(OUT, "CGSO2026_Cadangan_Kulit_Buku.pdf")
doc.save(path, garbage=3, deflate=True)
for f in os.listdir(OUT):
    if f.startswith("_deck_"):
        os.remove(os.path.join(OUT, f))
print("deck", path, len(doc), "pages")
