from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired


class UploadForm(FlaskForm):
    pdf1 = FileField('Upload First PDF', validators=[DataRequired()], description="Upload the first PDF file.")
    pdf2 = FileField('Upload Second PDF', validators=[DataRequired()], description="Upload the second PDF file.")
    submit = SubmitField('Compare PDFs')
