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

O **Eutava** é um site feito para que estudantes tenham controle sobre suas quantias de faltas em seu ambiente academico.   

Na faculdade, cada matéria tem um limite de faltas, e passar desse limite reprova o aluno mesmo com nota boa. Acompanhar isso de cabeça ou numa planilha é difícil e cansativo.
No Eutava, o usuário cadastra cada matéria com o limite de faltas, o período e a grade semanal. A partir daí, o site calcula quantas aulas já aconteceram, quantas faltas foram usadas e quantas ainda restam. Os feriados são descontados automaticamente, e os dias que o usuário não marcou seguem a presença padrão da matéria, então não é preciso registrar todo dia.  
O nome Eutava se origina de "eu tava", jeito informal de dizer "eu estava (presente)" no português brasileiro.  

A página inicial mostra as aulas de hoje permitindo o usuário marcar a presença com um clique, e a lista de matérias exibe cada uma com um status (Safe, Warning ou At risk), começando pelas que estão mais perto do limite. Assim, o aluno vê com prioridade quais matérias pedem mais atenção.

O projeto foi realizado como trabalho final do CS50x (Harvard) dos estudantes Enzo Hashinokuti e Augusto Correa. Servindo como uma oportunidade de estudo e experimentação de novas tecnologias, além de servir como um projeto para exibir em portifólio pelo trabalho em equipe realizado durante todo o desenvolvimento.

## Features

### Conta

- **Cadastro**: nome, email e senha. Com validação de email da biblioteca email-validator e verificação de tamanho da senha.
- **Login e logout**: as senhas são guardadas com hash Argon2 para não ficar em texto puro no banco de dados.
- **Troca de senha**: pede a senha atual e a confirmação da nova senha, não aceita uma senha nova igual à atual.
- **Exclusão de conta**: pede a senha para confirmar. Ao excluir a conta, todas as matérias, presenças e feriados do usuário também são apagados automaticamente do banco de dados pelo cascade.

### Matérias

- **Informações**: cada matéria tem nome, limite de faltas e período marcado por data de início e de fim.
- **Grade semanal**: usuário informa quantas aulas a matéria tem para cada dia da semana.
- **Editar**: tem como editar as informações da matéria com um formulário que já abre preenchido com os dados atuais.

### Marcação de presença

- **Página inicial**: mostra as aulas do dia. Cada matéria tem as opções:
  - **Present**: presente em todas as aulas;
  - **Partial**: escolhe quantas aulas faltou;
  - **Missed**: faltou em todas;
  - **No class**: não houve aula, o dia não conta.
- **Desfazer**: tirar a marcação do dia e volta a seguir a presença padrão da matéria.
- **Dias não marcados**: preenchidos automaticamente com a presença padrão da matéria.

### Feriados e recessos

- **Data**: seleciona os dias que serão afetados
- **Descrição**: texto para lembrar depois o motivo de nao ter aula no dia.
- **Matérias**: todas matérias do dia não é contam no registro de faltas.
- **Unicidade**: não é possível cadastrar dois feriados que caiam no mesmo dia.

### Status e acompanhamento

- **Faltas**: cada matéria mostra quantas foram usadas e quantas sobram.
- **Status da matéria**: "Safe", "Warning" ou "At risk"
- **Listagem**: a página inicial lista todas as matérias em ordem crescente de sobra de dias de falta restantes.
- **Página de detalhes da matéria**:
  - barra de progresso das faltas.
  - grade semanal.
  - aulas canceladas por feriados.
  - histórico de presenças, da mais recente para a mais antiga.

## How attendance is calculated

As faltas são contadas por aula no dia: faltar num dia com 2 aulas gasta 2 faltas do limite.  
O cálculo fica em [attendance.py](backend/app/attendance.py).

### 1. Classificação de cada dia

A função `day_info` olha um dia de cada vez e decide o que ele é. As regras são testadas nesta ordem, e a primeira que se aplica vale:

| n | Situação do dia | Tipo | Faltas que conta |
| --- | --- | --- | --- |
| 1 | Fora do período da matéria | out | 0 (ignorado) |
| 2 | Cai num feriado ou recesso | holiday | 0, mesmo que o dia tenha uma marcação |
| 3 | Sem aula na grade e sem marcação | none | 0 (ignorado) |
| 4 | Marcado como sem aula | noclass | 0 |
| 5 | Marcado como presente | present | 0 |
| 6 | Marcado com faltas em todas as aulas | missed | todas as aulas do dia |
| 7 | Marcado com faltas em parte das aulas | partial | as faltas informadas |
| 8 | Sem marcação, no futuro | future | 0 |
| 9 | Sem marcação, hoje | pending | 0 até o usuário marcar |
| 10 | Sem marcação, no passado | segue a presença padrão | 0 se a padrão for presença; todas as aulas do dia se for falta |

- Se um feriado for cadastrado depois, ele cancela as aulas daquele dia mesmo que já tivessem sido marcadas.
- O dia de hoje fica `pending` e não conta como falta. A presença padrão só é aplicada quando o dia termina e continua sem marcação.
- Ao desfazer uma marcação, o registro é apagado e o dia volta para as regras 8 a 10.

### 2. Total de faltas

A função `course_stats` percorre todos os dias da matéria, da data de início à de fim, e soma as faltas dos dias do tipo present, partial e missed.   
Faltas restantes = limite − faltas usadas.

### 3. Status

| Status | Condição |
| --- | --- |
| At risk | faltas usadas ≥ limite |
| Warning | faltas usadas ≥ 75% do limite |
| Safe | abaixo de 75% do limite |

Os 75% ficam na constante `WARN_AT` em [routes.py](backend/app/routes.py).

## Tech stack

### Backend

- **[Python 3](https://www.python.org/)**: linguagem principal do funcionamento do projeto.
- **[Flask](https://flask.palletsprojects.com/)**: framework web escolhida para servir de base do funcionamento do site, cuidando das rotas, da sessão do usuário e das mensagens de aviso (`flash`).
- **[python-dotenv](https://pypi.org/project/python-dotenv/)**: carrega o `DATABASE_URL` e a `SECRET_KEY` do arquivo `.env`, para que senhas e chaves não fiquem no código. Esolhido como solução do problema de programar em equipe com um repositório público no github.

### Banco de dados

- **[PostgreSQL](https://www.postgresql.org/)**: guarda usuários, matérias, grade semanal, presenças e feriados. As regras de integridade ficam no próprio banco com as funções SQL:
  - `CHECK` para impedir que o número de faltas passe o número de aulas.
  - `UNIQUE`para que cada matéria tenha uma só marcação por dia.
  - `ON DELETE CASCADE` para que ao excluir a conta apague do banco todos os dados do usuário.
- **[psycopg 3](https://github.com/psycopg/psycopg/)**: serve para conectar o Python ao Postgre. As consultas são escritas em SQL puro, com parâmetros para evitar SQL injection.

### Segurança

- **[argon2-cffi](https://argon2-cffi.readthedocs.io/)**: gera o hash das senhas com Argon2id para manter a segurança dos dados não guardando as senhas em texto puro.
- **[Flask-WTF](https://flask-wtf.readthedocs.io/)**: adiciona um token CSRF a todos os formulários. 
- **[email-validator](https://pypi.org/project/email-validator/)**: confere se o email do cadastro tem um formato válido.

### Frontend

- **[Jinja](https://jinja.palletsprojects.com/)**: templates HTML gerados no servidor, com um layout base que as outras páginas herdam.
- **[Bootstrap 5](https://getbootstrap.com/)**: layout responsivo, componentes (barra de navegação, botões, dropdowns, barras de progresso) e as cores de status.
- **[Bootstrap Icons](https://icons.getbootstrap.com/)**: ícones da interface.
- **[CSS](https://www.w3schools.com/css/)** e **[JS](https://developer.mozilla.org/pt-BR/docs/Web/JavaScript/)**: estilos personalizados e pequenos scripts, sem nenhum framework de JavaScript.

### Testes

- **[pytest](https://docs.pytest.org/)**: testes para verificar o funcionamento correto das funções em python. Os testes do banco criam usuário e matéria de teste antes de cada teste e apagam tudo depois, então um teste não depende do outro.

## Project structure / Files

TODO

## Design decisions

### Porque Python ?
Escolhemos o python por ser uma linguagem mais simples e prática para fazer projetos, outras linguagens que temos experiência seriam mais complicadas para realizar nossos objetivos
- Enzo - "Por estar já estar familiarizado com a linguagem python a um bom tempo e ter sido abordada no CS50 achei que seria ideal para este projeto "

### Python + Flask + Jinja
Escolhemos esta combinação por termos aprendido e praticado essa combinação com o curso CS50. Já utilizamos essa combinação em outros projetos após ter aprendido com o CS50 então optamos por seguir com oque aprendemos no curso.

### Bootstrap
Já havíamos utilizado anteriormente em outros projetos e optamos por usar neste para facilitar o processo sem ter que criar componentes do zero e deixar a estilização mais agradavel visualmente com componentes prontos

### Porque PostgreSQL e não SQLite3 ?
Começamos o projeto planejando usar SQLite3 por ter aprendido no CS50, mas decidimos mudar para Postgres.

- Augusto - "SQlite não é recomendado pra escrita simultanea, acho q n é uma boa pra um projeto em produção onde teria +1 cliente" 

Já nos deparamos com este mesmo problema na realização de outro projeto, resolvemos neste outro projeto com aiosqlite, mas agora optamos por utilizar o PostgreSQL que aprendemos durante a faculdade.

### Porque feriado afeta todas as matérias ?
Inicialmente planejamos cadastrar cada feriado ligado a uma matéria mas depois decidimos alterar para um feriado afetar todas matérias do usuário. Isso porque apesar da possibilidade de um recesso de meio período poder afetar uma matéria e outra não no mesmo dia, é um caso raro que para o escopo do nosso projeto não compensa manter uma tabela de relação entre matérias e feriados. Essa decisão pode ser repensada caso o projeto for á produção com clientes reais 

### Blueprints separados para holidays
Ao mudar o planejamento para feriados ligados ao usuário criamos um blueprint dedicado aos holidays por não estarem ligados a cada matéria diretamente mas ao usuário

  
Assim, outro site não consegue enviar requisições em nome do usuário logado.
## How to run

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

Deve aparecer "(venv)" no começo da linha do terminal.

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Criar o banco de dados

Conecte ao PostgreSQL com o usuário definido na instalação (geralmente postgres) e crie um banco vazio:

```bash
psql -U postgres -c "CREATE DATABASE eutava;"
```

### 5. Criar o arquivo .env

Copie o `.env.example` para um arquivo novo chamado `.env` na **raiz do projeto** (mesma pasta deste README):

Windows:

```bash
copy .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

Depois abra o .env e preencha os dois valores:

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

Deve aparecer "Banco initialized with success". Pode rodar de novo sem problema: só cria as tabelas que ainda não existem.

### 7. Iniciar o servidor

```bash
flask --app app.main run
```

Abra http://127.0.0.1:5000 no navegador.

### 8. Testar o site

1. Clique em `Register` e crie uma conta (qualquer email em formato válido, senha com pelo menos 8 caracteres).
2. Faça login.
3. Crie uma matéria: defina o limite de faltas, as datas de início e fim e quantas aulas ela tem em cada dia da semana.
4. Na página inicial, marque as aulas de hoje como presença / falta / sem aula e veja o status da matéria mudar.
5. Adicione um feriado ou recesso e confira que esses dias deixam de contar.

Para parar o servidor, aperte `Ctrl + C`. Nas próximas vezes basta ativar o venv (passo 2), entrar em `backend` e rodar o passo 7.

### Problemas comuns

problemas que tivemos durante o desenvolvimento

- Could not import 'app.main': você não está dentro da pasta backend, rode 
  ```bash
  cd backend
  ```
- Connection refused / Connection timed out: o serviço do PostgreSQL não está rodando, ou a porta não é 5432. 
- Password authentication failed: usuário ou senha errados no DATABASE_URL. 
- 'flask' não é reconhecido: o ambiente virtual não está ativo. Veja o passo 2. 

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

### Mensagens de commit

- A maioria das mensagens de commit foi gerada pelo gerador de mensagens de commit do VS Code (GitHub Copilot), a partir das alterações de cada commit. A IA só escreveu o texto da mensagem, não o conteúdo dos commits.

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