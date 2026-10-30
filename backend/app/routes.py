from datetime import date
from flask import Blueprint, render_template, session
from app.decorators import login_required
from app.models import get_courses, get_holidays, build_course
from app.attendance import course_stats

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
# GET /courses/<id>: detalhe da matéria, com um calendário que usa day_info dia a dia
# POST /courses/<id>/edit e /delete
# POST /courses/<id>/attendance: marcar presença ou falta num dia
# POST /courses/<id>/holidays: adicionar feriados e recessos