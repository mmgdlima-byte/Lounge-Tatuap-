# Lounge Tatuapé — Controle de Entregas

MVP acadêmico para cadastro, consulta e acompanhamento de pedidos, com identificação de entregas concluídas, atrasadas e extraviadas.

## Funcionalidades
- Login demonstrativo.
- Cadastro de pedidos com região, transportadora, código de rastreamento e data.
- Consulta e filtro de pedidos.
- Atualização de status e registro de ocorrências.
- Interface responsiva em preto, branco e azul, inspirada no protótipo visual.

## Tecnologias
- Python, Flask e Flask-SQLAlchemy
- SQLite para execução local rápida
- PostgreSQL por meio da variável `DATABASE_URL`
- HTML, CSS e JavaScript

## Executar localmente
1. Instale Python 3.10 ou superior.
2. Crie e ative um ambiente virtual:
   - Windows: `py -m venv .venv`
   - PowerShell: `.\.venv\Scripts\Activate.ps1`
3. Instale as dependências: `pip install -r requirements.txt`
4. Inicie: `python app.py`
5. Abra `http://127.0.0.1:5000`.

## Acesso demonstrativo
- Usuário: `admin`
- Senha: `lounge123`

As credenciais são apenas para demonstração acadêmica. Não utilize esse acesso em produção. Antes de publicar um sistema real, configure `SECRET_KEY`, `DEMO_USER`, `DEMO_PASSWORD` e `DATABASE_URL` por variáveis de ambiente, implemente controles adicionais de segurança e revise o tratamento de sessões.

## Banco de dados
Por padrão, o projeto cria um banco SQLite local e inclui pedidos fictícios na primeira execução. Para usar PostgreSQL, configure `DATABASE_URL` com a URL do banco, por exemplo:

`postgresql+psycopg://usuario:senha@localhost:5432/lounge_tatuape`

O arquivo `database/schema.sql` contém o esquema SQL de referência.

## Escopo do MVP
A integração automática com transportadoras reais não faz parte desta primeira versão. Os status e ocorrências são administrados manualmente para fins de prototipagem e validação.
## Histórico de funcionalidades

- Cadastro de pedidos com nome e volume.
- Consulta e acompanhamento de pedidos.
- Registro de ocorrências.
- Atualização de status das entregas.
## Segurança e armazenamento

- Banco de dados SQLite para armazenamento local.
- Arquivos temporários e banco de dados local ignorados pelo Git.