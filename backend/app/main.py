from pathlib import Path
from flask import Flask, render_template, redirect, url_for, request, session, flash
from datetime import timedelta
from app.db import get_connection, init_db
from app.models import create_user, get_user
from app.security import hash_password, verify_password
from psycopg.errors import OperationalError
from dotenv import load_dotenv
import os
from email_validator import validate_email, EmailNotValidError

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/app -> backend -> raiz do projeto
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
STATIC_DIR = BASE_DIR / "frontend" / "static"

app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))
app.secret_key = SECRET_KEY
app.permanent_session_lifetime = timedelta(days=2) # quanto tempo armazena sessão para nao precisar logar toda vez que fechar o browser

@app.cli.command("init-db")
def init_db_command():
    init_db()
    print("Banco initialized with success")

#
# !!! ALTERAR : 
# @login_required para não repetir if "user_id" in session em cada rota
# formulários POST nao tem proteção, usar Flask-WTF com CSRFProtect
# erros OperationalError não são tratados, fazer @app.errorhandler global 
# rotas para user_exists, email_exists, get_user_hash
#


# Pagina inicial, se não estiver logado redireciona para pagina de login
@app.route("/")
def home():
    if "user" in session:
        user = session["user"]
        return render_template("index.html", user=user)
    else:
        flash("You're not logged in!", "info")
        return redirect(url_for("login"))

# Get recebe formulario e quando preenchido envia em POST 
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        if "user_id" in session:
            flash("You're already logged in!", "info")
            return redirect(url_for("home"))
        return render_template("login.html")
        
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if (len(email) == 0) or (len(password) == 0):
        flash("Please fill in all fields", "error")
        return render_template("login.html"), 400
    
    try:    
        user = get_user(email)
    except OperationalError:
        flash("Internal Server Error", "error")
        return render_template("login.html"), 503
    
    if user is None or not verify_password(user[2], password):
        flash("Invalid email or password", "error")
        return render_template("login.html"), 401

    user_id, name, _ = user

    session.clear()
    session.permanent = True
    session["user_id"] = user_id
    session["user"] = name

    return redirect(url_for("home"))

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    # Validar email
    try:
        # validate_email retorna um objeto com o email validado, caso seja valido, caso contrario lança EmailNotValidError
        info = validate_email(email, check_deliverability=True) # True para verificar se o email é entregável, False para apenas validar o formato
        email = info.email # o gmail não é verificado se é ativo, apenas se o formato é valido com dominio existente 
    except EmailNotValidError:
        flash("Please enter a valid email address", "error")
        return render_template("register.html"), 400

    if (len(name) == 0) or (len(email) == 0) or (len(password) == 0):
        flash("Please fill in all fields", "error")
        return render_template("register.html"), 400

    if (len(password) < 8):
        flash("Password must be at least 8 characters long", "error")
        return render_template("register.html"), 400

    hashed = hash_password(password)
    try:
        user_id = create_user(name, email, hashed)
    except OperationalError:
        flash("Internal server error", "error")
        return render_template("register.html"), 503

    if user_id is None:
        flash("This email is already registered", "error")
        return render_template("register.html"), 409

    flash("Account created", "success")
    return redirect(url_for("login"))

# Limpa sessão
@app.route("/logout")
def logout():
    if "user" in session:
        session.clear()
        flash("Logged out successfully!", "info")
    return redirect(url_for("login"))

# Só roda o servidor web quando executar diretamente de main.py
if __name__ == "__main__":
    app.run(debug=True) 