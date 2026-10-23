import pytest
from datetime import date
from models import user_exists, email_exists, create_user, get_user, get_user_hash, update_user_hash, delete_user, create_course, get_course, get_courses, get_schedule 

TEST_NAME = "test_user"
TEST_EMAIL = "test_email"
TEST_HASH = "test_hash"

TEST_COURSE_NAME = "test_course"
TEST_ABSENCE_LIMIT = 10
TEST_DEFAULT_PRESENCE = True
TEST_START_DATE = date(2026, 2, 1)
TEST_END_DATE = date(2026, 6, 30)
TEST_SCHEDULE = {0: 2, 2: 1, 4: 3} # segunda: 2 aulas, quarta: 1 aula, sexta: 3 aulas

# remove o usuario de teste caso tenha sobrado de uma execucao anterior
def cleanup():
    user = get_user(TEST_EMAIL)
    if user is not None:
        delete_user(user[0])

# cria o usuario de teste antes de cada teste e remove depois, para os testes nao dependerem da ordem
@pytest.fixture  # fixture fornece um valor para os testes que precisam de um usuario criado
def user_id(): # passa id para os testes que precisam de um usuario criado
    cleanup() #limpa antes de criar o usuario de teste
    uid = create_user(TEST_NAME, TEST_EMAIL, TEST_HASH) # uid armazena o id do usuario criado
    yield uid # passa o id do usuario criado para os testes
    cleanup() # limpa depois de cada teste

# cria uma materia para o usuario de teste, removida junto com o usuario ON DELETE CASCADE
@pytest.fixture
def course_id(user_id):
    return create_course(user_id, TEST_COURSE_NAME, TEST_ABSENCE_LIMIT, TEST_DEFAULT_PRESENCE, TEST_START_DATE, TEST_END_DATE, TEST_SCHEDULE)

# para usuario que nao existe user_exists deve retornar False
def test_user_exists():
    assert user_exists("nonexistent_user") == False

# para email que nao existe email_exists deve retornar False
def test_email_exists():
    assert email_exists("nonexistent_email") == False

# create_user deve retornar o id e depois user_exists e email_exists devem retornar True
def test_create_user(user_id):
    assert isinstance(user_id, int)
    assert user_exists(TEST_NAME) == True
    assert email_exists(TEST_EMAIL) == True

# create_user com email repetido deve retornar None
def test_create_user_duplicate_email(user_id):
    assert create_user("other_user", TEST_EMAIL, "other_hash") is None

# get_user deve retornar (id, nome, hash) buscando pelo email
def test_get_user(user_id):
    assert get_user(TEST_EMAIL) == (user_id, TEST_NAME, TEST_HASH)

# get_user para email que nao existe deve retornar None
def test_get_user_nonexistent():
    assert get_user("nonexistent_email") is None

# get_user_hash deve retornar o hash correto do usuario
def test_get_user_hash(user_id):
    assert get_user_hash(user_id) == TEST_HASH

# update_user_hash deve atualizar o hash do usuario e retornar True
def test_update_user_hash(user_id):
    assert update_user_hash(user_id, "new_hash") == True
    assert get_user_hash(user_id) == "new_hash"

# delete_user para usuario que nao existe deve retornar False
def test_delete_user_nonexistent():
    assert delete_user(999999) == False

# delete_user deve remover o usuario e retornar True, depois user_exists e email_exists devem retornar False
def test_delete_user(user_id):
    assert delete_user(user_id) == True
    assert user_exists(TEST_NAME) == False
    assert email_exists(TEST_EMAIL) == False

# create_course deve retornar o id da materia criada
def test_create_course(course_id):
    assert isinstance(course_id, int)

# get_course deve retornar (id, nome, limite de faltas, presenca padrao, inicio, fim)
def test_get_course(user_id, course_id):
    assert get_course(course_id, user_id) == (course_id, TEST_COURSE_NAME, TEST_ABSENCE_LIMIT, TEST_DEFAULT_PRESENCE, TEST_START_DATE, TEST_END_DATE)

# get_course para materia que nao existe deve retornar None
def test_get_course_nonexistent(user_id):
    assert get_course(999999, user_id) is None

# get_course nao deve retornar materia de outro usuario
def test_get_course_other_user(user_id, course_id):
    assert get_course(course_id, 999999) is None

# get_courses deve retornar as materias do usuario ordenadas pelo nome
def test_get_courses(user_id, course_id):
    other_id = create_course(user_id, "a_course", 5, False, TEST_START_DATE, TEST_END_DATE, {1: 1})
    courses = get_courses(user_id)
    assert [c[0] for c in courses] == [other_id, course_id]
    assert courses[1] == (course_id, TEST_COURSE_NAME, TEST_ABSENCE_LIMIT, TEST_DEFAULT_PRESENCE, TEST_START_DATE, TEST_END_DATE)

# get_courses para usuario sem materias deve retornar lista vazia
def test_get_courses_empty(user_id):
    assert get_courses(user_id) == []

# get_schedule deve retornar o dict {dia da semana: quantidade de aulas} passado no create_course
def test_get_schedule(course_id):
    assert get_schedule(course_id) == TEST_SCHEDULE

# get_schedule para materia que nao existe deve retornar dict vazio
def test_get_schedule_nonexistent():
    assert get_schedule(999999) == {}

# delete_user deve remover tambem as materias do usuario (ON DELETE CASCADE)
def test_delete_user_removes_courses(user_id, course_id):
    delete_user(user_id)
    assert get_course(course_id, user_id) is None
    assert get_schedule(course_id) == {}

