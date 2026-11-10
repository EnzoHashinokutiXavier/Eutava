from datetime import date
from flask import Blueprint, render_template, request, session
from app.decorators import login_required
from app.models import get_courses, get_holidays, build_course
from app.attendance import course_stats

# decisao : Blueprint foi escolhido para organizar as rotas relacionadas a matérias, separando-as das rotas de autenticação e de usuários.

bp = Blueprint("courses", __name__, url_prefix="/courses")

WARN_AT = 75  # % das faltas usadas a partir da qual o status vira "warn"

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
        return render_template("new_course.html")
    return "Not implemented", 501  # !!! implementar

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