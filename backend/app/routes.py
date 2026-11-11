from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from app.decorators import login_required
from app.models import get_courses, get_holidays, build_course, create_course
from app.attendance import course_stats

# decisao : Blueprint foi escolhido para organizar as rotas relacionadas a matérias, separando-as das rotas de autenticação e de usuários.

bp = Blueprint("courses", __name__, url_prefix="/courses")

WARN_AT = 75  # % das faltas usadas a partir da qual o status vira "warn"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] # dias da semana

# GET /courses: listar matérias, com o status vindo de course_stats (safe/warn/risk)
@bp.route("/")
@login_required
def list_courses():
    today = date.today()
    courses = []
    user_holidays = get_holidays(session["user_id"])  # busca uma vez so, valem para todas as materias
    for row in get_courses(session["user_id"]):
        course = build_course(row, user_holidays)
        stats = course_stats(course, today, WARN_AT)  # {"used", "max", "status"}
        courses.append({"id": row[0], "name": course.name, **stats})
    return render_template("courses.html", courses=courses)

# GET/POST /courses/new: criar matéria (nome, limite de faltas, presença padrão, datas e os dias da semana com quantidade de aulas)
@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_course():
    if request.method == "GET":
        return render_template("new_course.html", weekdays=WEEKDAYS) # envia formulario

    # POST: pega os dados do form e cria a matéria
    name = request.form.get("name", "").strip() # "" serve para evitar None, que quebraria o strip()
    default_presence = request.form.get("default_presence") == "on" # checkbox só envia quando marcado 

    # pega os dias da semana com quantidade de aulas, que vem do form como "Monday": "2", "Tuesday": "", etc
    try:
        absence_limit = int(request.form.get("absence_limit", "")) # limite de faltas 
        start_date = date.fromisoformat(request.form.get("start_date", "")) # data de início
        end_date = date.fromisoformat(request.form.get("end_date", "")) # data de fim
        # fromisoformat lança ValueError se a string não estiver no formato YYYY-MM-DD
        # uso de ia: indicação do uso de fromisformat para converter strings de datas do formulário em objetos date, garantindo que as datas sejam manipuladas corretamente no backend.

    except ValueError:
        flash("Please fill in all fields with valid values", "error") # mensagem de erro para o usuário
        return render_template("new_course.html", weekdays=WEEKDAYS), 400 # volta para o form com status 400 (bad request)

    # monta o schedule {weekday: qtd_classes} só com os dias que têm aula
    # uso de ia : seguinte trecho da função foi adaptado de exemplo de ia para criar um dicionario
    schedule = {}
    for i in range(7): # para cada dia da semana (0=Monday, 6=Sunday)
        qtd = request.form.get(f"classes_{i}", "").strip() # pega a quantidade de aulas do dia i, se houver
        if qtd:
            # verifica se é digito positivo, se não for, retorna erro
            if not qtd.isdigit() or int(qtd) < 1: # primeiro verifica se é um dígito para não quebrar na comparação com numero 
                flash("Number of classes must be a positive number", "error")
                return render_template("new_course.html", weekdays=WEEKDAYS), 400
            # se for válido, adiciona ao schedule
            schedule[i] = int(qtd)

    # série de validações para garantir que os dados do formulário são coerentes
    if not name:
        flash("Please enter the course name", "error")
        return render_template("new_course.html", weekdays=WEEKDAYS), 400
    if absence_limit < 0:
        flash("Absence limit can't be negative", "error")
        return render_template("new_course.html", weekdays=WEEKDAYS), 400
    if end_date < start_date:
        flash("End date must be after start date", "error")
        return render_template("new_course.html", weekdays=WEEKDAYS), 400
    if not schedule:
        flash("Select at least one weekday with classes", "error")
        return render_template("new_course.html", weekdays=WEEKDAYS), 400

    # se tudo estiver ok, cria a matéria no banco de dados
    create_course(session["user_id"], name, absence_limit, default_presence, start_date, end_date, schedule)
    flash("Course created", "success")
    return redirect(url_for("courses.list_courses"))  # endpoint do blueprint = "courses.<função>"

# GET /courses/<id>: detalhe da matéria, com um calendário que usa day_info dia a dia
@bp.route("/<int:course_id>")
@login_required
def course_detail(course_id):
    today = date.today()
    user_holidays = get_holidays(session["user_id"])
    course = build_course(get_courses(session["user_id"], course_id), user_holidays)
    stats = course_stats(course, today, WARN_AT)
    return render_template("course_detail.html", course=course, stats=stats)

# POST /courses/<id>/edit e /delete
@bp.route("/<int:course_id>/edit", methods=["POST"])
@login_required
def edit_course(course_id):
    # !!! implementar
    return "Not implemented", 501

# POST /courses/<id>/attendance: marcar presença ou falta num dia
@bp.route("/<int:course_id>/attendance", methods=["POST"])
@login_required
def mark_attendance(course_id):
    # !!! implementar
    return "Not implemented", 501

# POST /courses/<id>/holidays: adicionar feriados e recessos
@bp.route("/<int:course_id>/holidays", methods=["POST"])
@login_required
def add_holidays(course_id):
    # !!! implementar
    return "Not implemented", 501