# HydroKnow · Enterprise knowledge assistant

[English](README.en.md) · [简体中文](README.md)

> A local RAG assistant for your own documents (assistant persona: 小知)

**Live demo (GitHub Pages)**: https://voskamp099.github.io/hydroknow/

## What it is

A knowledge assistant that runs entirely offline. It loads the documents in `data/`, extracts and cleans the text, splits it into semantic chunks, retrieves the most relevant passages with a hybrid BM25 + TF-IDF search, and assembles an answer with its sources and a confidence score.

The corpus shipped in `data/` is a **fictional sample** — a made-up hydrogen company — so the whole retrieval and answer path can be demonstrated without shipping anyone else's material. To use it on your own documents, drop your own PDFs, Markdown or plain-text files into `data/` and re-run.

This repository contains no third-party material. The sample corpus, the sample questions and the retrieval results are all generated from self-written content.

## Features

- **Corpus loading**: PDF, Markdown and plain text; text cleaning and semantic chunking
- **Hybrid retrieval**: BM25 + TF-IDF fused with a weight, no Chinese word segmenter needed
- **Answering**: key sentences extracted from the retrieved passages, with sources and confidence
- **Web chat**: live Q&A with the retrieved sources and match scores
- **CLI demo**: runs a batch of preset questions and writes a static demo.html
- **Pluggable LLM**: the default generator is an offline stub; replace one function to call a real model

## Layout

```
.
├── app.py                 # Flask web app
├── build_static.py        # builds the self-contained static demo into dist/index.html
├── data/                  # corpus directory: PDF / Markdown / plain text
├── dist/index.html        # self-contained static demo
├── run.py                 # CLI entry point
├── run_cli.py             # CLI batch mode, writes demo.html
├── rag/                   # the RAG engine
│   ├── loader.py          # document loading, cleaning, chunking
│   ├── retriever.py       # hybrid BM25 + TF-IDF retrieval
│   ├── generator.py       # answer generation (pluggable)
│   └── pipeline.py        # RAGEngine wiring
├── templates/index.html   # chat UI
└── static/                # front-end assets
```

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python app.py            # web UI at http://127.0.0.1:5000
python run_cli.py        # CLI batch run, writes demo.html
python build_static.py   # self-contained static demo in dist/index.html
```

PyMuPDF is only needed for PDF corpora; Markdown and plain text work without it.

## Use it with your own documents

1. Put your files in `data/` (`.pdf`, `.md` or `.txt`).
2. Update the preset questions in `run_cli.py` and `app.py`.
3. Re-run `python run_cli.py` and `python build_static.py`, then `bash publish.sh`.

## Design notes

- **Why hybrid retrieval**: BM25 handles rare terms and proper nouns, TF-IDF captures the overall term distribution. With Chinese text a character n-gram approximation works without a segmenter, and fusing the two is steadier than either alone.
- **Why no LLM by default**: the offline stub keeps the project runnable and reproducible anywhere; to call a real model, replace `generate_answer()` in `rag/generator.py` and keep the signature `generate_answer(question, retrieved_chunks) -> str`.
- **Why PyMuPDF for PDFs**: pdfminer replaces digits with U+FFFD when a font has no ToUnicode mapping, which loses the characters irreversibly. PyMuPDF keeps them in the private use area, where `_repair_pua_digits` can restore them.
