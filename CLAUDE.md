# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Ini adalah folder latihan LangGraph milik pengguna (bukan proyek produksi): pipeline multi-agent yang membuat artikel blog dari sebuah topik. LLM dipanggil lewat `langchain_openai.ChatOpenAI` yang diarahkan ke OpenRouter.

Karena ini untuk belajar, saat membantu:
- Jelaskan konsep LangGraph yang dipakai (state, node, edge, conditional edge, reducer, dsb.) secara singkat, dan jaga kode tetap sederhana dan mudah dibaca.
- Lanjutkan dengan gaya yang sudah ada (satu class per agent, node tipis, template prompt di `prompts/`) kecuali pengguna minta refactor.
- Komentar/docstring di kode ditulis dalam bahasa Indonesia; respons ke pengguna dalam bahasa Indonesia.

## Commands

```bash
python -m venv .venv && .venv\Scripts\activate   # venv ada di .venv/ (gitignored)
pip install -r requirements.txt
python main.py                                     # jalankan workflow penuh (topik di-hardcode di main.py)
python -m tests.test_router                        # jalankan satu "test"
```

Konfigurasi dibaca dari `.env` (lihat `.env.example`): `OPENROUTER_API_KEY` dan `OPENROUTER_MODEL` wajib ada (`config/settings.py` membuat `Settings()` saat import, jadi import `config.*` gagal tanpa keduanya); `OPENROUTER_BASE_URL` opsional.

Tidak ada pytest/lint. File di `tests/` adalah skrip mandiri dengan `main()` yang mencetak hasil (tanpa assertion), dan sebagian besar (`test_evaluator`, `test_generator`, ...) memanggil LLM sungguhan. Jalankan dari root repo agar import top-level (`graph`, `agents`, `config`) ter-resolve.

## Architecture

- `graph/state.py` — `ArticleState` (TypedDict) adalah shared state; hanya `topic` yang wajib, sisanya `NotRequired`. Field `image_prompt`, `image_path`, `output_path` sudah dideklarasikan untuk langkah yang belum dibuat; folder kosong `memory/`, `output/`, `prompts/`, `services/` juga masih placeholder.
- `graph/workflow.py` — membangun `StateGraph`: `START → orchestrator → generator → evaluator → (conditional)`; conditional: `approved` → `image_prompt` → `human_review` → (`approved` → `save` → `END` | `rejected` → `END`), `max_revisions` → `END`, `rejected` → kembali ke `generator`.
- `graph/nodes.py` — fungsi node tipis: buat instance agent lalu panggil `agent.run(state)`.
- `agents/` — satu class per agent (`OrchestratorAgent` → `outline`, `GeneratorAgent` → `article`, `EvaluatorAgent` → `feedback`/`approved`). Template prompt diambil dari `prompts/article_prompts.py`. Evaluator memakai `with_structured_output(models.evaluation.EvaluationResult)`.
- `graph/router.py` — `route_after_evaluation` mengembalikan `"approved"`/`"rejected"`/`"max_revisions"`; `route_after_human_review` mengembalikan `"approved"`/`"rejected"`.

## Dokumentasi

`docs/index.html` adalah dokumentasi interaktif satu file (tanpa dependensi, buka langsung di browser): diagram workflow yang bisa diklik, simulator alur, kartu agent, tabel state, dan cuplikan kode beranotasi. Perbarui jika alur graph atau field state berubah (data diagram/simulator ada di bagian `<script>` paling bawah).

## Status & rencana latihan berikutnya

Kondisi sekarang:
- Loop revisi sudah ada: rute `rejected` kembali ke `generator`, yang memakai `feedback` + draft sebelumnya di prompt dan menambah `revision_count`. `route_after_evaluation` mengembalikan `"max_revisions"` (→ `END`) bila `revision_count >= MAX_REVISIONS` (di `graph/router.py`, saat ini 2), jadi ada paling banyak 3 draft.

Langkah lanjutan yang masuk akal (urutan kira-kira dari paling dasar):
1. ~~Loop revisi~~ (selesai).
2. ~~Simpan artikel yang disetujui~~ (selesai): node `save` memanggil `services/storage.py::save_article`, menulis `output/<slug-topik>-<waktu>.md` dan mengisi `output_path`. Rute `max_revisions` → `END` tanpa menyimpan.
3. ~~Node `image_prompt`~~ (selesai): `ImagePromptAgent` (`agents/image_prompt.py`) membuat prompt gambar cover dari artikel yang disetujui. Yang belum: membuat gambarnya (`image_path`) lewat model image generation; `image_prompt` juga belum ikut tersimpan ke file.
4. ~~Pindahkan prompt ke `prompts/`~~ (selesai): semua template ada di `prompts/article_prompts.py` dan diisi lewat `str.format()` (jangan tulis `{ }` literal di template). `services/` baru berisi `storage.py`; pembuatan LLM masih di `config/llm.py`, dan akan pindah ke `services/` bila nanti ada panggilan eksternal lain (mis. image generation).
5. Eksplorasi fitur LangGraph lain:
   - ~~Checkpointer~~ (selesai, SQLite): `create_workflow(checkpointer=...)`; `main.py` memakai `SqliteSaver` dengan database `memory/checkpoints.db` (gitignored) dan `thread_id` baru tiap run (memakai ulang thread lama membawa `feedback`/`revision_count` lama ke run baru), lalu mencetak `get_state_history`. `python main.py <thread_id>` hanya menampilkan riwayat run lama dari database, tanpa memanggil LLM. `tests/test_checkpointer.py` (in-memory) dan `tests/test_sqlite_checkpointer.py` (persistensi ke disk) memakai agent palsu, tanpa LLM. Paket `langgraph-checkpoint-sqlite` dipasang dengan `pip --trusted-host` karena error SSL di mesin ini; jika `pip install -r requirements.txt` gagal dengan `CERTIFICATE_VERIFY_FAILED`, itu penyebabnya.
   - ~~Streaming~~ (selesai): `main.py` memakai `workflow.stream(..., stream_mode="updates")` dan mencetak tiap node yang selesai beserta field yang diubahnya; state akhir diambil lewat `workflow.get_state(config).values` karena `stream()` tidak mengembalikannya. `tests/test_streaming.py` (agent palsu) memeriksa urutan node termasuk loop revisi.
   - ~~Human-in-the-loop~~ (selesai): node `human_review` (`graph/nodes.py`) memanggil `interrupt(payload)` sehingga graph berhenti setelah `image_prompt`; `main.py` (`run_stream` + `ask_approval`) menanyakan y/n di terminal lalu melanjutkan dengan `Command(resume=True/False)` pada `thread_id` yang sama. `y` → `save`, selain itu → `END` tanpa menyimpan (`human_approved` di state). Node dijalankan ulang dari awal saat resume, jadi jangan taruh efek samping sebelum `interrupt()`. Memanggil `invoke`/`stream` tanpa resume akan berhenti di `human_review`; tes yang menjalankan graph penuh harus melanjutkan dengan `Command(resume=True)`. Tes: `tests/test_human_review.py`.

## Catatan kode yang perlu diketahui

- Agent mengembalikan partial state update (LangGraph yang menggabungkan).
- `agents/image_prompt.py` meng-import `BaseChatModel` dengan benar (contoh yang bisa ditiru).
- `agents/generator.py` dan `agents/orchestrator.py` memberi anotasi `BaseChatModel` tanpa meng-import-nya (tetap jalan karena anotasi pada assignment `self.x:` tidak dievaluasi saat runtime); tambahkan import dari `langchain_core.language_models` jika ingin dirapikan.
- Bahasa prompt campur (generator Indonesia, lainnya Inggris).
