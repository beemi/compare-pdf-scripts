import datetime
import os

import shutil

import cv2
import fitz  # PyMuPDF
import numpy as np
from flask import Flask, render_template, redirect, url_for
from flask import send_file
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired

from compare_pdf_09 import compare_pdfs_highlight_and_combine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER'] = 'uploader-folder'


class UploadForm(FlaskForm):
    pdf1 = FileField('Upload First PDF', validators=[DataRequired()], description="Upload the first PDF file.")
    pdf2 = FileField('Upload Second PDF', validators=[DataRequired()], description="Upload the second PDF file.")
    submit = SubmitField('Compare')


def pdf_page_to_image(pdf_path, page_number, resolution=300):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    pix = page.get_pixmap(matrix=fitz.Matrix(resolution / 72, resolution / 72))
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


@app.route('/', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        pdf1_filename = secure_filename(form.pdf1.data.filename)
        pdf2_filename = secure_filename(form.pdf2.data.filename)
        pdf1_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf1_filename)
        pdf2_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf2_filename)
        print("PDF1 path:", pdf1_path)
        print("PDF2 path:", pdf2_path)

        form.pdf1.data.save(pdf1_path)
        form.pdf2.data.save(pdf2_path)
        print("PDFs saved successfully.")

        pdf_time_stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_' + pdf_time_stamp + '.pdf')

        try:
            compare_pdfs_highlight_and_combine(pdf1_path, pdf2_path, output_pdf_path)
        except Exception as e:
            return f'Error comparing PDFs: {str(e)}'

        # Calculate the relative path to the PDF file from the static folder
        static_pdf_path = os.path.join('static', 'output_' + pdf_time_stamp + '.pdf')
        shutil.move(output_pdf_path, static_pdf_path)

        # Calculate the relative path to the PDF file from the static folder
        pdf_relative_path = os.path.relpath(static_pdf_path, 'static')

        # Print the absolute and relative paths to the PDF file
        print(f'Absolute path: {output_pdf_path}')
        print(f'Relative path: {pdf_relative_path}')

        # Check if the file exists at the absolute path
        if os.path.exists(output_pdf_path):
            print('File exists at the absolute path.')
        else:
            print('File does not exist at the absolute path.')

        # Render the output.html template and pass the path to the PDF file
        return render_template('output.html', pdf_path=pdf_relative_path)

    return render_template('upload.html', form=form)


@app.route('/clear', methods=['POST'])
def clear():
    folder = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    return redirect(url_for("upload"))


@app.route('/download/<path:filename>')
def download(filename):
    return send_file(f'static/{filename}', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
