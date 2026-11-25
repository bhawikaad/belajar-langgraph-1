import tempfile
from pathlib import Path

from services.storage import save_article, slugify


def main():
    # slugify: teks bebas -> aman untuk nama file
    print("Slug:", slugify("Agentic AI in 2027!"))  # agentic-ai-in-2027
    print("Slug kosong:", slugify("???"))  # artikel

    # Simpan ke folder sementara supaya folder output/ asli tidak terisi tes.
    with tempfile.TemporaryDirectory() as tmp:
        path = save_article(
            "Agentic AI in 2027",
            "# Judul\n\nIsi artikel.",
            Path(tmp),
            outline="1. Pendahuluan\n2. Penutup",
            image_prompt="A calm cover scene of ...",
        )

        print("Path:", path)
        print("Isi:\n" + Path(path).read_text(encoding="utf-8"))

        # Tanpa outline: bagian Outline dilewati, topik tetap ada.
        path2 = save_article("Topik Saja", "Isi.", Path(tmp))
        content2 = Path(path2).read_text(encoding="utf-8")
        assert "**Topik:** Topik Saja" in content2
        assert "### Outline" not in content2
        assert "### Prompt Gambar" not in content2
        print("OK (tanpa outline)")


if __name__ == "__main__":
    main()
