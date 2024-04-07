from flask import Flask

from app.routes.main_routes import init_app

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER'] = 'uploader-folder'

# Initialize routes
init_app(app)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
