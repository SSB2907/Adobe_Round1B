import os
import re
import fitz 
import logging
from sentence_transformers import util
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === SECTION EXTRACTION CODE ===
def extract_sections_from_pdf(pdf_path_str):
    try:
        doc = fitz.open(pdf_path_str)
        sections = []
        current_title = "Introduction"
        current_text_lines = []
        current_page = 1
        found_headings = False

        def flush():
            nonlocal current_text_lines, current_page, current_title
            full_text = "\n".join(current_text_lines).strip()
            if full_text:
                sections.append({
                    "document": os.path.basename(pdf_path_str),
                    "section_title": current_title,
                    "section_text": full_text,
                    "page_number": current_page
                })
            current_text_lines.clear()

        for page_num, page in enumerate(doc, 1):
            blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_SEARCH)["blocks"]
            for block in blocks:
                if block["type"] == 0:
                    for line in block["lines"]:
                        text = " ".join(span["text"] for span in line["spans"]).strip()
                        is_heading = len(line["spans"]) == 1 and (line["spans"][0].get("flags", 0) & 16)
                        if is_heading and text:
                            flush()
                            current_title = text
                            current_page = page_num
                            found_headings = True
                        elif text:
                            current_text_lines.append(text)
        flush()

        # === Fallback: Flat PDFs ===
        if not found_headings:
            logging.info(f" No headings in {os.path.basename(pdf_path_str)}, using paragraph fallback.")
            sections = []
            for page_num, page in enumerate(doc, 1):
                text = page.get_text().strip()
                if text:
                    for idx, chunk in enumerate([text[i:i+1000] for i in range(0, len(text), 1000)]):
                        sections.append({
                            "document": os.path.basename(pdf_path_str),
                            "section_title": f"Page {page_num} - Part {idx+1}",
                            "section_text": chunk,
                            "page_number": page_num
                        })
        return sections
    except Exception as e:
        logging.error(f"Failed to extract from {pdf_path_str}: {e}")
        return []

# === ANALYZER CODE ===
class PDFAnalyzer:
    def __init__(self, config, persona, job, model):
        self.config = config
        self.persona = persona
        self.job = job
        self.model = model
        self.query_embedding = model.encode(f"{persona}: {job}", convert_to_tensor=True)
        self.model.max_seq_length = 512

    def _clean(self, text):
        return re.sub(r'\s+', ' ', text.strip())

    def _split_paragraphs(self, text):
        return [self._clean(p) for p in re.split(r'\n{2,}', text) if len(p.strip()) > 30]

    def embed_sections(self, sections):
        texts = [s["section_text"] for s in sections]
        return self.model.encode(texts, convert_to_tensor=True, batch_size=self.config["embedding_batch_size"], show_progress_bar=False)

    def rank_sections(self, sections, embeddings, top_k=5):
        sims = util.cos_sim(self.query_embedding, embeddings)[0].cpu().numpy()
        for i, s in enumerate(sections):
            s["score"] = float(sims[i])

        sorted_sections = sorted(sections, key=lambda x: x["score"], reverse=True)
        ranked, seen_titles, seen_docs = [], set(), set()

        for sec in sorted_sections:
            title, doc, score = sec["section_title"].lower(), sec["document"], sec["score"]
            penalty = 0
            if title in seen_titles: penalty += self.config["penalty_weight"]
            if doc in seen_docs: penalty += self.config["penalty_weight"]
            final_score = score - penalty
            if final_score >= self.config["relevance_threshold"]:
                if title not in seen_titles and doc not in seen_docs:
                    ranked.append({
                        "document": doc,
                        "page_number": sec["page_number"],
                        "section_title": sec["section_title"],
                        "importance_rank": len(ranked) + 1
                    })
                    seen_titles.add(title)
                    seen_docs.add(doc)
            if len(ranked) >= top_k:
                break
        return ranked, sorted_sections

    def extract_subsections(self, sorted_sections):
        subs = []
        for sec in sorted_sections:
            if sec["score"] >= self.config["relevance_threshold"]:
                for para in self._split_paragraphs(sec["section_text"]):
                    subs.append({
                        "document": sec["document"],
                        "refined_text": para,
                        "page_number": sec["page_number"]
                    })
        return subs

    def rank_subsections(self, subsections, top_k=10):
        if not subsections: return []
        texts = [s["refined_text"] for s in subsections]
        embeddings = self.model.encode(texts, convert_to_tensor=True, show_progress_bar=False, batch_size=self.config["embedding_batch_size"])
        sims = util.cos_sim(self.query_embedding, embeddings)[0].cpu().numpy()

        for i, s in enumerate(subsections):
            s["score"] = float(sims[i])

        sorted_subs = sorted(subsections, key=lambda x: x["score"], reverse=True)
        final, seen = [], set()

        for s in sorted_subs:
            key = s["refined_text"][:100].lower()
            if key not in seen:
                seen.add(key)
                final.append({
                    "document": s["document"],
                    "refined_text": s["refined_text"],
                    "page_number": s["page_number"]
                })
            if len(final) >= top_k:
                break
        return final

    def process_analysis(self, sections):
        if not sections:
            return {"sections": [], "subsection_analysis": []}
        embeddings = self.embed_sections(sections)
        top_sections, sorted_sections = self.rank_sections(sections, embeddings)
        top_subs = self.rank_subsections(self.extract_subsections(sorted_sections))
        return {
            "sections": top_sections,
            "subsection_analysis": top_subs
        }
