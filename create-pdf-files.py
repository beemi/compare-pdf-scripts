import datetime

from fpdf import FPDF

# Create two PDF files that are mostly similar but with slight differences in fonts, some bold text, and distinct
# watermarks.

# Create instance of FPDF class for PDF 1 (UAT)
pdf_uat = FPDF()
pdf_uat.add_page()
pdf_uat.set_font("Times", size=12)  # Change font to Times
pdf_uat.cell(0, 10, "This PDF file is designated for UAT.", ln=True)
pdf_uat.set_font("Arial", size=12, style='B')
pdf_uat.cell(0, 10, "The content here is mostly similar to its counterpart, with some differences.", ln=True)
pdf_uat.set_font("Arial", size=12)
pdf_uat.cell(0, 10, "Firstname: John Doe", ln=True)
# Add a watermark for UAT
pdf_uat.set_font("Arial", style='I', size=50)
pdf_uat.set_text_color(220, 220, 220)
pdf_uat.rotate(45, x=55, y=55)
pdf_uat.text(30, 190, "UAT")

pdf_time_stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Save PDF 1
pdf_uat_path = "pdffiles/source/pdf_uat_" + pdf_time_stamp + ".pdf"
pdf_uat.output(pdf_uat_path)

# Create instance of FPDF class for PDF 2 (Prod)
pdf_prod = FPDF()
pdf_prod.add_page()
pdf_prod.set_font("Times", size=12)  # Change font to Times
pdf_prod.cell(0, 10, "This PDF file is designated for Production.", ln=True)
pdf_prod.set_font("Times", size=12, style='B')
pdf_prod.cell(0, 10, "Most content is identical to its UAT version, with minor variances.", ln=True)
pdf_prod.set_font("Times", size=12, style='BI')  # Slight change in style for user input text
pdf_prod.cell(0, 10, "Firstname: Jane Smith", ln=True)  # Change in user input text
# Add a watermark for Prod
pdf_prod.set_font("Times", style='B', size=50)
pdf_prod.set_text_color(200, 200, 200)
pdf_prod.rotate(45, x=55, y=55)
pdf_prod.text(30, 190, "PROD")

# Save PDF 2
pdf_prod_path = "pdffiles/target/pdf_prod_" + pdf_time_stamp + ".pdf"
pdf_prod.output(pdf_prod_path)

var = pdf_uat_path, pdf_prod_path
print(var)
