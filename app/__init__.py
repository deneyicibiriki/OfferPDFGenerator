from flask import Flask
from flask_cors import CORS

def create_app():
    """
    Flask uygulamasını oluşturur ve CORS'u aktif eder.
    """
    app = Flask(__name__)
    CORS(app)  # CORS'u aktif eder
    return app
