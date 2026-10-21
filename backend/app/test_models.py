import pytest
from models import user_exists, email_exists, create_user, get_user, get_user_hash, update_user_hash, delete_user

TEST_NAME = "test_user"
TEST_EMAIL = "test_email"
TEST_HASH = "test_hash"

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

# delete_user deve remover o usuario e retornar True, depois user_exists e email_exists devem retornar False
def test_delete_user(user_id):
    assert delete_user(user_id) == True
    assert user_exists(TEST_NAME) == False
    assert email_exists(TEST_EMAIL) == False
