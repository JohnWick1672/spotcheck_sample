from PIL import Image
import pytesseract
from pathlib import Path
from collections import defaultdict

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Folder containing images
images_folder = Path(r"C:\Users\jonhe\OneDrive\Documents\SpotCheck\images")

# Output folder for text files
output_folder = Path(r"C:\Users\jonhe\OneDrive\Documents\SpotCheck\ocr_textfiles")
output_folder.mkdir(exist_ok=True)

# Grouping image files by page number
image_files = sorted(images_folder.glob("*.png"))
grouped_images = defaultdict(list)

for image_path in image_files:
    page_num = image_path.stem.split("_")[0]
    grouped_images[page_num].append(image_path)

# OCR each image and write text by page
for page, files in grouped_images.items():
    page_text = ""
    for file in sorted(files):
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
        page_text += text.strip() + "\n\n"

    output_file = output_folder / f"{page}.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(page_text.strip())

print("OCR complete. Text files saved in:", output_folder)
