from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from app.decorators import login_required
from app.models import get_course, get_courses, get_holidays, build_course, create_course, get_schedule, set_attendance, update_course, update_schedule, delete_attendance, add_holiday
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

    row = get_course(course_id, session["user_id"]) # busca a matéria no banco de dados
    if row is None:
        flash("Course not found", "error")
        return redirect(url_for("courses.list_courses"))

    today = date.today()
    user_holidays = get_holidays(session["user_id"])
    course = build_course(row, user_holidays)
    stats = course_stats(course, today, WARN_AT)
    return render_template("course_detail.html", course=course, stats=stats)

# GET/POST /courses/<id>/edit: editar matéria (nome, limite de faltas, presença padrão, datas e os dias da semana com quantidade de aulas)
@bp.route("/<int:course_id>/edit", methods=["GET", "POST"])
@login_required
def edit_course(course_id):
    row = get_course(course_id, session["user_id"]) # busca a matéria no banco de dados

    # se matéria não existir, volta para pagina de matérias com mensagem de erro
    if row is None:
        flash("Course not found", "error")
        return redirect(url_for("courses.list_courses"))

    # busca o schedule da matéria no banco de dados
    schedule = get_schedule(course_id) 

    # GET : renderiza o formulário com os dados da matéria
    if request.method == "GET":
        return render_template("edit_course.html", weekdays=WEEKDAYS, course=row, schedule=schedule)

    # POST : pega os dados do form e atualiza a matéria

    name = request.form.get("name", "").strip()
    default_presence = request.form.get("default_presence") == "on"

    try:
        absence_limit = int(request.form.get("absence_limit", ""))
        start_date = date.fromisoformat(request.form.get("start_date", ""))
        end_date = date.fromisoformat(request.form.get("end_date", ""))
    except ValueError:
        flash("Please fill in all fields with valid values", "error")
        return render_template("edit_course.html", weekdays=WEEKDAYS, course=row, schedule=schedule), 400

    new_schedule = {}
    for i in range(7):
        qtd = request.form.get(f"classes_{i}", "").strip()
        if qtd:
            if not qtd.isdigit() or int(qtd) < 1:
                flash("Number of classes must be a positive number", "error")
                return redirect(url_for("courses.edit_course", course_id=course_id))
            new_schedule[i] = int(qtd)

    # se faltar algum campo, volta para pagina de edição do curso com mensagem de erro
    if not name:
        flash("Please enter the course name", "error")
        return redirect(url_for("courses.edit_course", course_id=course_id))
    if absence_limit < 0:
        flash("Absence limit can't be negative", "error")
        return redirect(url_for("courses.edit_course", course_id=course_id))
    if end_date < start_date:
        flash("End date must be after start date", "error")
        return redirect(url_for("courses.edit_course", course_id=course_id))
    if not new_schedule:
        flash("Select at least one weekday with classes", "error")
        return redirect(url_for("courses.edit_course", course_id=course_id))

    # se tudo estiver ok, atualiza a matéria no banco de dados
    ok = update_course(course_id, session["user_id"], name, absence_limit, default_presence, start_date, end_date)
    if not ok or not update_schedule(course_id, new_schedule):
        flash("Error updating course", "error")
        return redirect(url_for("courses.edit_course", course_id=course_id))


    flash("Course updated", "success")
    return redirect(url_for("courses.course_detail", course_id=course_id))


# POST /courses/<id>/attendance: marcar presença ou falta num dia
@bp.route("/<int:course_id>/attendance", methods=["POST"])
@login_required
def mark_attendance(course_id):

    # verificar se a matéria existe e pertence ao usuário logado
    row = get_course(course_id, session["user_id"])
    # se não existir, volta para pagina de matérias com mensagem de erro
    if row is None:
        flash("Course not found", "error")
        return redirect(url_for("courses.list_courses"))

    # pegar dados do form
    try:
        day = date.fromisoformat(request.form.get("day", "")) # date.fromisoformat lança ValueError se a string não estiver no formato YYYY-MM-DD
        qtd_classes = int(request.form.get("qtd_classes", ""))
        absences = int(request.form.get("absences", "0")) # 0 se não for enviado
    except ValueError:
        flash("Please fill in all fields with valid values", "error")
        return redirect(url_for("courses.course_detail", course_id=course_id))

    # verificar se a data está dentro do período da matéria
    start_date = row[4] # start_date vem do banco de dados
    end_date = row[5] # end_date vem do banco de dados
    # se a data estiver fora do período, volta para pagina de detalhes da matéria com mensagem de erro
    if day < start_date or day > end_date:
        flash("Date is outside the course period", "error")
        return redirect(url_for("courses.course_detail", course_id=course_id))

    # botão limpar remove registro e volta ao comportamento padrão (presença padrão da matéria)
    if request.form.get("action") == "clear":
        delete_attendance(course_id, day)
        flash("Attendance cleared for this day", "success")
        return redirect(url_for("courses.course_detail", course_id=course_id))

    # validação iguais as do banco (qtd_classes >= 0, absences >= 0, absences <= qtd_classes
    if qtd_classes < 0:  
        flash("Number of classes can't be negative", "error")
        return redirect(url_for("courses.course_detail", course_id=course_id))
    if absences < 0 or absences > qtd_classes:
        flash("Number of absences must be between 0 and number of classes", "error")
        return redirect(url_for("courses.course_detail", course_id=course_id))

    # salva no banco (atualiza se já existir, insere se não existir)
    if set_attendance(course_id, day, qtd_classes, absences) is None:
        flash("Error saving attendance", "error")
        return redirect(url_for("courses.course_detail", course_id=course_id))

    # se tudo der certo
    flash("Attendance saved", "success")
    return redirect(url_for("courses.course_detail", course_id=course_id))

# POST /courses/<id>/holidays: adicionar feriados e recessos
@bp.route("/<int:course_id>/holidays", methods=["POST"])
@login_required
def add_holidays(course_id):

    # verificar se a matéria existe e pertence ao usuário logado
    row = get_course(course_id, session["user_id"])
    # se não existir, volta para pagina de matérias com mensagem de erro
    if row is None:
        flash("Course not found", "error")
        return redirect(url_for("courses.list_courses"))

    # pega dados do form
    description = request.form.get("description", "").strip()
    try:
        start_date = date.fromisoformat(request.form.get("start_date", ""))
        end_raw = request.form.get("end_date", "").strip()
        # se preencheu end_raw converte texto com a data em um objeto
        if end_raw: # string vazia conta como False, preenchida como True
            end_date = date.fromisoformat(end_raw)
        else:
            end_date = start_date
    # se nao preenchido, volta para pagina de detalhes da matéria com mensagem de erro
    except ValueError:
        flash("Please fill in all fields with valid values", "error")
        return redirect(url_for("courses.course_detail", course_id=course_id))

    # validações iguais às do banco (description NOT NULL, end_date >= start_date)
    if not description:
        flash("Please enter a description", "error")
        return redirect(url_for("courses.course_detail", course_id=course_id))
    if end_date < start_date:
        flash("End date must be after start date", "error")
        return redirect(url_for("courses.course_detail", course_id=course_id))

    # salva no banco (feriado é do usuário, vale para todas as matérias)
    if add_holiday(start_date, end_date, description, session["user_id"]) is None:
        flash("Error saving holiday", "error")
        return redirect(url_for("courses.course_detail", course_id=course_id))

    flash("Holiday added", "success")
    return redirect(url_for("courses.course_detail", course_id=course_id))