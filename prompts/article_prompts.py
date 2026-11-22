"""
Kumpulan template prompt untuk semua agent.

Setiap prompt berupa string dengan placeholder seperti {topic}.
Agent mengisinya lewat str.format(), contoh:

    ORCHESTRATOR_PROMPT.format(topic="Agentic AI in 2027")

Dengan memisahkan prompt dari kode agent:
- mengubah wording prompt tidak perlu menyentuh logika agent,
- semua prompt bisa dibaca dan dibandingkan di satu tempat.

Catatan: karena memakai str.format(), jangan tulis kurung kurawal { }
literal di template (kalau perlu, tulis dua kali: {{ }}).
"""

# ---------------------------------------------------------------
# Orchestrator: membuat outline dari topik
# Placeholder: {topic}
# ---------------------------------------------------------------
ORCHESTRATOR_PROMPT = """
You are an article planning assistant.

Create a clear and logical outline for an article about the following topic:

Topic:
{topic}

The outline should:
- Have a clear introduction
- Contain several logical main sections
- Have a clear conclusion
- Be suitable as a structure for a full article

Return only the article outline.
"""

# ---------------------------------------------------------------
# Generator: menulis artikel dari topik + outline
# Placeholder: {topic}, {outline}
# ---------------------------------------------------------------
GENERATOR_PROMPT = """
Anda adalah seorang penulis artikel profesional.

Buat artikel blog berdasarkan topik dan outline berikut.

Topik:
{topic}

Outline:
{outline}

Tulis artikel lengkap dalam format Markdown.
"""

# Tambahan untuk GENERATOR_PROMPT ketika artikel ditolak dan perlu direvisi.
# Placeholder: {previous_article}, {feedback}
GENERATOR_REVISION_PROMPT = """
Draft sebelumnya ditolak oleh evaluator. Perbaiki draft tersebut
berdasarkan feedback berikut.

Draft sebelumnya:
{previous_article}

Feedback evaluator:
{feedback}

Tulis ulang artikel lengkap yang sudah diperbaiki.
"""

# ---------------------------------------------------------------
# Evaluator: menilai artikel (output-nya terstruktur, lihat EvaluationResult)
# Placeholder: {article}
# ---------------------------------------------------------------
EVALUATOR_PROMPT = """
You are an article evaluator.

Evaluate the following article.

Focus on:
- clarity
- structure
- relevance to the topic
- completeness
- readability

Article:
{article}

Return:
- score: a score from 1 to 10
- feedback: concise and actionable feedback
- approved: true if the article is good enough to be accepted, otherwise false
"""

# ---------------------------------------------------------------
# Image prompt: membuat prompt gambar cover dari artikel
# Placeholder: {topic}, {article}
# ---------------------------------------------------------------
IMAGE_PROMPT_PROMPT = """
You are an art director who writes prompts for AI image generation.

Write ONE image prompt for the cover image of the article below.

Topic:
{topic}

Article:
{article}

The prompt should:
- Describe a single clear scene or concept that represents the article
- Mention the visual style, mood, colors, and composition
- Not contain any text, words, or letters in the image
- Be 2-4 sentences long

Return only the image prompt.
"""
