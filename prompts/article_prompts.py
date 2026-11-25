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

Bahasa:
- Semua INSTRUKSI prompt ditulis dalam bahasa Inggris (model biasanya paling
  patuh pada instruksi berbahasa Inggris).
- Bahasa HASIL (outline, artikel, feedback) ditentukan terpisah lewat
  placeholder {language}, yang diisi dari settings.output_language.
- Prompt gambar sengaja selalu berbahasa Inggris, tanpa {language}.
"""

# ---------------------------------------------------------------
# Orchestrator: membuat outline dari topik
# Placeholder: {topic}, {language}
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

Write the outline in {language}.
Return only the article outline.
"""

# ---------------------------------------------------------------
# Generator: menulis artikel dari topik + outline
# Placeholder: {topic}, {outline}, {language}
# ---------------------------------------------------------------
GENERATOR_PROMPT = """
You are a professional article writer.

Write a blog article based on the following topic and outline.

Topic:
{topic}

Outline:
{outline}

Write the complete article in {language}, formatted as Markdown.
"""

# Tambahan untuk GENERATOR_PROMPT ketika artikel ditolak dan perlu direvisi.
# Bahasanya sudah ditentukan oleh GENERATOR_PROMPT, jadi di sini cukup
# meminta bahasa dan format yang sama.
# Placeholder: {previous_article}, {feedback}
GENERATOR_REVISION_PROMPT = """
The previous draft was rejected by a reviewer. Improve that draft
based on the feedback below.

Previous draft:
{previous_article}

Reviewer feedback:
{feedback}

Rewrite the complete, improved article. Keep the same language and Markdown format.
"""

# ---------------------------------------------------------------
# Evaluator: menilai artikel (output-nya terstruktur, lihat EvaluationResult)
# Placeholder: {article}, {language}
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
- feedback: concise and actionable feedback, written in {language}
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
