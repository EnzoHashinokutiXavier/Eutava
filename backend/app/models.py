
# Registro

def register_user(username, email, password):
    try:
        # validate the input data
        # verify if the email is already in use
        # hash the password
        # sql insert the new user into the database
        # confirm the registration was successful
        return {"message": "User registered successfully"}
    return {"message": "Error registering user"}


# Login

def login_user(email, password):
    try:
        # validate the input data
        # verify if the email exists
        # check if the password is correct
        # create a session or token for the user
        return {"message": "User logged in successfully"}
    return {"message": "Error logging in user"}


# Deletar usuário

def delete_user(user_id):
    try:
        # validate the input data
        # verify if the user exists
        # sql delete the user from the database
        return {"message": "User deleted successfully"}
    return {"message": "Error deleting user"}