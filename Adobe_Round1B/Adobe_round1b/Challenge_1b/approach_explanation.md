## Adobe India Hackathon 2025 – Challenge 1B: Multi-Collection PDF Analyzer

### Objective

The goal of Challenge 1B is to process 3–10 related PDFs in each collection and generate structured JSON output containing the most relevant **sections** and **subsections** tailored to a defined **persona** and **job-to-be-done**. The solution must meet stringent constraints: **offline execution**, **CPU-only**, **model size ≤1GB**, and **≤60 seconds runtime** for 3–5 collections.

---

### Methodology

Our solution is built using Python and SentenceTransformers with a lightweight `all-MiniLM-L6-v2` model (approx. 80MB). The system is divided into two core modules:

- `main.py` orchestrates parallel execution using `ProcessPoolExecutor`.
- `pdf_analyzer.py` handles PDF parsing, section/subsection ranking, and output formatting.

Each collection is independently processed in parallel.

---

## 📘 Section Extraction

PDF parsing is handled via `PyMuPDF`, allowing rich text extraction and layout analysis:

- **Structured PDFs**: Section headers are detected using font flags and hierarchy.
- **Fallback mode**: For unstructured PDFs, the system slices long pages into paragraph-sized chunks (~1000 characters).

Extracted sections are annotated with:
- Document name
- Page number
- Section title
- Section content

---

## Semantic Ranking

A combined semantic query is formed using the input:  
**`"{persona}: {job_to_be_done}"`**

- All section texts are embedded using batch encoding for efficiency.
- Cosine similarity scores between query and sections are computed.
- A **penalty function** reduces scores for:
  - Duplicate section titles
  - Overrepresented documents
- Only top-scoring sections above a **relevance threshold** are retained.
- Diversity across documents is enforced during ranking.

---

## Subsection Analysis

Top-ranked sections are decomposed into smaller paragraphs. Each paragraph is:
- Cleaned and length-filtered
- Embedded and scored against the query
- Deduplicated using a 100-character semantic fingerprint

The system selects up to **10 unique, high-relevance** refined paragraphs for final output.

---

## Optimizations

- **Multiprocessing**: Parallel handling of all collections using `ProcessPoolExecutor`.
- **Batch Embedding**: Improves speed using tunable embedding batch sizes.
- **Robust Fallback**: Automatically switches to flat-mode parsing for noisy PDFs.
- **Deduplication & Diversity**: Ensures unique and context-rich selections from multiple sources.

---

## Output & Compliance

The generated JSON strictly adheres to the specified structure:
- `metadata`: persona, job, documents, timestamp, runtime
- `sections`: 3–5 ranked entries with source and page
- `subsection_analysis`: 5–10 unique, relevant excerpts

The solution runs **entirely offline**, within **≤1GB memory**, and completes in **≤60s** for 5 collections (~28–38s average). It achieves **high section and subsection relevance scores** and is fully compliant with all challenge constraints.