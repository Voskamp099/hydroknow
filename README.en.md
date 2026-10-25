# HydroKnow · 氢知 — enterprise knowledge assistant for hydrogen energy

An enterprise question-answering service built on the company's own public material.
The corpus is three PDFs — a company profile sheet, a product one-pager and the 2025
brochure — and the answers are retrieved from those documents, with the source and a
confidence score attached.

Built for the Enterprise knowledge and service assistant.

Online demo (stable, GitHub Pages): https://voskamp099.github.io/hydroknow/

[English](README.en.md) · [简体中文](README.md)

## What it does

- **Knowledge base** — loads the enterprise PDFs, cleans the extracted text and splits it
  into chunks.
- **Hybrid retrieval** — BM25 for exact keyword matches plus TF-IDF char n-grams for
  fuzzy wording, fused with a weighted score. Character-level features mean Chinese text
  works without a tokenizer.
- **Structured answers** — a key-point list, the source documents with their match scores,
  and a confidence value, instead of one long paragraph.
- **Web chat** — a small Flask chat interface that shows the sources behind each answer.
- **CLI batch mode** — runs a set of prepared questions, prints the answers and writes a
  static `demo.html` plus a machine-readable `cli_results.json`.
- **Pluggable LLM** — the generator is an offline stub by default; swapping in a real
  model is a one-function change.

## Quick start

```bash
pip install -r requirements.txt
```

Web mode:

```bash
python app.py     # then open http://127.0.0.1:5000
```

CLI mode:

```bash
python run.py                                        # run the prepared questions
python run.py --question "When was the company founded?"
```

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | chat interface |
| POST | `/api/ask` | ask a question, body `{"question": "..."}` |
| GET | `/api/stats` | corpus statistics (documents, chunks) |
| GET | `/api/suggest` | suggested questions |

## How retrieval works

```
question
   │
   ▼
PDF load ──▶ chunking ──▶ hybrid retrieval ──▶ answer generation
 (pdfminer)  (~400 chars)  (BM25 + TF-IDF)    (pluggable LLM)
                                          │
                                          ▼
                              answer + key points + sources + confidence
```

- **BM25** — exact keyword matching over character bigrams, so Chinese needs no tokenizer.
- **TF-IDF** — character n-grams (1, 2) with cosine similarity, covering phrasings that
  do not match literally.
- **Fusion** — `score = 0.6 × normalised BM25 + 0.4 × normalised TF-IDF`.

## Plugging in a real model

The generator is an offline stub: it extracts and structures the relevant sentences from
the retrieved chunks without calling any API. To use a real model, change one function in
`rag/generator.py`:

```python
def generate_answer(question, retrieved_chunks):
    context = "\n\n".join(c["text"] for c, _ in retrieved_chunks)
    prompt = f"Answer the question using only the context.\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
    answer_text = your_llm_client.chat(prompt)   # replace with your model call
    return {"answer": answer_text, "key_points": [...], "sources": [...], "confidence": ...}
```

The signature stays the same, so the web and CLI paths need no changes.

## Data

- Source: three publicly released PDFs from the company (company profile, product
  one-pager, 2025 brochure).
- The one-pager is an image-based design file, so text extraction from it returns noise;
  that content is filtered out automatically. The usable material comes from the profile
  sheet and the brochure.

## Known limits

1. **The generator is a stub** — no model call yet, so answers are structured extractions
   rather than composed answers.
2. **Thin corpus** — three documents. A real deployment would add FAQs, product manuals
   and technical documentation.
3. **Lexical retrieval** — BM25 and TF-IDF match words, not meaning. Embedding models
   would improve it.
4. **No persistence** — the PDFs are reloaded and re-indexed on every start (about two to
   three seconds).
