import cv2
import fitz  # PyMuPDF
import numpy as np


def pdf_page_to_image(pdf_path, page_number, resolution=300):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    pix = page.get_pixmap(matrix=fitz.Matrix(resolution / 72, resolution / 72))
    img = cv2.imdecode(np.frombuffer(pix.tobytes(), dtype=np.uint8), cv2.IMREAD_COLOR)
    doc.close()
    return img


def find_and_draw_differences(img1, img2):
    # Convert images to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Compute the absolute difference between the two images
    diff = cv2.absdiff(gray1, gray2)

    # Threshold the difference to get a binary image of differences
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    # Find contours of the differences
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw red rectangles around differences in the second image
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(img2, (x, y), (x + w, y + h), (0, 0, 255), 2)

    return img2


def compare_pdfs_and_highlight(pdf_path1, pdf_path2, output_pdf_path):
    doc1 = fitz.open(pdf_path1)
    doc2 = fitz.open(pdf_path2)

    for page_num in range(len(doc1)):
        img1 = pdf_page_to_image(pdf_path1, page_num)
        img2 = pdf_page_to_image(pdf_path2, page_num)

        # Find and draw differences
        img2_with_differences = find_and_draw_differences(img1, img2)

        # Convert the image with differences back to a PDF page
        doc2[page_num].insert_image(doc2[page_num].rect,
                                    stream=cv2.imencode('.png', img2_with_differences)[1].tobytes())

    doc2.save(output_pdf_path)
    doc2.close()


# Usage
# Paths to the PDF files you want to compare
pdf_path1 = "pdffiles/source/sample_pdf_1.pdf"
pdf_path2 = "pdffiles/target/sample_pdf_2.pdf"
output_pdf_path = 'output_highlighted_differences.pdf'

compare_pdfs_and_highlight(pdf_path1, pdf_path2, output_pdf_path)
