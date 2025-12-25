# unredact_epstein_batch.py
# Purpose: Batch extract hidden/underlying text from PDFs (bypasses overlay redactions)
# Requirements: pymupdf, pdfplumber (already installed in this venv)
# Usage: python unredact_epstein_batch.py /path/to/epstein_pdfs_folder

import os
import sys
import fitz       # PyMuPDF
import pdfplumber # Fallback extractor

def extract_text_from_pdf(pdf_path):
    """Pull raw text layers, ignoring black box annotations/overlays."""
    text = ""
    try:
        # PyMuPDF first - best at recovering "hidden" text under redactions
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + "\n\n"
        doc.close()

        # If nothing found, try pdfplumber as backup
        if not text.strip():
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n\n"

        return text.strip() if text.strip() else "No extractable text (likely image-only PDF)."
    except Exception as e:
        return f"Error: {str(e)}"

def batch_process(input_dir, output_dir=None):
    """Process all .pdf files recursively, save extracted text."""
    if output_dir is None:
        output_dir = os.path.join(input_dir, "unredacted_txt")
    os.makedirs(output_dir, exist_ok=True)

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                print(f"Processing: {pdf_path}")
                extracted = extract_text_from_pdf(pdf_path)

                base_name = os.path.splitext(file)[0]
                txt_path = os.path.join(output_dir, f"{base_name}.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(f"Source: {pdf_path}\n\n{extracted}")
                print(f"Saved: {txt_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python unredact_epstein_batch.py /path/to/your/epstein_folder")
        sys.exit(1)
    input_dir = sys.argv[1]
    batch_process(input_dir)
