
# verificar se usuário existe  
def user_exists(username):
    # se username existe no banco de dados
    if ():
        return True
    return False

# verificar se email já está cadastrado
def  email_exists(email):
    # se email existe no banco de dados
    if ():
        return True
    return False

# criar usuário
def create_user(username, email, password_hash):
    # Cria um novo usuário no banco de dados
    try:
        return True
    except:
        return False

# pegar id do usuário pelo username
def get_user_id(username):
    # Pega o ID no banco de dados
    try:
        return user_id
    except:
        return None

# pegar hash por id 
def get_user_hash(user_id):
    # Pega o hash no banco de dados
    try:
        return user_hash
    except:
        return None

# atualizar hash do usuário pelo id
def update_user_hash(user_id, new_hash):
    # Atualiza o hash do usuário no banco de dados
    try:
        return True
    except:
        return False

# deletar usuário pelo id
def delete_user(user_id):
    # Deleta o usuário do banco de dados
    try:
        return True
    except:
        return False
