import datetime
import logging
import os
import shutil

from flask import render_template, redirect, url_for, send_file, make_response, jsonify
from werkzeug.utils import secure_filename

from app.forms import UploadForm
from app.pdf_utils import compare_pdfs_highlight_and_combine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

start_time = datetime.datetime.now()

def init_app(app):
    @app.route('/', methods=['GET', 'POST'])
    def upload():
        form = UploadForm()
        if form.validate_on_submit():
            pdf1_filename = secure_filename(form.pdf1.data.filename)
            pdf2_filename = secure_filename(form.pdf2.data.filename)
            logging.info(f"PDF1 filename: {pdf1_filename}")
            logging.info(f"PDF2 filename: {pdf2_filename}")

            pdf1_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf1_filename)
            pdf2_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf2_filename)
            logging.info(f"PDF1 path: {pdf1_path}")
            logging.info(f"PDF2 path: {pdf2_path}")

            form.pdf1.data.save(pdf1_path)
            form.pdf2.data.save(pdf2_path)
            logging.info('PDFs uploaded successfully.')

            pdf_time_stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            report_full_name = 'output_' + pdf_time_stamp + '.pdf'
            output_pdf_path = os.path.join('app/static', report_full_name)
            logging.info(f"Output PDF path: {output_pdf_path}")

            try:
                compare_pdfs_highlight_and_combine(pdf1_path, pdf2_path, output_pdf_path)
            except Exception as e:
                return f'Error comparing PDFs: {str(e)}'

            # Render the output.html template and pass the path to the PDF file
            return render_template('output.html', pdf_path=report_full_name, pdf1=pdf1_filename, pdf2=pdf2_filename,
                                   form=form)

        return render_template('upload.html', form=form)

    @app.route('/clear', methods=['POST'])
    def clear():
        logging.info("Clearing the upload folder requested.")
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

    @app.route('/download/<path:pdf_path>')
    def download(pdf_path):
        return send_file(f'app/static/{pdf_path}', as_attachment=True)

    @app.route('/clear/output', methods=['POST'])
    def delete_all_output():
        logging.info("Deleting all output files requested from app/static.")
        folder = 'app/static'
        # Delete all files in the 'app/static' folder starting with 'output_'
        for filename in os.listdir(folder):
            if filename.startswith('output_'):
                file_path = os.path.join(folder, filename)
                try:
                    os.unlink(file_path)
                except Exception as e:
                    logging.error(f'Failed to delete {file_path}. Reason: {e}')
        return redirect(url_for("upload"))

    # add health check endpoint with timestamp & version
    @app.route('/health', methods=['GET'])
    def health():
        try:
            uptime = datetime.datetime.now() - start_time
            return make_response(
                jsonify({
                    'status': 'healthy',
                    'timestamp': datetime.datetime.now().isoformat(),
                    'version': '1.0.0',
                    'uptime': str(uptime)
                }),
                200
            )
        except Exception as e:
            return make_response(jsonify({'status': 'error', 'message': str(e)}), 500)