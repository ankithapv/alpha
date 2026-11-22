from flask import Flask
from dotenv import load_dotenv
from pathlib import Path

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = __import__("os").getenv("SECRET_KEY", "dev-only-change-me")
    from .routes import bp
    app.register_blueprint(bp)
    return app
