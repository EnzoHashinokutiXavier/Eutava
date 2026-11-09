# conexão do backend com banco de dados PostgreSQL

import os # os lê variáveis de ambiente do arquivo .env
from pathlib import Path # path trabalha com caminhos de arquivos e pastas
import psycopg # biblioteca para conectar com PostgreSQL
from dotenv import load_dotenv

# carrega variáveis de ambiente do .env para o ambiente do sistema operacional
load_dotenv() 

# decisão : Sem o caminho de pastas e url do db hardcoded para rodar em maquinas diferentes de maneira dinamica

# caminho do arquivo schema.sql que contém o esquema do banco de dados
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql" 
# resolve() retorna o caminho absoluto do arquivo atual
# parent retorna o diretório pai do arquivo atual
# "schema.sql" é o nome do arquivo que contém o esquema do banco de dados.

# variável que armazena a URL de conexão com o banco de dados
DATABASE_URL = os.environ["DATABASE_URL"] # url é um valor salvo em uma variável de ambiente

# função que retorna uma conexão com o banco de dados
def get_connection():
    return psycopg.connect(DATABASE_URL) # conecta banco com a url 

# função que inicializa o banco de dados com o esquema definido no arquivo schema.sql
def init_db():
    with get_connection() as conn: # get_connection() retorna a conexão com o banco de dados
        with conn.cursor() as cur: # .cursor() cria um cursor para executar comandos SQL
            cur.execute(SCHEMA_PATH.read_text()) # executa no cursor o comando SQL contido no arquivo schema.sql

