from pathlib import Path
from flask import Flask, render_template, redirect, url_for, request, session, flash
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/app -> backend -> raiz do projeto
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
STATIC_DIR = BASE_DIR / "frontend" / "static"

app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))
app.secret_key = "hello" # para encriptar !!! temporario, mudar depois
app.permanent_session_lifetime = timedelta(days=2) # quanto tempo armazena sessão para nao precisar logar toda vez que fechar o browser

# Pagina inicial, se não estiver logado redireciona para pagina de login
@app.route("/")
def home():
    if "user" in session:
        user = session["user"]
        return render_template("index.html", user=user)
    else:
        flash("Não está logado!", "info")
        return redirect(url_for("login"))

# Get recebe formulario e quando preenchido envia em POST 
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["name"]
        session["user"] = user
        return redirect(url_for("home"))
    else:
        if "user" in session:
            flash("Já está logado!", "info")
            return redirect(url_for("home"))
        return render_template("login.html")

# Limpa sessão
@app.route("/logout")
def logout():
    if "user" in session:
        session.pop("user", None)
        flash("Desconectado com sucesso!", "info")
    return redirect(url_for("login"))

# Só roda o servidor web quando executar diretamente de main.py
if __name__ == "__main__":
    app.run(debug=True) 