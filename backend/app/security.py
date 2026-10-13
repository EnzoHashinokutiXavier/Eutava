from argon2 import PasswordHasher, Type
from argon2.exceptions import VerificationError, InvalidHashError

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
    hashed = ph.hash(password)
    return hashed

# Verifica a senha se o hash bate.
def verify_password(hashed, password):
    try: 
        ph.verify(hashed, password)
        return True
    except (VerificationError, InvalidHashError):
        return False
