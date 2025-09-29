# -*- coding: utf-8 -*-
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os


# Извлечение нативного текста
def extract_native_text(pdf_path):
    doc = fitz.open(pdf_path)
    pages_text = []
    for page in doc:
        text = page.get_text("text")
        pages_text.append(text)
    return pages_text


# OCR через Tesseract для сканированных страниц
def ocr_pdf(pdf_path, dpi=300, lang='rus'):
    pages_images = convert_from_path(pdf_path, dpi=dpi)
    pages_text = []
    for i, img in enumerate(pages_images):
        text = pytesseract.image_to_string(img, lang=lang)
        pages_text.append(text)
    return pages_text


# Объединяем нативный текст и OCR (приоритет нативного текста)
def parse_pdf(pdf_path):
    native_texts = extract_native_text(pdf_path)
    ocr_texts = ocr_pdf(pdf_path)
    full_text = []
    for n, o in zip(native_texts, ocr_texts):
        if n.strip():  # если есть нативный текст
            full_text.append(n)
        else:
            full_text.append(o)
    return full_text


def work():
    # Указываем папку pdfres и файл в ней
    pdf_folder = "pdfres"
    pdf_filename = "document.pdf"  # замените на имя вашего файла

    pdf_path = os.path.join(pdf_folder, pdf_filename)

    if not os.path.exists(pdf_path):
        print(f"Файл {pdf_path} не найден!")
        print("Убедитесь, что:")
        print(f"1. Папка '{pdf_folder}' существует")
        print(f"2. Файл '{pdf_filename}' находится в папке '{pdf_folder}'")
        exit(1)

    result_pages = parse_pdf(pdf_path)
    print(f"Количество страниц: {len(result_pages)}")

    full_text = "\n\n".join(result_pages)
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(full_text)
    print("Распознанный текст сохранён в output.txt")