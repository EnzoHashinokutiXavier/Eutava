from pathlib import Path
from flask import Flask, render_template, redirect, url_for, request, session, flash
from datetime import date, timedelta
from app.db import init_db
from app.decorators import login_required
from app.routes import bp as courses_bp, WARN_AT
from app.holidays import bp as holidays_bp
from app.models import create_user, get_user, get_user_hash, update_user_hash, delete_user, get_courses, get_holidays, build_course
from app.attendance import day_info, course_stats
from app.security import hash_password, verify_password
from psycopg.errors import OperationalError
from dotenv import load_dotenv
import os
from email_validator import validate_email, EmailNotValidError
from flask_wtf.csrf import CSRFProtect, CSRFError

# carrega variáveis de ambiente do .env para o ambiente do sistema operacional
load_dotenv()

# os lê variáveis de ambiente do arquivo .env
SECRET_KEY = os.environ["SECRET_KEY"]
# encontrar o caminho do diretório raiz do projeto, que é o pai do diretório backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/app -> backend -> raiz do projeto
# define os diretórios de templates e arquivos estáticos do frontend
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
# define o diretório de arquivos estáticos do frontend
STATIC_DIR = BASE_DIR / "frontend" / "static"

app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))
app.secret_key = SECRET_KEY
app.permanent_session_lifetime = timedelta(days=2) # quanto tempo armazena sessão para nao precisar logar toda vez que fechar o browser
app.register_blueprint(courses_bp) # rotas de matérias (/courses) definidas em routes.py
app.register_blueprint(holidays_bp) # rotas de feriados (/holidays) definidas em holidays.py

# CSRF é um ataque de outro site, CSRF token resolve gerando um token escondido no html
csrf = CSRFProtect(app) # exige csrf_token válido em todo POST/PUT/PATCH/DELETE

# uso de ia : a ia identificou brecha na segurança do site, que poderia permitir que um site malicioso fizesse requisições em nome do usuário logado, como deletar matérias ou marcar faltas. Para resolver isso, foi implementado o CSRF token, que é um token único gerado para cada sessão do usuário e incluído em todos os formulários. O servidor verifica esse token em cada requisição para garantir que a requisição veio do próprio site e não de um site externo.

@app.cli.command("init-db")
def init_db_command():
    init_db()
    print("Banco initialized with success")

#
# !!! ALTERAR :
# rotas para get_user_hash
#

# uso de ia : ao buscar falhas a ia recomendou o uso de handlers globais para tratar erros de conexão com o banco de dados e erros de CSRF, garantindo que o usuário receba uma mensagem amigável e que o sistema não exponha detalhes técnicos. Além disso, a ia sugeriu a implementação de validação de email no registro de usuários para evitar emails inválidos e melhorar a segurança do sistema.

# Handler global para falhas de conexão com o banco: re-renderiza a página da rota que falhou com status 503
@app.errorhandler(OperationalError)
def handle_db_error(error): 
    app.logger.exception("Database error on %s", request.path)
    flash("Internal server error", "error")
    templates = {"login": "login.html", "register": "register.html", "change_password": "change_password.html", "delete_account": "delete_account.html"}
    # rotas com formulário voltam para a própria página
    template = templates.get(request.endpoint)
    if template is None: # rotas que não tem template definido retornam apenas status 503
        return "Service unavailable", 503
    return render_template(template), 503

# Handler para token CSRF ausente/inválido/expirado: volta para o formulário com mensagem de erro, ou retorna 400 se não for rota de formulário
@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    app.logger.warning("CSRF error on %s: %s", request.path, error.description) # loga o erro de CSRF para debug, mas não mostra detalhes para o usuário
    flash("Your session expired, please try again", "error")
    templates = {"login": "login.html", "register": "register.html", "change_password": "change_password.html", "delete_account": "delete_account.html"}
    template = templates.get(request.endpoint)
    if template is None:
        return "Bad request", 400
    return render_template(template), 400

# Pagina inicial
@app.route("/")
@login_required
def home():
    today = date.today()
    user_holidays = get_holidays(session["user_id"])  # busca uma vez so, valem para todas as materias

    today_courses = []  # matérias que têm alguma coisa hoje: aula pendente, aula já marcada ou feriado
    all_courses = []    # todas as matérias, com as faltas usadas (card "All courses")
    for row in get_courses(session["user_id"]):
        course = build_course(row, user_holidays)

        stats = course_stats(course, today, WARN_AT)  # {"used", "max", "status"}
        all_courses.append({"id": row[0], "name": course.name, "left": stats["max"] - stats["used"], **stats})

        info = day_info(course, today, today)  # {"type", "schedules", "absences", ...}
        if info["type"] not in ("none", "out"):  # "none" = sem aula hoje, "out" = fora do período da matéria
            today_courses.append({"id": row[0], "name": course.name, **info})

    # as que têm menos faltas sobrando aparecem primeiro
    all_courses.sort(key=lambda c: c["left"])

    return render_template("index.html", user=session["user"], today=today, courses=today_courses, all_courses=all_courses)

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
    
    user = get_user(email)

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

    # uso de ia : identificar que verificação dos campos vazios depois de validar email resultaria em mensagem de erro incorreta
    if (len(name) == 0) or (len(email) == 0) or (len(password) == 0):
        flash("Please fill in all fields", "error")
        return render_template("register.html"), 400

    # Validar email
    try:
        # validate_email retorna um objeto com o email validado, caso seja valido, caso contrario lança EmailNotValidError
        info = validate_email(email, check_deliverability=False) 
        # !!!! True faz uma consulta DNS a cada cadastro. Sem internet, ou se o DNS falhar, o cadastro de um email válido é recusado. Em desenvolvimento ou nos testes, vale usar False !!!!!!!!

        email = info.email # o gmail não é verificado se é ativo, apenas se o formato é valido com dominio existente 
    except EmailNotValidError:
        flash("Please enter a valid email address", "error")
        return render_template("register.html"), 400

    if (len(password) < 8):
        flash("Password must be at least 8 characters long", "error")
        return render_template("register.html"), 400

    hashed = hash_password(password)
    user_id = create_user(name, email, hashed)

    if user_id is None:
        flash("This email is already registered", "error")
        return render_template("register.html"), 409

    flash("Account created", "success")
    return redirect(url_for("login"))

# Troca de senha : GET mostra o formulario, POST valida e atualiza
@app.route("/account/password", methods=["POST", "GET"])
@login_required
def change_password(): 
    # GET
    if request.method == "GET":
        return render_template("change_password.html")

    # POST
    current = request.form.get("current_password", "") # usuario digita senha atual
    new = request.form.get("new_password", "") # usuario digita nova senha
    confirm = request.form.get("confirm_password", "") # digita novamente nova senha 

    # verificação campo vazio
    if len(current) == 0:
        flash("Please enter the current password", "error")
        return render_template("change_password.html"), 400
    if len(new) == 0:
        flash("Please enter the new password", "error")
        return render_template("change_password.html"), 400
    if len(confirm) == 0:
        flash("Please confirm new password", "error")
        return render_template("change_password.html"), 400

    # pega usuário da sessão e hash da senha dele
    user_id = session["user_id"]
    hashed = get_user_hash(user_id)

    # sessão aponta para um usuário que não existe mais (conta excluída / banco recriado)
    # isso só acontece quando a sessão ainda existe mas a conta não existe mais. Por exemplo, a conta foi excluída enquanto o usuário continuava logado (o cookie dura 2 dias), ou o banco foi recriado com init-db
    # uso de ia : identificar possível problema com usuário que nao existe mais 
    if hashed is None:
        session.clear()
        flash("Your session is no longer valid, please log in again", "error")
        return redirect(url_for("login"))

    # se a senha atual estiver errada
    if not verify_password(hashed, current):
        flash("Current password is incorrect", "error")
        return render_template("change_password.html"), 401

    # se senha menor que oito caracteres
    if len(new) < 8:
        flash("Password must be at least 8 characters long", "error")
        return render_template("change_password.html"), 400

    # se digitar errado a confirmação
    if new != confirm:
        flash("Passwords do not match", "error")
        return render_template("change_password.html"), 400

    # se a nova senha for a senha antiga
    if verify_password(hashed, new):
        flash("New password must be different from the current one", "error")
        return render_template("change_password.html"), 400

    # atualiza senha e redireciona para home
    update_user_hash(user_id, hash_password(new))
    flash("Password changed successfully", "success")
    return redirect(url_for("home"))

# Excluir conta: GET mostra a página de confirmação, POST confirma com a senha e apaga
@login_required
def delete_account():
    # GET
    if request.method == "GET":
        return render_template("delete_account.html")

    # POST
    password = request.form.get("password", "") # senha do formulario
    user_id = session["user_id"] # id da sessão 
    hashed = get_user_hash(user_id) # hash do usuario

    # se nao digitar senha 
    if len(password) == 0:
        flash("Please enter your password", "error")
        return render_template("delete_account.html"), 400

    # sessão aponta para um usuário que não existe mais (conta excluída / banco recriado)
    if hashed is None:
            session.clear()
            flash("Your session is no longer valid, please log in again", "error")
            return redirect(url_for("login"))

    # se a senha estiver errada
    if not verify_password(hashed, password):
        flash("Incorrect password", "error")
        return render_template("delete_account.html"), 401

    # deleta usuário
    delete_user(user_id)
    session.clear()
    flash("Your account was deleted", "info")
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