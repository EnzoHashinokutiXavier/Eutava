from models import user_exists, email_exists, create_user, get_user, get_user_hash, update_user_hash, delete_user

# para usuario que nao existe user_exists deve retornar False
# para email que nao existe email_exists deve retornar False
# create_user e depois verificar se user_exists retorna True e se email_exists retorna True
# get_user deve retornar o id do usuario, nome e hash
# update_user_hash deve atualizar o hash do usuario e retornar True
# get_user_hash deve retornar o hash correto do usuario
# delete_user deve remover o usuario e retornar True, depois verificar se user_exists retorna False e se email_exists retorna False