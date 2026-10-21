from app.db import get_connection
from psycopg.errors import UniqueViolation

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
