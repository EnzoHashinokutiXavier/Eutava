from security import hash_password, verify_password, is_safe_string

# teste para hash da password
def test_hash_password():
    password = "my_secure_password"
    hashed = hash_password(password)
    
    # Verifica se o hash não é None e não é igual à senha original
    assert hashed is not None
    assert hashed != password

# teste para verificação da senha
def test_verify_password():
    password = "my_secure_password"
    hashed = hash_password(password)
    
    # Verifica se a senha verificada é True para a senha correta
    assert verify_password(hashed, password) is True
    
    # Verifica se a senha verificada é False para uma senha incorreta
    assert verify_password(hashed, "wrong_password") is False