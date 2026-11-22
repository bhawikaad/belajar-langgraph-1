"""
Service untuk menyimpan hasil artikel ke file.

Logika I/O file sengaja dipisah dari node/agent supaya:
- node tetap tipis (hanya "menjembatani" state ke fungsi),
- fungsi ini mudah dites tanpa menjalankan LangGraph maupun LLM.
"""

import re
from datetime import datetime
from pathlib import Path

# Folder output = <root proyek>/output.
# __file__ adalah path file ini (services/storage.py), jadi:
#   .parent         -> services/
#   .parent.parent  -> root proyek
# Dengan cara ini lokasi output tidak bergantung pada
# folder tempat Anda menjalankan `python main.py`.
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def slugify(text: str) -> str:
    """
    Ubah teks jadi aman dipakai sebagai nama file.
    Contoh: "Agentic AI in 2027!" -> "agentic-ai-in-2027"
    """
    # Huruf kecil semua, lalu ganti setiap deretan karakter selain
    # huruf/angka dengan satu tanda "-".
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower())

    # Buang "-" di awal/akhir. Jika kosong (mis. topik hanya simbol),
    # pakai nama cadangan "artikel".
    return slug.strip("-") or "artikel"


def save_article(topic: str, article: str, output_dir: Path = OUTPUT_DIR) -> str:
    """
    Simpan artikel sebagai file Markdown, lalu kembalikan path file-nya.

    Nama file: <slug-topik>-<tanggal-jam>.md, sehingga menjalankan
    workflow berkali-kali tidak saling menimpa file lama.
    """
    # Buat folder output jika belum ada.
    # parents=True : buat juga folder induk bila perlu.
    # exist_ok=True: jangan error kalau foldernya sudah ada.
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_path = output_dir / f"{slugify(topic)}-{timestamp}.md"

    # encoding utf-8 penting di Windows agar karakter non-ASCII
    # (mis. tanda kutip melengkung, emoji) tidak error.
    file_path.write_text(article, encoding="utf-8")

    # State LangGraph sebaiknya berisi tipe sederhana, jadi kita simpan str.
    return str(file_path)
