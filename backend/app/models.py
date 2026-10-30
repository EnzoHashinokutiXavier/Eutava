from app.db import get_connection
from psycopg.errors import UniqueViolation, CheckViolation
from app.attendance import Course

# verificar se usuário existe  
def user_exists(username):
    # se username existe no banco de dados
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE name = %s", (username,))
            return cur.fetchone() is not None

# verificar se email já está cadastrado
def email_exists(email):
    # se email existe no banco de dados
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE email = %s", (email,))
            return cur.fetchone() is not None

# criar usuário
def create_user(username, email, password_hash):
    # Cria um novo usuário no banco de dados
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO users (name, email, hash_password) VALUES (%s, %s, %s) RETURNING user_id",(username, email, password_hash))
                return cur.fetchone()[0]
    # erro da validação da regra unique do banco
    except UniqueViolation:
        return None

# pegar id do usuário pelo email
def get_user(email):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, name, hash_password FROM users WHERE email = %s",(email,))
            return cur.fetchone()

# pegar hash por id 
def get_user_hash(user_id):
    # Pega o hash no banco de dados
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT hash_password FROM users WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            return row[0] if row else None

# atualizar hash do usuário pelo id
def update_user_hash(user_id, new_hash):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET hash_password = %s WHERE user_id = %s", (new_hash, user_id))
            return cur.rowcount == 1

# deletar usuário pelo id
def delete_user(user_id):
    # Deleta o usuário do banco de dados
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            return cur.rowcount == 1

# cria a materia no banco linkado ao usuario e tambem ja insere os dias da semana quando tem aula e quantas aulas
def create_course(user_id, name, absence_limit, default_presence, start_date, end_date, schedule):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO courses (user_id, name, absence_limit, default_presence, start_date, end_date)"
                " VALUES (%s,%s,%s,%s,%s,%s) RETURNING course_id", 
                (user_id, name, absence_limit, default_presence, start_date, end_date))
            course_id = cur.fetchone()[0]
            for weekday, qtd_classes in schedule.items():
                cur.execute(
                    "INSERT INTO schedule (course_id, weekday, qtd_classes)"
                    " VALUES (%s, %s, %s)",
                    (course_id, weekday, qtd_classes)
                )
            return course_id

# lista as materias do usuario (retorna uma lista de tuplas [...])
def get_courses(user_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT course_id, name, absence_limit, default_presence, start_date, end_date "
                " FROM courses WHERE user_id = %s ORDER BY name", 
                (user_id, ))
            return cur.fetchall()

# lista os dados de uma materia e retorna uma tupla com 6 elementos
def get_course(course_id, user_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT course_id, name, absence_limit, default_presence, start_date, end_date"
                " FROM courses WHERE course_id = %s AND user_id = %s",
                (course_id, user_id)
            )
            return cur.fetchone()

# lista os dias da semana em que tem aula da materia retorna um dict {...} com int nas chaves e int nos valores
def get_schedule(course_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT weekday, qtd_classes FROM schedule WHERE course_id = %s", (course_id, )
            )
            return dict(cur.fetchall())

# Presença: set_attendance(course_id, date, qtd_classes, absences) (com ON CONFLICT (course_id, date) DO UPDATE), get_attendances(course_id) e delete_attendance
def set_attendance(course_id, date, qtd_classes, absences):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO attendance (course_id, date, qtd_classes, absences)"
                    " VALUES (%s, %s, %s, %s) ON CONFLICT (course_id, date) DO UPDATE"
                    " SET qtd_classes = EXCLUDED.qtd_classes, absences = EXCLUDED.absences"
                    " RETURNING attendance_id",
                    (course_id, date, qtd_classes, absences)
                )
                return cur.fetchone()[0]
    except CheckViolation:
        return None

# Captura um attendance atraves do course_id e retorna as colunas (date, qtd_classes e absences)
def get_attendances(course_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT date, qtd_classes, absences FROM attendance WHERE course_id = %s",
                (course_id, )
            )
            return {day: (qtd_classes, absences) for day, qtd_classes, absences in cur.fetchall()}

# Deleta o attendance do banco usando o course_id e date
def delete_attendance(course_id, date):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM attendance WHERE course_id = %s AND date = %s",
                (course_id, date)
            )
            return cur.rowcount == 1
        
# Feriados: add_holiday, get_holidays e delete_holiday
def add_holiday(start_date, end_date, description, user_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO holidays (user_id, description, start_date, end_date)"
                    " VALUES (%s, %s, %s, %s)"
                    " RETURNING holiday_id",
                    (user_id, description, start_date, end_date)
                )
                return cur.fetchone()[0]
    except CheckViolation:
        return None

def get_holidays(user_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT holiday_id, start_date, end_date, description FROM holidays WHERE user_id = %s"
                " ORDER BY start_date",
                (user_id, )
            )
            return cur.fetchall()

def delete_holiday(user_id, holiday_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM holidays WHERE holiday_id = %s AND user_id = %s",
                (holiday_id, user_id)
            )
            return cur.rowcount == 1
# Matérias: update_course, delete_course e update_schedule
def update_course(course_id, user_id, name, absence_limit, default_presence, start_date, end_date):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE courses SET name = %s, absence_limit = %s, default_presence = %s, start_date = %s, end_date = %s"
                    " WHERE  course_id = %s AND user_id = %s",
                    (name, absence_limit, default_presence, start_date, end_date, course_id, user_id)
                )
                return cur.rowcount == 1
    except CheckViolation:
        return None

def delete_course(course_id, user_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM courses WHERE course_id = %s AND user_id = %s",
                (course_id, user_id)
            )
            return cur.rowcount == 1

# construção e retorno do objeto course incluindo name, max_abs, default_present, start_date, end_date, schedule, attendances e holidays
def build_course(row, user_holidays):
    course_id, name, absence_limit, default_presence, start_date, end_date = row

    holidays = []

    # recebe os holidays do usuario ja buscados no banco e monta a list sem o holiday_id
    for _, start, end, desc in user_holidays:
        holidays.append((start, end, desc))
    
    return Course(
        name=name,
        max_abs=absence_limit,
        default_present=default_presence,
        start_date=start_date,
        end_date=end_date,
        schedule=get_schedule(course_id),
        attendances=get_attendances(course_id),
        holidays=holidays
    )
