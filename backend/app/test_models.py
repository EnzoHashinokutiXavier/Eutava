from models import user_exists, email_exists, create_user, get_user, get_user_hash, update_user_hash, delete_user

# para usuario que nao existe user_exists deve retornar False
def test_user_exists():
    assert user_exists("nonexistent_user") == False

# para email que nao existe email_exists deve retornar False
def test_email_exists():
    assert email_exists("nonexistent_email") == False

# create_user e depois verificar se user_exists retorna True e se email_exists retorna True
def test_create_user():
    create_user("test_user", "test_email", "test_hash")
    assert user_exists("test_user") == True
    assert email_exists("test_email") == True

# get_user deve retornar o id do usuario, nome e hash
def test_get_user():
    user = get_user("test_user")
    assert user["id"] == "test_user"
    assert user["name"] == "test_user"
    assert user["hash"] == "test_hash"

# update_user_hash deve atualizar o hash do usuario e retornar True
def test_update_user_hash():
    assert update_user_hash("test_user", "new_hash") == True

# get_user_hash deve retornar o hash correto do usuario
def test_get_user_hash():
    assert get_user_hash("test_user") == "new_hash"

# delete_user deve remover o usuario e retornar True, depois verificar se user_exists retorna False e se email_exists retorna False
def test_delete_user():
    assert delete_user("test_user") == True
    assert user_exists("test_user") == False
    assert email_exists("test_email") == False