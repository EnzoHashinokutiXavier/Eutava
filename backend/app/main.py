from pathlib import Path
from flask import Flask, render_template, redirect, url_for, request, session, flash
from datetime import date, timedelta
from app.db import init_db
from app.decorators import login_required
from app.routes import bp as courses_bp, WARN_AT
from app.holidays import bp as holidays_bp
from app.models import create_user, get_user, get_user_hash, get_user_info, update_user_hash, update_user_name, update_user_email, delete_user, get_courses, get_holidays, build_course
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
    # decisao : só login e register têm template próprio. As rotas da conta (settings, nome, email, senha, excluir) não entram aqui porque settings.html precisa de name e email, que o handler não tem
    templates = {"login": "login.html", "register": "register.html"}
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
    templates = {"login": "login.html", "register": "register.html"}
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

# uso de ia : análise do código e identificação de problemas que levaram as seguintes decisões
# decisao : os formulários da conta (nome, email, senha e excluir conta) ficam todos em settings.html, então as rotas abaixo só aceitam POST e o GET é a rota settings.
# decisao : em caso de erro as rotas fazem redirect para settings em vez de render_template(..., 400). Motivos:
# - settings.html precisa de name e email, e a rota GET settings já busca esses dados no banco (não precisa repetir em cada erro)
# - padrão Post/Redirect/Get: se o usuário apertar F5 depois do erro, o navegador não reenvia o formulário com as senhas
# - o flash sobrevive ao redirect, então a mensagem de erro aparece normalmente
# - ponto negativo: a resposta vira 302 em vez de 400/401. Para o usuário não muda nada, só para quem olha o status HTTP

# Troca de senha : POST valida e atualiza, sempre volta para settings (o formulário fica em settings.html)
@app.route("/account/password", methods=["POST"])
@login_required
def change_password():
    current = request.form.get("current_password", "") # usuario digita senha atual
    new = request.form.get("new_password", "") # usuario digita nova senha
    confirm = request.form.get("confirm_password", "") # digita novamente nova senha 

    # verificação campo vazio
    if len(current) == 0:
        flash("Please enter the current password", "error")
        return redirect(url_for("settings"))
    if len(new) == 0:
        flash("Please enter the new password", "error")
        return redirect(url_for("settings"))
    if len(confirm) == 0:
        flash("Please confirm new password", "error")
        return redirect(url_for("settings"))

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
        return redirect(url_for("settings"))

    # se senha menor que oito caracteres
    if len(new) < 8:
        flash("Password must be at least 8 characters long", "error")
        return redirect(url_for("settings"))

    # se digitar errado a confirmação
    if new != confirm:
        flash("Passwords do not match", "error")
        return redirect(url_for("settings"))

    # se a nova senha for a senha antiga
    if verify_password(hashed, new):
        flash("New password must be different from the current one", "error")
        return redirect(url_for("settings"))

    # atualiza senha e volta para settings
    update_user_hash(user_id, hash_password(new))
    flash("Password changed successfully", "success")
    return redirect(url_for("settings"))

# Configurações : mostra nome e email atuais e os formulários da conta
@app.route("/account/settings")
@login_required
def settings():
    info = get_user_info(session["user_id"])
    if info is None:  # mesmo caso de sessão órfã de change_password
        session.clear()
        flash("Your session is no longer valid, please log in again", "error")
        return redirect(url_for("login"))
    name, email = info
    return render_template("settings.html", name=name, email=email)

# Troca de nome : POST valida e atualiza, sempre volta para settings
@app.route("/account/name", methods=["POST"])
@login_required
def change_name():
    name = request.form.get("name", "").strip()

    if len(name) == 0:
        flash("Please enter your name", "error")
        return redirect(url_for("settings"))

    # rowcount 0 = usuário não existe mais (sessão órfã)
    if not update_user_name(session["user_id"], name):
        session.clear()
        flash("Your session is no longer valid, please log in again", "error")
        return redirect(url_for("login"))

    # decisao : o nome também fica guardado em session["user"] (definido no login) e a home mostra esse valor, então é atualizado aqui para o nome novo aparecer sem precisar logar de novo
    session["user"] = name
    flash("Name changed successfully", "success")
    return redirect(url_for("settings"))

# Troca de email : POST valida e atualiza, sempre volta para settings
# decisao : trocar o email exige a senha atual, porque o email é o login da conta. Sem isso, alguém com acesso ao navegador logado poderia trocar o email e tomar a conta
@app.route("/account/email", methods=["POST"])
@login_required
def change_email():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    # verificação campo vazio
    if len(email) == 0 or len(password) == 0:
        flash("Please fill in all fields", "error")
        return redirect(url_for("settings"))

    user_id = session["user_id"]
    hashed = get_user_hash(user_id)

    # sessão aponta para um usuário que não existe mais
    if hashed is None:
        session.clear()
        flash("Your session is no longer valid, please log in again", "error")
        return redirect(url_for("login"))

    # se a senha estiver errada
    if not verify_password(hashed, password):
        flash("Incorrect password", "error")
        return redirect(url_for("settings"))

    # decisao : mesma validação do register (lower + validate_email sem checar DNS), para o email salvo ter sempre o mesmo formato e o login continuar funcionando
    try:
        email = validate_email(email, check_deliverability=False).email
    except EmailNotValidError:
        flash("Please enter a valid email address", "error")
        return redirect(url_for("settings"))

    # se o email novo for igual ao atual
    info = get_user_info(user_id)
    if info is not None and info[1] == email:
        flash("New email must be different from the current one", "error")
        return redirect(url_for("settings"))

    # decisao : não usa email_exists() antes do UPDATE porque entre a consulta e o UPDATE outro cadastro poderia usar o mesmo email. A regra UNIQUE do banco garante isso e update_user_email retorna None quando ela é violada
    if update_user_email(user_id, email) is None:
        flash("This email is already registered", "error")
        return redirect(url_for("settings"))

    flash("Email changed successfully", "success")
    return redirect(url_for("settings"))

# Excluir conta : POST confirma com a senha e apaga (o formulário fica em settings.html)
@app.route("/account/delete", methods=["POST"])
@login_required
def delete_account():
    password = request.form.get("password", "") # senha do formulario
    user_id = session["user_id"] # id da sessão

    # se nao digitar senha
    if len(password) == 0:
        flash("Please enter your password", "error")
        return redirect(url_for("settings"))

    hashed = get_user_hash(user_id) # hash do usuario

    # sessão aponta para um usuário que não existe mais (conta excluída / banco recriado)
    if hashed is None:
        session.clear()
        flash("Your session is no longer valid, please log in again", "error")
        return redirect(url_for("login"))

    # se a senha estiver errada
    if not verify_password(hashed, password):
        flash("Incorrect password", "error")
        return redirect(url_for("settings"))

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