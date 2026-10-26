
# GET /courses: listar matérias, com o status vindo de course_stats (safe/warn/risk)
# GET/POST /courses/new: criar matéria (nome, limite de faltas, presença padrão, datas e os dias da semana com quantidade de aulas)
# GET /courses/<id>: detalhe da matéria, com um calendário que usa day_info dia a dia
# POST /courses/<id>/edit e /delete
# POST /courses/<id>/attendance: marcar presença ou falta num dia
# POST /courses/<id>/holidays: adicionar feriados e recessos