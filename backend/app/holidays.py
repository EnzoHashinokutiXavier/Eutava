from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from app.decorators import login_required
from app.models import add_holiday, get_holidays, delete_holiday, holiday_overlaps

# decisao : feriados ganharam um blueprint próprio porque pertencem ao usuário, não a uma matéria
bp = Blueprint("holidays", __name__, url_prefix="/holidays")

# GET /holidays: lista os feriados do usuário e mostra o formulário de cadastro
@bp.route("/")
@login_required
def list_holidays():
    holidays = get_holidays(session["user_id"])  # lista de tuplas (holiday_id, start_date, end_date, description)
    return render_template("holidays.html", holidays=holidays)

# mostra a página de feriados de novo com uma mensagem de erro
# o status 400 avisa o navegador que o formulário tinha problema
# o que o usuário digitou continua no formulário (o template lê request.form)
def show_form_error(user_id, message):
    flash(message, "error")
    holidays = get_holidays(user_id)
    return render_template("holidays.html", holidays=holidays), 400


# POST /holidays: cadastra um feriado (vale para todas as matérias do usuário)
@bp.route("/", methods=["POST"])
@login_required
def create_holiday():
    user_id = session["user_id"]

    # pegar o que o usuário digitou
    description = request.form.get("description", "").strip()
    start_text = request.form.get("start_date", "")
    end_text = request.form.get("end_date", "").strip()

    # transformar os textos em datas
    try:
        start_date = date.fromisoformat(start_text)

        if end_text == "":
            end_date = start_date  # sem data final = feriado de um dia só
        else:
            end_date = date.fromisoformat(end_text)

    except ValueError:  # acontece quando a data está vazia ou em formato errado
        return show_form_error(user_id, "Please fill in all fields with valid values")

    # validar os dados
    if description == "":
        return show_form_error(user_id, "Please enter a description")
    if end_date < start_date:
        return show_form_error(user_id, "End date must be after start date")
    if holiday_overlaps(user_id, start_date, end_date):
        return show_form_error(user_id, "There is already a holiday on one of these days")

    # salvar no banco
    new_holiday = add_holiday(start_date, end_date, description, user_id)
    if new_holiday is None:
        return show_form_error(user_id, "Error saving holiday")

    flash("Holiday added", "success")
    return redirect(url_for("holidays.list_holidays"))

# POST /holidays/<id>/delete: remove um feriado do usuário
@bp.route("/<int:holiday_id>/delete", methods=["POST"])
@login_required
def remove_holiday(holiday_id):
    # delete_holiday já filtra por user_id, então um usuário não consegue apagar feriado de outro
    if delete_holiday(session["user_id"], holiday_id):
        flash("Holiday removed", "success")
    else:
        flash("Holiday not found", "error")
    return redirect(url_for("holidays.list_holidays"))