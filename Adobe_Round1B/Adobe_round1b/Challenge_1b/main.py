import os
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from sentence_transformers import SentenceTransformer
from pdf_analyzer import extract_sections_from_pdf, PDFAnalyzer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def _find_pdf_paths(collection_path: Path) -> list:
    pdf_dir = collection_path / "PDFs"
    return list(pdf_dir.glob("*.pdf")) if pdf_dir.exists() else list(collection_path.glob("*.pdf"))

def is_valid_collection(path: Path) -> bool:
    return (path / "challenge1b_input.json").exists() and _find_pdf_paths(path)

def process_collection(collection_path: Path, output_dir: Path, model_path: str, config: dict):
    start_time = time.time()
    try:
        # Load persona and job config
        with open(collection_path / "challenge1b_input.json", "r", encoding="utf-8") as f:
            user_config = json.load(f)

        persona = user_config.get("persona", {}).get("role") if isinstance(user_config.get("persona"), dict) else str(user_config.get("persona", ""))
        job = user_config.get("job_to_be_done", {}).get("task") if isinstance(user_config.get("job_to_be_done"), dict) else str(user_config.get("job_to_be_done", ""))

        # Collect PDF files
        pdf_files = _find_pdf_paths(collection_path)
        logging.info(f"Extracting from {len(pdf_files)} PDFs in '{collection_path.name}'...")

        # Parallel section extraction
        sections = []
        with ProcessPoolExecutor(max_workers=min(8, len(pdf_files))) as pool:
            futures = [pool.submit(extract_sections_from_pdf, str(p)) for p in pdf_files]
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        sections.extend(result)
                except Exception as e:
                    logging.warning(f"Error extracting from a PDF: {e}")

        # Load model & analyzer
        model = SentenceTransformer(model_path)
        analyzer = PDFAnalyzer(config=config, persona=persona, job=job, model=model)
        result = analyzer.process_analysis(sections)

        # Write output JSON
        output = {
            "metadata": {
                "input_documents": sorted([p.name for p in pdf_files]),
                "persona": persona,
                "job_to_be_done": job,
                "processing_timestamp": datetime.now().isoformat(),
                "processing_time_seconds": round(time.time() - start_time, 2)
            },
            "sections": result.get("sections", []),
            "subsection_analysis": result.get("subsection_analysis", [])
        }

        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / f"{collection_path.name}_output.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        logging.info(f"Completed '{collection_path.name}' in {output['metadata']['processing_time_seconds']} seconds.")
    except Exception as e:
        logging.error(f"Failed to process '{collection_path.name}': {e}")

def main():
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    print("\nChallenge 1B Optimized Analyzer (Shared Model + PDF Parallelism)\n")

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, default="./input")
    parser.add_argument("--output_dir", type=str, default="./output")
    parser.add_argument("--relevance_threshold", type=float, default=0.05)
    parser.add_argument("--penalty_weight", type=float, default=0.7)
    parser.add_argument("--embedding_batch_size", type=int, default=32)
    parser.add_argument("--max_workers", type=int, default=4)
    parser.add_argument("--model_name", type=str, default="all-MiniLM-L6-v2")
    args = parser.parse_args()

    input_root = Path(args.input_dir)
    output_root = Path(args.output_dir)
    config = {
        "relevance_threshold": args.relevance_threshold,
        "penalty_weight": args.penalty_weight,
        "embedding_batch_size": args.embedding_batch_size
    }

    valid_collections = [d for d in input_root.iterdir() if d.is_dir() and is_valid_collection(d)]
    if not valid_collections:
        logging.warning("No valid collections found.")
        return

    logging.info("Preloading model once to confirm availability...")
    _ = SentenceTransformer(args.model_name)
    logging.info("Model loaded successfully.")

    total_start = time.time()
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {
            executor.submit(process_collection, coll, output_root, args.model_name, config): coll.name
            for coll in valid_collections
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error in '{name}': {e}")

    logging.info(f"\nAll collections processed in {time.time() - total_start:.2f} seconds.")

if __name__ == "__main__":
    main()
