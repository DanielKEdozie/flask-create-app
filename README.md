# flask-create-app

Instant, production-ready scaffolding CLI for modern Flask applications.

Creates fully-configured projects pre-wired with **`flask-user-auth`** (dual token/session auth), **`flask-api-builder`** (RESTful CRUD & Marshmallow schemas), and **`sqlalchemy-utility`** (auto-slugs, timestamps, BaseModel).

---

## Installation

Install globally or in your environment:

```bash
pip install git+https://github.com/DanielKEdozie/flask-create-app.git
```

---

## Usage

### 1. Scaffold in Current Directory (No Subfolder)

If you have already created or opened your project folder (e.g. `mkdir my-app && cd my-app`), you do **not** need to declare a project name:

```bash
# Using '.'
flask-create-app . --factory

# Or using '--here' flag
flask-create-app --here --factory
```

- Infers the project name automatically from the current directory name.
- Generates the structure directly in the current directory without creating nested folders.
- Preserves existing `.env` or `README.md` files if already present.

---

### 2. Scaffold in a New Subfolder

```bash
flask-create-app my_enterprise_app --factory
```

Creates `./my_enterprise_app/` with the scalable Application Factory pattern (`create_app()`):
```text
my_enterprise_app/
├── app/
│   ├── __init__.py        # create_app(config_class=...)
│   ├── config.py          # Config, DevelopmentConfig, ProductionConfig
│   ├── extensions.py      # db, user_auth, ma, api_builder_ext
│   ├── models/
│   │   ├── __init__.py    # db, BaseModel, User, UserAuth
│   │   └── user.py        # User & UserAuth model declarations
│   ├── api/
│   │   ├── __init__.py    # Blueprint registration
│   │   └── routes.py      # Health & API endpoints
│   ├── web/
│   │   ├── __init__.py    # Blueprint registration
│   │   └── routes.py      # Web / Jinja views
│   ├── templates/
│   │   └── index.html     # Welcome template
│   └── static/
│       ├── css/style.css
│       └── js/main.js
├── wsgi.py                # WSGI entrypoint (app = create_app())
├── requirements.txt
├── .env / .env.example
├── .gitignore
└── README.md
```

---

### 3. Simple Modular Layout (Prototypes & Microservices)

```bash
flask-create-app my_microservice
```

Generates:
```text
my_microservice/
├── app.py             # Single-file modular app with models & routes
├── config.py          # App & FUA_* configurations
├── requirements.txt   # Pinned dependencies
├── .env / .env.example
├── .gitignore
└── README.md
```

---

## Command Options

```text
Usage: flask-create-app [OPTIONS] [PROJECT_NAME]

Arguments:
  [PROJECT_NAME]              Name of the project to create, or '.' for current directory.

Options:
  --factory                   Generate modular Application Factory structure.
  -c, --here                  Generate structure directly in current directory.
  --db [sqlite|postgres|mysql]
                              Target database dialect (default: sqlite).
  --auth / --no-auth          Include flask-user-auth dual auth (default: --auth).
  --api / --no-api            Include flask-api-builder CRUD (default: --api).
  --utility / --no-utility    Include sqlalchemy-utility auto-slugs (default: --utility).
  --git / --no-git            Initialize a Git repository (default: --git).
  -h, --help                  Show this message and exit.
```

---

## License

MIT