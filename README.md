# SpotCheck Sample – Minneapolis 1900 Directory Parsing

This project is a structured data extraction sample from the 1900 Minneapolis city directory, submitted as part of a parsing trial for HouseNovel.

## 📌 About This Submission

This repository showcases a sample data extraction and normalization pipeline for the 1900 Minneapolis city directory (pages 104–108). Given the complexity of the OCR results, I applied a combination of automation, regex parsing, and manual refinement to structure the resident listings into consistent JSON format.

Full documentation of the workflow decisions and technical trade-offs is available in the linked process doc.

## 📁 Folder Structure

- `images/` – Cropped screenshots of resident columns (used for OCR)
- `ocr_textfiles/` – Text output from Tesseract OCR on cleaned screenshots
- `output/` – Final structured JSON output
- `raw_pdfs/` – Original directory PDFs (pages 104–108)
- `scripts/` – Python scripts used to parse and normalize the data

## 🔧 How to Run the Parser

1. Make sure you have Python 3 installed.
2. Install dependencies:
   ```bash
   pip install pytesseract pdf2image Pillow
