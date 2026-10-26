from functools import wraps
from flask import session, flash, redirect, url_for


# Decorator para rotas que exigem login, se não estiver logado redireciona para pagina de login
def login_required(view):
    @wraps(view) # @wraps: mantém o nome original da função. Sem ele todas as rotas protegidas ficariam com o nome wrapped_view, o que gera conflito no Flask e quebra o url_for
    def wrapped_view(*args, **kwargs): # wrapped_view: função que envolve a view original, recebe os mesmos argumentos da view original
        if "user_id" not in session: # se não estiver logado, redireciona para pagina de login
            flash("You're not logged in!", "info")
            return redirect(url_for("login"))
        return view(*args, **kwargs) # chama a view original com os mesmos argumentos
    return wrapped_view # retorna a função que envolve a view original, que será chamada no lugar da view original
