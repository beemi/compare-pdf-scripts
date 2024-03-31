import cv2
import fitz  # PyMuPDF
import numpy as np


# This script works for, script06


def pdf_page_to_image(pdf_path, page_number, resolution=300):
    """Convert a PDF page to an image."""
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    pix = page.get_pixmap(matrix=fitz.Matrix(resolution / 72, resolution / 72))
    img = cv2.imdecode(np.frombuffer(pix.tobytes(), dtype=np.uint8), cv2.IMREAD_COLOR)
    doc.close()
    return img


def find_and_draw_differences(img1, img2):
    """Find differences between two images and draw red rectangles around each distinct change in the second image."""
    # Convert to grayscale and find differences
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray1, gray2)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    # Use dilation to merge nearby contours, making it easier to detect complete changes
    kernel = np.ones((5, 5), np.uint8)  # Kernel size affects merging of close changes
    dilated = cv2.dilate(thresh, kernel, iterations=2)  # Fewer iterations to avoid over-merging

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw a rectangle around each distinct contour
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(img2, (x, y), (x + w, y + h), (0, 0, 255), 2)

    return img2


def combine_images_horizontally(img1, img2):
    """Combine two images horizontally with the same height."""
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    max_height = max(h1, h2)
    total_width = w1 + w2
    combined_img = np.zeros((max_height, total_width, 3), dtype=np.uint8)
    combined_img[:h1, :w1, :] = img1
    combined_img[:h2, w1:w1 + w2, :] = img2
    return combined_img


def compare_pdfs_highlight_and_combine(pdf_path1, pdf_path2, output_pdf_path):
    """Compare PDFs, highlight differences on PDF2, and combine PDF1 and PDF2 pages side by side."""
    doc1 = fitz.open(pdf_path1)
    doc2 = fitz.open(pdf_path2)

    # Validate number of pages in both PDFs before proceeding, else raise an error
    if len(doc1) != len(doc2):
        raise ValueError("Number of pages in the two PDFs do not match.")

    output_pdf = fitz.open()

    for page_num in range(len(doc1)):
        img1 = pdf_page_to_image(pdf_path1, page_num)
        img2 = pdf_page_to_image(pdf_path2, page_num)
        img2_with_differences = find_and_draw_differences(img1, img2)
        combined_img = combine_images_horizontally(img1, img2_with_differences)

        # Convert the combined image to a PDF page
        combined_page = output_pdf.new_page(width=combined_img.shape[1], height=combined_img.shape[0])
        combined_page.insert_image(combined_page.rect, stream=cv2.imencode('.png', combined_img)[1].tobytes())

    output_pdf.save(output_pdf_path)
    output_pdf.close()


# Example usage
# Paths to the PDF files you want to compare
pdf_path1 = "pdffiles/source/pdf_uat_20240330213915.pdf"
pdf_path2 = "pdffiles/target/pdf_prod_20240330213915.pdf"

output_pdf_path = 'output_highlighted_difference_06_06.pdf'

compare_pdfs_highlight_and_combine(pdf_path1, pdf_path2, output_pdf_path)
