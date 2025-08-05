from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Vercel akan menangani mode debug, jadi kita tidak perlu mengaturnya secara eksplisit di sini

from app.routes import main
app.register_blueprint(main.bp)
