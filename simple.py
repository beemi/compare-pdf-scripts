import fitz  # PyMuPDF
import difflib


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    texts = []
    for page in doc:
        texts.append(page.get_text())
    doc.close()
    return texts


def find_differences(text1, text2):
    # This is a basic implementation; consider line-by-line comparison for more detailed diffs
    differ = difflib.Differ()
    diff = list(differ.compare(text1.splitlines(keepends=True), text2.splitlines(keepends=True)))
    return diff


def highlight_differences_in_pdf(pdf_path, differences):
    doc = fitz.open(pdf_path)
    for page_num, diff in enumerate(differences):
        page = doc.load_page(page_num)
        for line in diff:
            if line.startswith("+ "):  # Line only in text2 (consider "- " for text1)
                # Search for the text in the page to find its position
                areas = page.search_for(line[2:])
                for area in areas:
                    annot = page.add_highlight_annot(area)
                    annot.update()
    doc.save("highlighted.pdf")
    doc.close()


# Paths to your PDF files
pdf_path_v1 = "pdffiles/source/amelco-invoice-March-2024.pdf"
pdf_path_v2 = "pdffiles/target/amelco-invoice-March-2024-v2.pdf"

# Extract texts
text_v1 = extract_text_from_pdf(pdf_path_v1)
text_v2 = extract_text_from_pdf(pdf_path_v2)

# Find differences
differences = [find_differences(text_v1[page], text_v2[page]) for page in range(min(len(text_v1), len(text_v2)))]

print(f"Found {sum(len(diff) for diff in differences)} differences")
for page, diff in enumerate(differences):
    print(f"Log each difference for page {page} in the PDF:")
    print("".join(diff))

# Highlight differences in PDF v1
highlight_differences_in_pdf(pdf_path_v1, differences)
