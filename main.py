import sys
import uuid
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from graph.workflow import create_workflow

# File database checkpoint, disimpan di folder memory/ (diabaikan git).
# Dihitung dari lokasi file ini agar tidak bergantung pada folder kerja.
DB_PATH = Path(__file__).resolve().parent / "memory" / "checkpoints.db"


def print_history(workflow, config) -> None:
    """Cetak semua snapshot sebuah thread, dari yang terlama ke terbaru."""

    # get_state_history() mengembalikan snapshot dari yang terbaru ke terlama,
    # jadi dibalik agar urutannya sesuai jalannya workflow.
    for snapshot in reversed(list(workflow.get_state_history(config))):
        step = snapshot.metadata["step"]
        # snapshot.next = node yang akan dijalankan berikutnya (kosong = selesai)
        print(f"step {step}: next={snapshot.next}, fields={sorted(snapshot.values)}")


def run_stream(workflow, graph_input, config):
    """
    Jalankan/lanjutkan graph sambil mencetak progres tiap node.

    graph_input: state awal (run baru) atau Command(resume=...) (melanjutkan
    graph yang berhenti). Mengembalikan payload interrupt() jika graph
    berhenti menunggu manusia, atau None jika sudah selesai.
    """
    for update in workflow.stream(graph_input, config, stream_mode="updates"):
        # Saat interrupt(), stream menghasilkan item khusus berkunci
        # "__interrupt__" yang berisi payload dari interrupt() di node.
        if "__interrupt__" in update:
            return update["__interrupt__"][0].value

        for node_name, changes in update.items():
            print(f"[{node_name}] selesai, mengubah: {sorted(changes)}")

    return None


def ask_approval(payload: dict) -> dict:
    """
    Tampilkan artikel di terminal dan minta keputusan dari manusia.

    Mengembalikan {"approved": True} jika setuju, atau
    {"approved": False, "note": "..."} jika menolak (artikel akan ditulis
    ulang; catatan opsional dikirim ke penulis sebagai feedback).
    """
    print("\n=== MENUNGGU PERSETUJUAN ===")
    print(payload["article"])
    print("\nPrompt gambar:", payload["image_prompt"])

    answer = input(f"\n{payload['pesan']} (y/n): ").strip().lower()
    if answer == "y":
        return {"approved": True}

    # Selain "y" dianggap menolak -> graph kembali ke generator.
    note = input("Catatan perbaikan untuk penulis (opsional, Enter untuk lewati): ").strip()
    print("Artikel ditolak, menulis ulang...\n")
    return {"approved": False, "note": note}


def ask_topic() -> str | None:
    """
    Tanyakan topik artikel ke user lewat terminal.

    Input kosong (hanya spasi/Enter) ditolak dan ditanya lagi. Mengembalikan
    None jika user membatalkan (Ctrl+C) atau input sudah habis (EOF),
    misalnya program dijalankan tanpa terminal interaktif.
    """
    while True:
        try:
            # .strip() membuang spasi di awal/akhir agar "   " dianggap kosong.
            topic = input("Silakan masukkan topik artikel: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nDibatalkan.")
            return None

        if topic:
            return topic

        print("Topik tidak boleh kosong, coba lagi.")


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # SqliteSaver menyimpan checkpoint ke file SQLite, jadi tetap ada setelah
    # program selesai (beda dengan InMemorySaver yang hilang bersama proses).
    # from_conn_string dipakai dengan `with` agar koneksi ditutup otomatis.
    with SqliteSaver.from_conn_string(str(DB_PATH)) as checkpointer:
        workflow = create_workflow(checkpointer=checkpointer)

        # Mode lihat riwayat: `python main.py <thread_id>` menampilkan
        # checkpoint run lama yang tersimpan di database, tanpa menjalankan LLM.
        if len(sys.argv) > 1:
            config = {"configurable": {"thread_id": sys.argv[1]}}
            print(f"=== CHECKPOINT HISTORY thread {sys.argv[1]} ===")
            print_history(workflow, config)
            return

        # Topik diminta dari user saat program jalan (tidak lagi hardcoded).
        topic = ask_topic()
        if topic is None:
            return

        initial_state = {
            "topic": topic
        }

        # thread_id = "nama sesi" untuk checkpoint. Semua checkpoint dengan
        # thread_id yang sama dianggap satu run yang berlanjut. Kita buat id
        # baru tiap run: kalau thread lama dipakai ulang, nilai lama (mis.
        # feedback, revision_count) masih ada di state dan terbawa ke run baru.
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        print("=== INITIAL STATE ===")
        print(initial_state)
        print(f"thread_id: {thread_id}")

        # stream() menjalankan workflow seperti invoke(), tapi menghasilkan
        # (yield) output setiap kali sebuah node selesai, jadi progres bisa
        # dilihat langsung tanpa menunggu seluruh workflow berakhir.
        # stream_mode="updates": tiap item berupa {nama_node: field_yang_diubah_node_itu}.
        # Dengan checkpointer, config yang berisi thread_id tetap wajib.
        print("\n=== PROGRESS ===")
        pending = run_stream(workflow, initial_state, config)

        # Selama graph berhenti karena interrupt(), tanyakan keputusan ke
        # manusia lalu lanjutkan graph dengan Command(resume=keputusan).
        # Loop dipakai karena satu run bisa berhenti lebih dari sekali:
        # tiap kali manusia menolak, artikel ditulis ulang dan kembali
        # menunggu persetujuan sampai manusia menjawab "y".
        while pending is not None:
            decision = ask_approval(pending)
            pending = run_stream(workflow, Command(resume=decision), config)

        # stream() tidak mengembalikan state akhir; ambil dari checkpointer.
        final_state = workflow.get_state(config).values

        print("\n=== FINAL STATE ===")
        print(final_state)

        print("\n=== CHECKPOINT HISTORY (terlama -> terbaru) ===")
        print_history(workflow, config)

        print(f"\nLihat lagi nanti dengan: python main.py {thread_id}")


if __name__ == "__main__":
    main()
