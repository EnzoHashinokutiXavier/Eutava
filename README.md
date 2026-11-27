# Eutava
#### Video Demo:  <URL HERE>
#### Description:

Name: Enzo Hashinokuti Xavier  
Github: [EnzoHashinokutiXavier](https://github.com/EnzoHashinokutiXavier)  
LinkedIn: [Enzo Hashinokuti Xavier](https://www.linkedin.com/in/enzo-hashinokuti-xavier-33a267365/)  
edX Account: Enzo_HX  
city: Dourados-MS (Brasil/Brazil)  

Name: Augusto Corrêa  
Github: [Augustbr01](https://github.com/Augustbr01)  
LinkedIn: [Augusto Corrêa](https://www.linkedin.com/in/augusto-corr%C3%AAa/)  
edX Account: AugustoCorrea_  
city: Dourados-MS (Brasil/Brazil)  

## Overview

O **Eutava** é um site para estudantes controlarem as próprias faltas. O nome vem de "eu tava", jeito informal de dizer "eu estava (presente)" em português brasileiro.

Na faculdade, cada matéria tem um limite de faltas, e passar desse limite reprova o aluno mesmo com nota boa. Acompanhar isso de cabeça, ou numa planilha, é difícil: as matérias têm quantidades de aulas diferentes em cada dia da semana, existem feriados e recessos, e às vezes o aluno falta só em parte das aulas de um dia.

No Eutava, o usuário cadastra cada matéria com o limite de faltas, o período e a grade semanal. A partir daí, o site calcula quantas aulas já aconteceram, quantas faltas foram usadas e quantas ainda restam. Os feriados são descontados automaticamente, e os dias que o usuário não marcou seguem a presença padrão da matéria, então não é preciso registrar todo dia.

A página inicial mostra as aulas de hoje, para marcar a presença com um clique, e a lista de matérias com um status (**Safe**, **Warning** ou **At risk**), começando pelas que estão mais perto do limite. Assim, o aluno vê logo quais matérias pedem mais atenção.

O projeto foi feito como trabalho final do [CS50x](https://cs50.harvard.edu/x/), com Flask e PostgreSQL no backend e Jinja e Bootstrap no frontend.

## Features

### Conta

- **Cadastro** com nome, email e senha. O email é validado e a senha precisa ter pelo menos 8 caracteres.
- **Login e logout**. As senhas são guardadas com hash Argon2, nunca em texto puro.
- **Troca de senha**: pede a senha atual e a confirmação da nova senha, e não aceita uma senha nova igual à atual.
- **Exclusão de conta**: pede a senha para confirmar. Ao excluir a conta, todas as matérias, presenças e feriados do usuário também são apagados.

### Matérias

- Cada matéria tem **nome**, **limite de faltas** e **período** (data de início e de fim).
- **Grade semanal**: você informa quantas aulas a matéria tem em cada dia da semana (por exemplo, 2 aulas na segunda e 1 na quarta).
- **Presença padrão**: cada matéria define o que acontece com os dias que você não marcou. Eles podem contar como presença ou como falta.
- Dá para **editar** a matéria a qualquer momento. O formulário já abre preenchido com os dados atuais.

### Marcação de presença

- A **página inicial** mostra as aulas de hoje. Cada uma tem os botões:
  - **Present**: presente em todas as aulas do dia;
  - **Partial**: escolhe quantas aulas você faltou;
  - **Missed**: faltou em todas;
  - **No class**: não houve aula nesse dia, então ele não conta.
- Uma marcação pode ser **desfeita**, e o dia volta a seguir a presença padrão da matéria.
- **Dias passados que não foram marcados** são preenchidos automaticamente com a presença padrão da matéria, então você não precisa marcar todo dia.

### Feriados e recessos

- Você cadastra feriados de um dia ou recessos com várias datas, cada um com uma descrição.
- Os feriados valem para **todas as matérias** do usuário: as aulas nesses dias são canceladas e não contam como falta.
- Não é possível cadastrar dois feriados que caiam no mesmo dia.

### Status e acompanhamento

- Cada matéria mostra quantas **faltas já foram usadas** e quantas ainda restam.
- **Status** da matéria:
  - **Safe**: abaixo de 75% do limite;
  - **Warning**: a partir de 75% do limite;
  - **At risk**: limite atingido ou ultrapassado.
- A página inicial lista todas as matérias, começando pelas que têm **menos faltas sobrando**.
- A página de detalhes da matéria mostra:
  - uma barra de progresso das faltas;
  - a grade semanal;
  - as aulas canceladas por feriados;
  - o histórico de presenças, da mais recente para a mais antiga.

## How attendance is calculated

 TODO

## Tech stack

### Backend

- **[Python 3](https://www.python.org/)**: linguagem do projeto.
- **[Flask](https://flask.palletsprojects.com/)**: framework web. Cuida das rotas, da sessão do usuário e das mensagens de aviso (`flash`). As rotas de matérias e de feriados ficam em Blueprints separados.
- **[python-dotenv](https://pypi.org/project/python-dotenv/)**: carrega o `DATABASE_URL` e a `SECRET_KEY` do arquivo `.env`, para que senhas e chaves não fiquem no código.

### Banco de dados

- **[PostgreSQL](https://www.postgresql.org/)**: guarda usuários, matérias, grade semanal, presenças e feriados. As regras de integridade ficam no próprio banco:
  - `CHECK`, por exemplo, para impedir que o número de faltas passe o número de aulas;
  - `UNIQUE`, para que cada matéria tenha uma só marcação por dia;
  - `ON DELETE CASCADE`, para que excluir a conta apague todos os dados do usuário.
- **[psycopg 3](https://github.com/psycopg/psycopg/)**: conecta o Python ao PostgreSQL. As consultas são escritas em SQL puro, sem ORM, e sempre com parâmetros, o que evita SQL injection.

### Segurança

- **[argon2-cffi](https://argon2-cffi.readthedocs.io/)**: gera o hash das senhas com Argon2id, o algoritmo recomendado atualmente para guardar senhas.
- **[Flask-WTF](https://flask-wtf.readthedocs.io/)**: adiciona um token CSRF a todos os formulários. Assim, outro site não consegue enviar requisições em nome do usuário logado.
- **[email-validator](https://pypi.org/project/email-validator/)**: confere se o email do cadastro tem um formato válido.

### Frontend

- **[Jinja](https://jinja.palletsprojects.com/)**: templates HTML gerados no servidor, com um layout base que as outras páginas herdam.
- **[Bootstrap 5](https://getbootstrap.com/)**: layout responsivo, componentes (barra de navegação, botões, dropdowns, barras de progresso) e as cores de status.
- **[Bootstrap Icons](https://icons.getbootstrap.com/)**: ícones da interface.
- **CSS e JavaScript próprios**: estilos personalizados e pequenos scripts, sem nenhum framework de JavaScript.

### Testes

- **[pytest](https://docs.pytest.org/)**: testes do cálculo de presença (`attendance.py`), do hash de senhas (`security.py`) e das funções do banco (`models.py`). Os testes do banco usam fixtures que criam um usuário e uma matéria de teste antes de cada teste e apagam tudo depois, então um teste não depende do outro.

## Project structure / Files

TODO

## Design decisions

TODO

## How to run

TODO

### Pré-requisitos

- [Python 3](https://www.python.org/downloads/) (desenvolvido com Python 3.14)
- [PostgreSQL](https://www.postgresql.org/download/) (desenvolvido com PostgreSQL 18), instalado e rodando
- [Git](https://git-scm.com/downloads)

### 1. Clonar o repositório

```bash
git clone https://github.com/EnzoHashinokutiXavier/Eutava.git
cd Eutava
```

### 2. Criar e ativar o ambiente virtual

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Deve aparecer `(venv)` no começo da linha do terminal.

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Criar o banco de dados

Conecte ao PostgreSQL com o usuário definido na instalação (geralmente `postgres`) e crie um banco vazio:

```bash
psql -U postgres -c "CREATE DATABASE eutava;"
```

### 5. Criar o arquivo `.env`

Copie o `.env.example` para um arquivo novo chamado `.env` na **raiz do projeto** (mesma pasta deste README):

Windows:

```bash
copy .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

Depois abra o `.env` e preencha os dois valores:

```env
DATABASE_URL=postgresql://postgres:SUA_SENHA_DO_POSTGRES@localhost:5432/eutava
SECRET_KEY=cole_uma_string_aleatoria_aqui
```

- `DATABASE_URL`: troque `SUA_SENHA_DO_POSTGRES` pela sua senha do PostgreSQL (e `postgres` pelo seu usuário, se for outro).
- `SECRET_KEY`: qualquer string longa e aleatória. Dá para gerar uma com:

  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

### 6. Criar as tabelas

Todos os comandos `flask` devem ser rodados de dentro da pasta `backend`:

```bash
cd backend
flask --app app.main init-db
```

Deve aparecer `Banco initialized with success`. Pode rodar de novo sem problema: só cria as tabelas que ainda não existem.

### 7. Iniciar o servidor

```bash
flask --app app.main run
```

Abra **http://127.0.0.1:5000** no navegador.

### 8. Testar o site

1. Clique em **Register** e crie uma conta (qualquer email em formato válido, senha com pelo menos 8 caracteres).
2. Faça login.
3. Crie uma matéria: defina o limite de faltas, as datas de início e fim e quantas aulas ela tem em cada dia da semana.
4. Na página inicial, marque as aulas de hoje como presença / falta / sem aula e veja o status da matéria mudar.
5. Adicione um feriado ou recesso e confira que esses dias deixam de contar.

Para parar o servidor, aperte `Ctrl + C`. Nas próximas vezes basta ativar o venv (passo 2), entrar em `backend` e rodar o passo 7.

### Problemas comuns

| Erro | Causa / solução |
| --- | --- |
| `Could not import 'app.main'` | Você não está dentro da pasta `backend`. Rode `cd backend`. |
| `connection refused` / `Connection timed out` | O serviço do PostgreSQL não está rodando, ou a porta não é `5432`. |
| `password authentication failed` | Usuário ou senha errados no `DATABASE_URL`. |
| `'flask' não é reconhecido` | O ambiente virtual não está ativo. Veja o passo 2. |

## Testing 

TODO

## AI usage

Usamos IA como apoio para tirar dúvidas, revisar o código e procurar falhas. Os trechos em que ela ajudou estão marcados no código com o comentário `uso de ia`.

### Segurança

- **CSRF** ([main.py](backend/app/main.py)): a IA apontou que um site malicioso poderia fazer requisições em nome do usuário logado (por exemplo, apagar matérias ou marcar faltas). Por isso usamos o token CSRF do Flask-WTF em todos os formulários.
- **Handlers globais de erro** ([main.py](backend/app/main.py)): a IA recomendou tratar em um só lugar os erros de conexão com o banco e os erros de CSRF, para o usuário ver uma mensagem clara e o sistema não mostrar detalhes técnicos.
- **Validação de email** ([main.py](backend/app/main.py)): a IA sugeriu validar o email no cadastro para recusar endereços inválidos.

### Revisão de lógica e correção de bugs

- **Ordem das validações no cadastro** ([main.py](backend/app/main.py)): a IA percebeu que checar os campos vazios depois de validar o email mostraria a mensagem de erro errada.
- **Usuário que não existe mais** ([main.py](backend/app/main.py)): a IA apontou um possível problema quando a sessão aponta para um usuário que já foi apagado.
- **Funções do banco** ([models.py](backend/app/models.py)): a IA indicou funções que ainda faltavam, encontrou falhas de lógica e sugeriu melhorias.
- **Rotas** ([routes.py](backend/app/routes.py)): a IA encontrou uma inconsistência, que já foi corrigida.

### Organização do código

- **Decorator `login_required`** ([decorators.py](backend/app/decorators.py)): no começo, cada rota tinha sua própria checagem de login, o que repetia código. A IA recomendou um decorator, e assim essa lógica ficou em um só lugar. Ela também indicou o `@wraps`, que mantém o nome original das rotas e evita conflitos no `url_for`.
- **Datas do formulário** ([routes.py](backend/app/routes.py)): a IA indicou o `date.fromisoformat` para converter as datas do formulário em objetos `date`.
- **Montagem de um dicionário** ([routes.py](backend/app/routes.py)): um trecho foi adaptado de um exemplo dado pela IA.

### Frontend

- **Formulário de edição de matéria** ([edit_course.html](frontend/templates/edit_course.html)): perguntamos à IA como fazer os dias com aula já virem preenchidos ao abrir a página.
- **Detalhes da matéria** ([course_detail.html](frontend/templates/course_detail.html)): a IA ajudou a planejar como ordenar o resultado exibido.

### Testes

- **Estrutura dos testes** ([pytest.ini](backend/pytest.ini)): a IA ajudou a seguir as boas práticas na organização dos testes.
- **Testes unitários** ([test_models.py](backend/tests/test_models.py), [test_attendance.py](backend/tests/test_attendance.py)): usamos a IA para aprender a escrever testes unitários e organizá-los melhor.
- **Dados de teste compartilhados** ([test_models.py](backend/tests/test_models.py)): ao investigar um teste que falhava, a IA recomendou definir os dados no início do arquivo. Assim, todos os testes usam os mesmos valores, é fácil mudá-los e um teste não depende de outro.

## References

flask + jinja:   
https://www.youtube.com/watch?v=gnkkLc8IAMI  
flask sessions:  
https://www.youtube.com/watch?v=iIhAfX4iek0&list=PLzMcBGfZo4-n4vJJybUVV3Un_NFS5EOgX&index=5  
responsive navbar bootstrap5:  
https://www.youtube.com/watch?v=h5apE3E72wY&list=PLj0z0WBaTiH7jOjO7C0w2lSeuuisoiSR9  
pytest:  
https://www.youtube.com/watch?v=EgpLj86ZHFQ  
email validator:  
https://pypi.org/project/email-validator/  
markdown:  
https://docs.github.com/pt/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax