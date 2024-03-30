import fitz  # PyMuPDF


def extract_text_and_styles(pdf_path):
    doc = fitz.open(pdf_path)
    pages_text_styles = []
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        page_text_styles = []
        for block in blocks:
            if 'lines' in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        # Extract text and font information
                        text = span["text"]
                        font = span["font"]
                        # Approximation: Consider the text bold if "Bold" is in the font name
                        is_bold = "Bold" in font
                        bbox = span["bbox"]
                        page_text_styles.append((text, is_bold, bbox))
        pages_text_styles.append(page_text_styles)
    doc.close()
    return pages_text_styles


def highlight_bold_changes(pdf_path1, pdf_path2, output_pdf_path):
    text_styles1 = extract_text_and_styles(pdf_path1)
    text_styles2 = extract_text_and_styles(pdf_path2)

    doc2 = fitz.open(pdf_path2)
    for page_num, (styles1, styles2) in enumerate(zip(text_styles1, text_styles2)):
        page = doc2.load_page(page_num)
        for (text1, is_bold1, bbox1), (text2, is_bold2, bbox2) in zip(styles1, styles2):
            if text1 == text2 and is_bold1 != is_bold2 and is_bold2:
                # Highlight in PDF2 if text matches but boldness differs and PDF2's text is bold
                rect = fitz.Rect(bbox2)
                page.draw_rect(rect, color=(1, 0, 0), width=1.5)
    doc2.save(output_pdf_path)
    doc2.close()


def highlight_changes_debug(pdf_path1, pdf_path2, output_pdf_path):
    text_styles1 = extract_text_and_styles(pdf_path1)
    text_styles2 = extract_text_and_styles(pdf_path2)

    doc2 = fitz.open(pdf_path2)
    changes_found = False  # Debugging flag

    for page_num, (styles1, styles2) in enumerate(zip(text_styles1, text_styles2)):
        page = doc2.load_page(page_num)
        for (_, is_bold1, bbox1), (_, is_bold2, bbox2) in zip(styles1, styles2):
            # Simplified condition for demonstration: draw if any change detected
            if is_bold1 != is_bold2:  # Change this condition as per your criteria
                changes_found = True
                print(f"Change detected on page {page_num + 1}")  # Debugging print
                rect = fitz.Rect(bbox2)  # Use bbox from PDF2 for drawing
                page.draw_rect(rect, color=(1, 0, 0), width=1.5)  # Draw red rectangle

    if changes_found:
        doc2.save(output_pdf_path)
        print(f"Changes highlighted in {output_pdf_path}")
    else:
        print("No changes detected.")

    doc2.close()


# Example usage
pdf_path1 = "pdffiles/source/pdf_uat_20240330213915.pdf"
pdf_path2 = "pdffiles/target/pdf_prod_20240330213915.pdf"

highlight_changes_debug(pdf_path_v1, pdf_path_v2, "highlighted_bold_changes.pdf")
