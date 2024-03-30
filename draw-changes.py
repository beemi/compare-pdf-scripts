import fitz  # PyMuPDF
import numpy as np
from skimage.measure import label, regionprops
from skimage.color import rgb2gray
from skimage.morphology import dilation, square


def render_pdf_page_to_image(pdf_path, page_number, zoom=2):
    """
    Renders a PDF page to an image using a specified zoom factor for higher resolution.
    """
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    doc.close()
    return img


def compare_images(img1, img2):
    """
    Compares two images and returns a mask of differences. Enhanced to handle grayscale conversion.
    """
    gray1 = rgb2gray(img1)
    gray2 = rgb2gray(img2)
    diff = np.abs(gray1 - gray2) > 0.05  # Adjust threshold as needed
    # Optionally dilate the diff to make regions more contiguous
    diff = dilation(diff, square(3))
    return diff


def highlight_differences_in_pdf(pdf_path, diff_masks, output_pdf_path):
    """
    Draws rectangles around differences on the PDF pages and saves the output. Uses region detection.
    """
    doc = fitz.open(pdf_path)
    for page_number, diff_mask in enumerate(diff_masks):
        if np.any(diff_mask):  # If there are any differences
            labeled_mask = label(diff_mask)
            regions = regionprops(labeled_mask)
            page = doc.load_page(page_number)
            pix = page.get_pixmap()
            scale_x = pix.width / diff_mask.shape[1]
            scale_y = pix.height / diff_mask.shape[0]
            for region in regions:
                # Scale the bounding box back to PDF coordinate system
                y0, x0, y1, x1 = region.bbox
                rect = fitz.Rect(x0 * scale_x, y0 * scale_y, x1 * scale_x, y1 * scale_y)
                page.draw_rect(rect, color=(1, 0, 0), width=1.5)
    doc.save(output_pdf_path)
    doc.close()


def find_rectangles_in_mask(mask, scale_factor=1):
    """
    Detects rectangles in a binary mask of differences. This is a placeholder for
    a function that would identify contiguous differing regions.
    Returns a list of fitz.Rect objects scaled by scale_factor.
    """
    # Placeholder: return a single rectangle covering the whole page if any difference is found
    if np.any(mask):
        return [fitz.Rect(0, 0, mask.shape[1] * scale_factor, mask.shape[0] * scale_factor)]
    return []


# Example usage
# Paths to the PDF files you want to compare
pdf_path_v1 = "pdffiles/source/amelco-invoice-March-2024.pdf"
pdf_path_v2 = "pdffiles/target/amelco-invoice-March-2024-v2.pdf"
output_pdf = 'output_highlighted_differences.pdf'
page_num = 0  # Example for the first page

# Render pages to images
img1 = render_pdf_page_to_image(pdf_path_v1, page_num)
img2 = render_pdf_page_to_image(pdf_path_v2, page_num)

# Compare images and get difference mask
diff_mask = compare_images(img1, img2)

# Highlight differences in the output PDF
highlight_differences_in_pdf(pdf_path_v1, [diff_mask], output_pdf)
