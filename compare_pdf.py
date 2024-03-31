import fitz  # PyMuPDF


def extract_font_details_with_position(pdf_path):
    """
    Extract font name, size, and position from each text span in the PDF.
    """
    doc = fitz.open(pdf_path)
    font_details = []
    for page in doc:
        page_fonts = []
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if 'lines' in block:  # Ensure it's a text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        page_fonts.append({
                            "text": span["text"],
                            "font": span["font"],
                            "size": span["size"],
                            "bbox": span["bbox"]  # Bounding box of the text
                        })
        font_details.append(page_fonts)
    doc.close()
    return font_details


def highlight_font_changes(pdf_path, fonts1, fonts2):
    """
    Draws a red rectangle around text in the second PDF where font changes are detected.
    """
    doc = fitz.open(pdf_path)
    for page_num, (page_fonts1, page_fonts2) in enumerate(zip(fonts1, fonts2)):
        page = doc.load_page(page_num)
        for font1, font2 in zip(page_fonts1, page_fonts2):
            if font1["font"] != font2["font"] or font1["size"] != font2["size"]:
                rect = fitz.Rect(font2["bbox"])  # Use bbox for rectangle
                page.draw_rect(rect, color=(1, 0, 0), width=1.5)  # Draw red rectangle
    doc.save("highlighted_changes.pdf")
    doc.close()


def combine_pdfs_side_by_side(pdf_path1, pdf_path2, output_path):
    """
    Combines two PDFs side by side into a single PDF.
    """
    pdf1 = fitz.open(pdf_path1)
    pdf2 = fitz.open(pdf_path2)
    output_pdf = fitz.open()

    for page_num in range(min(pdf1.page_count, pdf2.page_count)):
        page1 = pdf1.load_page(page_num)
        page2 = pdf2.load_page(page_num)

        width = max(page1.rect.width, page2.rect.width)
        height = max(page1.rect.height, page2.rect.height)

        new_page = output_pdf.new_page(width * 2, height)
        new_page.show_pdf_page((0, 0, width, height), pdf1, page_num)
        new_page.show_pdf_page((width, 0, width * 2, height), pdf2, page_num)

    output_pdf.save(output_path)
    pdf1.close()
    pdf2.close()
    output_pdf.close()


# Paths to the PDF files you want to compare
pdf_path1 = "pdffiles/source/sample_pdf_1.pdf"
pdf_path2 = "pdffiles/target/sample_pdf_2.pdf"

# Extract font details and positions from the PDFs
fonts1 = extract_font_details_with_position(pdf_path1)
fonts2 = extract_font_details_with_position(pdf_path2)

# Highlight font changes in the second PDF
highlight_font_changes(pdf_path2, fonts1, fonts2)

# Combine the two PDFs side by side for visual comparison

output_path = "combined_pdfs.pdf"
combine_pdfs_side_by_side(pdf_path1, pdf_path2, output_path)
