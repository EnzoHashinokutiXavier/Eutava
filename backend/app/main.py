from pathlib import Path
from flask import Flask, render_template

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/app -> backend -> raiz do projeto
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
STATIC_DIR = BASE_DIR / "frontend" / "static"

app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()