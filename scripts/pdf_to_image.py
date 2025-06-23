from pdf2image import convert_from_path

pdf_path = r"C:\Users\jonhe\OneDrive\Documents\SpotCheck\raw_pdfs\page_108.pdf"
output_folder = r"C:\Users\jonhe\OneDrive\Documents\SpotCheck\images"
poppler_path = r"C:\Users\jonhe\OneDrive\Documents\poppler\poppler-24.08.0\Library\bin"

images = convert_from_path(pdf_path, dpi=400, poppler_path=poppler_path)

for i, image in enumerate(images, start=108):
    image_path = f"{output_folder}\\page_{i}.png"
    image.save(image_path, "PNG")
    print(f"Saved {image_path}")


