from argon2 import PasswordHasher, Type
from argon2.exceptions import VerificationError, InvalidHashError

# argon2 é um algoritmo de hashing de senha que é resistente a ataques de força bruta e ataques de dicionário. 

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
    type=Type.ID
)

# Gera o hash pra senha
def hash_password(password):
    hashed = ph.hash(password) # ph.hash() é o método que gera o hash da senha usando os parâmetros definidos na instância PasswordHasher.
    return hashed

# Verifica a senha se o hash bate.
def verify_password(hashed, password):
    try: 
        ph.verify(hashed, password) # ph.verify() é o método que verifica se a senha fornecida corresponde ao hash armazenado. 
        return True
    except (VerificationError, InvalidHashError): 
        return False
