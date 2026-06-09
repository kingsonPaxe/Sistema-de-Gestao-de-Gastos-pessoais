# 💰 Sistema de Gestão de Gastos Pessoais

Aplicação web completa para controle de finanças pessoais, desenvolvida como projeto acadêmico com Python/Flask, PostgreSQL e SQLAlchemy.

---

## 🚀 Tecnologias

| Camada | Tecnologia |
|---|---|
| Back-end | Python 3.11+, Flask 3.0 |
| ORM | SQLAlchemy 2.0 |
| Banco de dados | PostgreSQL |
| Autenticação | Flask-Login + Werkzeug |
| Front-end | HTML5, CSS3, Bootstrap 5, JavaScript ES6 |
| Gráficos | Chart.js 4 |
| Relatórios PDF | ReportLab 4 |

---

## 📁 Estrutura do Projeto

```
personal-finance-manager/
├── app.py                  # Factory Flask + inicialização
├── config.py               # Configurações (dev/prod)
├── .env                    # Variáveis de ambiente
├── requirements.txt
├── models/
│   ├── user.py             # Modelo de usuário + Flask-Login
│   ├── category.py         # Categorias (padrão + personalizadas)
│   ├── income.py           # Receitas
│   └── expense.py          # Despesas
├── routes/
│   ├── auth.py             # Login / Cadastro / Logout
│   ├── dashboard.py        # Dashboard + API de gráficos
│   ├── income.py           # CRUD de receitas
│   ├── expense.py          # CRUD de despesas
│   ├── reports.py          # Exportação PDF
│   └── categories.py       # Perfil + categorias
├── services/
│   └── report_service.py   # Geração de PDF com ReportLab
├── templates/
│   ├── base.html           # Layout base com sidebar
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── incomes.html
│   ├── expenses.html
│   └── profile.html
└── static/
    ├── css/style.css
    └── js/dashboard.js
```

---

## ⚙️ Instalação no Fedora Linux

### 1. Instalar dependências do sistema

```bash
sudo dnf install python3 python3-pip python3-venv postgresql postgresql-server postgresql-contrib -y
```

### 2. Inicializar e iniciar o PostgreSQL

```bash
sudo postgresql-setup --initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### 3. Criar o banco de dados e usuário

```bash
sudo -u postgres psql <<EOF
CREATE USER finance_user WITH PASSWORD 'finance_pass';
CREATE DATABASE personal_finance_db OWNER finance_user;
GRANT ALL PRIVILEGES ON DATABASE personal_finance_db TO finance_user;
\q
EOF
```

### 4. Configurar autenticação local (se necessário)

Edite `/var/lib/pgsql/data/pg_hba.conf` e altere as linhas `ident` para `md5`:

```
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

Reinicie o PostgreSQL:

```bash
sudo systemctl restart postgresql
```

### 5. Clonar/acessar o projeto

```bash
cd personal-finance-manager
```

### 6. Criar e ativar o ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 7. Instalar dependências Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 8. Configurar o arquivo `.env`

O arquivo `.env` já existe com as configurações padrão. Ajuste se necessário:

```env
SECRET_KEY=sua-chave-secreta-muito-segura-aqui
DATABASE_URL=postgresql://finance_user:finance_pass@localhost/personal_finance_db
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
```

---

## ▶️ Executar a aplicação

```bash
source venv/bin/activate   # ative o venv se não estiver ativo
flask run
```

Acesse: **http://127.0.0.1:5000**

> As tabelas do banco são criadas automaticamente no primeiro acesso. As categorias padrão também são inseridas automaticamente.

---

## 🧩 Funcionalidades

| Módulo | Funcionalidades |
|---|---|
| **Autenticação** | Cadastro, Login, Logout, sessão segura |
| **Dashboard** | Saldo, total receitas/despesas, contagem de transações, gráficos |
| **Receitas** | Adicionar, editar, excluir, listar, filtrar, pesquisar |
| **Despesas** | Adicionar, editar, excluir, listar, filtrar, pesquisar |
| **Categorias** | 8 categorias padrão + criação e exclusão de categorias personalizadas |
| **Gráficos** | Pizza (despesas por categoria) e Barras (receitas vs despesas por mês) |
| **Relatório PDF** | Exportação com resumo, tabelas de receitas e despesas, filtro por período |
| **Perfil** | Alterar nome, email e senha |

---

## 🗄️ Banco de Dados

```sql
users        → id, name, email, password_hash, created_at
categories   → id, name, is_default, user_id
incomes      → id, user_id, category_id, title, amount, description, date, created_at
expenses     → id, user_id, category_id, title, amount, description, date, created_at
```

---

## 🔐 Segurança

- Senhas com hash via **Werkzeug** (`pbkdf2:sha256`)
- Proteção de rotas via **Flask-Login** (`@login_required`)
- Queries via **SQLAlchemy ORM** (previne SQL Injection)
- Validação de formulários no servidor paxe
- Isolamento de dados por usuário em todas as queries

---

## 🏗️ Arquitetura

A aplicação usa o padrão **Application Factory** com **Blueprints**:

- `create_app()` inicializa extensões e registra blueprints
- Cada módulo (`auth`, `dashboard`, `income`, `expense`, `reports`, `categories`) é um blueprint independente
- Os models usam **SQLAlchemy declarativo** com relationships
- O serviço de PDF é isolado em `services/report_service.py`

---

## 📄 Licença

Projeto acadêmico — uso livre para fins educacionais.
