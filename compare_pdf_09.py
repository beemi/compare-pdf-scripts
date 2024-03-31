import datetime
import os
import sys

import cv2
import fitz  # PyMuPDF
import numpy as np


def pdf_page_to_image(pdf_path, page_number, resolution=300):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    pizx = page.get_pixmap(matrix=fitz.Matrix(resolution / 72, resolution / 72))
    img = cv2.imdecode(np.frombuffer(pix.tobytes(), dtype=np.uint8), cv2.IMREAD_COLOR)
    doc.close()
    return img


def find_and_draw_differences(img1, img2):
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray1, gray2)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(img2, (x, y), (x + w, y + h), (0, 0, 255), 2)
    return img2


def combine_images_horizontally(img1, img2):
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    max_height = max(h1, h2)
    total_width = w1 + w2
    combined_img = np.zeros((max_height, total_width, 3), dtype=np.uint8)
    combined_img[:h1, :w1, :] = img1
    combined_img[:h2, w1:w1 + w2, :] = img2
    return combined_img


def compare_pdfs_highlight_and_combine(pdf_path1, pdf_path2, output_pdf_path):
    doc1 = fitz.open(pdf_path1)
    doc2 = fitz.open(pdf_path2)
    if len(doc1) != len(doc2):
        raise ValueError("Number of pages in the two PDFs do not match.")
    output_pdf = fitz.open()
    for page_num in range(len(doc1)):
        img1 = pdf_page_to_image(pdf_path1, page_num)
        img2 = pdf_page_to_image(pdf_path2, page_num)
        img2_with_differences = find_and_draw_differences(img1, img2)
        combined_img = combine_images_horizontally(img1, img2_with_differences)
        combined_page = output_pdf.new_page(width=combined_img.shape[1], height=combined_img.shape[0])
        combined_page.insert_image(combined_page.rect, stream=cv2.imencode('.png', combined_img)[1].tobytes())
    output_pdf.save(output_pdf_path)
    output_pdf.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compare_pdf_09.py <pdf_path1> <pdf_path2> [output_dir]")
        sys.exit(1)
    pdf_path1 = sys.argv[1]  # Path to the first PDF file
    pdf_path2 = sys.argv[2]  # Path to the second PDF file
    # optional output directory
    output_dir = sys.argv[3] if len(sys.argv) == 4 else os.getcwd()
    pdf_time_stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_pdf_path = os.path.join(output_dir, 'result_' + pdf_time_stamp + '.pdf')
    compare_pdfs_highlight_and_combine(pdf_path1, pdf_path2, output_pdf_path)
