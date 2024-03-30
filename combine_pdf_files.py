import fitz  # PyMuPDF


def combine_pdfs_side_by_side(pdf_path1, pdf_path2, output_pdf_path):
    """
    Combines two PDFs by placing pages side by side into a new PDF.

    Parameters:
        pdf_path1 (str): Path to the first PDF file.
        pdf_path2 (str): Path to the second PDF file.
        output_pdf_path (str): Path where the output PDF should be saved.
    """
    # Open the PDFs
    doc1 = fitz.open(pdf_path1)
    doc2 = fitz.open(pdf_path2)

    # Create a new PDF for the output
    output_pdf = fitz.open()

    # Iterate through the pages of both PDFs
    for page_num in range(max(len(doc1), len(doc2))):
        # Create a blank new page with double the width of the largest page in either PDF
        if page_num < len(doc1) and page_num < len(doc2):
            new_width = doc1[page_num].rect.width + doc2[page_num].rect.width
            new_height = max(doc1[page_num].rect.height, doc2[page_num].rect.height)
        elif page_num < len(doc1):  # If doc2 has fewer pages
            new_width = doc1[page_num].rect.width * 2
            new_height = doc1[page_num].rect.height
        else:  # If doc1 has fewer pages
            new_width = doc2[page_num].rect.width * 2
            new_height = doc2[page_num].rect.height

        new_page = output_pdf.new_page(width=new_width, height=new_height)

        # If the current page exists in doc1, insert it to the left half of the new page
        if page_num < len(doc1):
            page1 = doc1.load_page(page_num)
            rect1 = fitz.Rect(0, 0, doc1[page_num].rect.width, doc1[page_num].rect.height)
            new_page.show_pdf_page(rect1, doc1, page_num)

        # If the current page exists in doc2, insert it to the right half of the new page
        if page_num < len(doc2):
            page2 = doc2.load_page(page_num)
            if page_num < len(doc1):
                x_offset = doc1[page_num].rect.width
            else:
                x_offset = 0
            rect2 = fitz.Rect(x_offset, 0, x_offset + doc2[page_num].rect.width, doc2[page_num].rect.height)
            new_page.show_pdf_page(rect2, doc2, page_num)

    # Save the output PDF
    output_pdf.save(output_pdf_path)

    # Close the documents
    doc1.close()
    doc2.close()
    output_pdf.close()



# Example usage
pdf_path1 = "pdffiles/source/sample_pdf_1.pdf"
pdf_path2 = "pdffiles/target/sample_pdf_2.pdf"

combine_pdfs_side_by_side(pdf_path1, pdf_path2, 'output_combined.pdf')
