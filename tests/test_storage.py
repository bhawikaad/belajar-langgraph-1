import tempfile
from pathlib import Path

from services.storage import save_article, slugify


def main():
    # slugify: teks bebas -> aman untuk nama file
    print("Slug:", slugify("Agentic AI in 2027!"))  # agentic-ai-in-2027
    print("Slug kosong:", slugify("???"))  # artikel

    # Simpan ke folder sementara supaya folder output/ asli tidak terisi tes.
    with tempfile.TemporaryDirectory() as tmp:
        path = save_article("Agentic AI in 2027", "# Judul\n\nIsi artikel.", Path(tmp))

        print("Path:", path)
        print("Isi:", Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
