from flask import Flask

from app.routes.main_routes import init_app

app = Flask(__name__, template_folder='app/templates')
init_app(app)
