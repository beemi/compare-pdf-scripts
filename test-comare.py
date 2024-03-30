import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path):
    """
    Extracts all text from a PDF file.
    """
    doc = fitz.open(pdf_path)
    text = ''
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def compare_texts(text1, text2):
    """
    Compares two blocks of text and identifies differences.
    Returns a list of strings describing the differences.
    """
    # Simple line-by-line comparison. More sophisticated diff can be implemented
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()

    diff = []
    for line in set(lines1 + lines2):
        if line in lines1 and line not in lines2:
            diff.append(f"Removed: {line}")
        elif line in lines2 and line not in lines1:
            diff.append(f"Added: {line}")

    return diff


def log_differences(differences, log_file='differences_log.txt'):
    """
    Logs the differences found between two texts to a file.
    """
    with open(log_file, 'w') as file:
        for difference in differences:
            file.write(difference + '\n')


# Paths to the PDF files you want to compare
pdf_path_v1 = "pdffiles/source/amelco-invoice-March-2024.pdf"
pdf_path_v2 = "pdffiles/target/amelco-invoice-March-2024-v2.pdf"

# Extract text from the PDFs
text1 = extract_text_from_pdf(pdf_path_v1)
text2 = extract_text_from_pdf(pdf_path_v2)

# Compare the extracted texts
differences = compare_texts(text1, text2)

# Log the differences
log_differences(differences)

print(f"Differences logged to 'differences_log.txt'.")
