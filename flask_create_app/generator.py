"""Template generator engine for flask-create-app."""
import os
import subprocess
from pathlib import Path
from typing import Dict, Optional


def write_file(path: Path, content: str) -> None:
    """Create directory if needed and write file without BOM."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")


def generate_requirements(
    include_auth: bool = True,
    include_api: bool = True,
    include_utility: bool = True,
    db: str = "sqlite",
) -> str:
    """Build requirements.txt contents."""
    reqs = [
        "flask>=3.0.0",
        "flask-sqlalchemy>=3.1.0",
        "sqlalchemy>=2.0.0",
        "python-dotenv>=1.0.0",
    ]
    if db == "postgres":
        reqs.append("psycopg2-binary>=2.9.9")
    elif db == "mysql":
        reqs.append("pymysql>=1.1.0")

    if include_auth:
        reqs.append("flask-user-auth @ git+https://github.com/DanielKEdozie/flask-user-auth.git@v1.2.0")
        reqs.append("flask-login>=0.6.3")
        reqs.append("pyjwt>=2.8.0")
    if include_api:
        reqs.append("flask-api-builder @ git+https://github.com/DanielKEdozie/flask-api-builder.git@v2.0.0")
        reqs.append("flask-marshmallow>=1.2.0")
        reqs.append("marshmallow-sqlalchemy>=1.0.0")
    if include_utility:
        reqs.append("sqlalchemy-utility @ git+https://github.com/DanielKEdozie/sqlalchemy-utility.git@v1.0.0")
        reqs.append("python-slugify>=8.0.0")

    return "\n".join(reqs)


def generate_env(project_name: str, db: str = "sqlite") -> str:
    """Build .env / .env.example contents."""
    db_uri = {
        "sqlite": f"sqlite:///{project_name}.db",
        "postgres": f"postgresql://postgres:postgres@localhost:5432/{project_name}",
        "mysql": f"mysql+pymysql://root:root@localhost:3306/{project_name}",
    }.get(db, f"sqlite:///{project_name}.db")

    return f"""
FLASK_APP={'wsgi.py' if True else 'app.py'}
FLASK_DEBUG=1
SECRET_KEY=dev-secret-change-in-production-{project_name}
SQLALCHEMY_DATABASE_URI={db_uri}
SQLALCHEMY_TRACK_MODIFICATIONS=False
FUA_JWT_SECRET_KEY=dev-jwt-secret-{project_name}
FUA_JWT_ACCESS_TOKEN_EXPIRES=3600
FUA_COOKIE_SECURE=False
FUA_COOKIE_SAMESITE=Lax
"""


def generate_gitignore() -> str:
    """Standard Python and Flask gitignore."""
    return """
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.env
.venv/
venv/
ENV/
*.db
*.sqlite3
instance/
.pytest_cache/
.coverage
htmlcov/
"""


def generate_simple_app(target_dir: Path, project_name: str, db: str, include_auth: bool, include_api: bool, include_utility: bool) -> None:
    """Generate a single-file modular Flask app."""
    # 1. config.py
    config_code = """
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # flask-user-auth configurations:
    FUA_JWT_SECRET_KEY = os.environ.get("FUA_JWT_SECRET_KEY", SECRET_KEY)
    FUA_JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    FUA_COOKIE_SECURE = os.environ.get("FUA_COOKIE_SECURE", "False").lower() in ("true", "1")
    FUA_COOKIE_SAMESITE = os.environ.get("FUA_COOKIE_SAMESITE", "Lax")
    FUA_LOGIN_VIEW = "auth.session_login"
"""
    write_file(target_dir / "config.py", config_code)

    # 2. app.py
    app_code = """
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object("config.Config")

db = SQLAlchemy(app)
"""

    if include_utility:
        app_code += """
from sqlalchemy_utility import BaseModel, SlugMixin, TimestampMixin, init_model_events
init_model_events()
"""

    if include_auth:
        app_code += """
from flask_user_auth import FlaskUserAuth, UserMixin, UserAuthMixin, current_user, login_required, session_required, token_required

class User(db.Model, UserMixin):
    __tablename__ = "users"
    name = db.Column(db.String(255), default="")
    role = db.Column(db.String(50), default="user")

class UserAuth(db.Model, UserAuthMixin):
    __tablename__ = "user_auth"

user_auth = FlaskUserAuth()
user_auth.init_app(app, db=db, user_model=User, auth_model=UserAuth)
"""

    if include_api:
        app_code += """
from flask_marshmallow import Marshmallow
from flask_api_builder import FlaskApiBuilder, ApiBuilder, SchemaBuilder

ma = Marshmallow(app)
api_ext = FlaskApiBuilder()
api_ext.init_app(app, db=db, ma=ma)
"""

    app_code += """
@app.route("/")
def index():
    return jsonify({
        "project": \"""" + project_name + """\",
        "status": "online",
        "message": "Welcome to your new Flask application!"
    })

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
"""
    write_file(target_dir / "app.py", app_code)


def generate_factory_app(target_dir: Path, project_name: str, db: str, include_auth: bool, include_api: bool, include_utility: bool) -> None:
    """Generate enterprise scalable Application Factory Flask project."""
    app_pkg = target_dir / "app"

    # 1. app/config.py
    config_code = """
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # flask-user-auth configurations:
    FUA_JWT_SECRET_KEY = os.environ.get("FUA_JWT_SECRET_KEY", SECRET_KEY)
    FUA_JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    FUA_JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    FUA_COOKIE_SECURE = os.environ.get("FUA_COOKIE_SECURE", "False").lower() in ("true", "1")
    FUA_COOKIE_SAMESITE = os.environ.get("FUA_COOKIE_SAMESITE", "Lax")
    FUA_LOGIN_VIEW = "auth.session_login"
    FUA_AUTH_PREFIX = "/auth"
    FUA_USER_PREFIX = "/users"

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    FUA_COOKIE_SECURE = True
"""
    write_file(app_pkg / "config.py", config_code)

    # 2. app/extensions.py
    ext_code = """
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
"""
    if include_auth:
        ext_code += """
from flask_user_auth import FlaskUserAuth
user_auth = FlaskUserAuth()
"""
    if include_api:
        ext_code += """
from flask_marshmallow import Marshmallow
from flask_api_builder import FlaskApiBuilder

ma = Marshmallow()
api_builder_ext = FlaskApiBuilder()
"""
    write_file(app_pkg / "extensions.py", ext_code)

    # 3. app/models/
    models_init = """
from app.extensions import db
"""
    if include_utility:
        models_init += """
from sqlalchemy_utility import BaseModel, SlugMixin, TimestampMixin, init_model_events
init_model_events()
"""
    if include_auth:
        models_init += """
from .user import User, UserAuth
__all__ = ["db", "User", "UserAuth"]
"""
    else:
        models_init += """
__all__ = ["db"]
"""
    write_file(app_pkg / "models" / "__init__.py", models_init)

    if include_auth:
        user_model_code = """
from app.extensions import db
from flask_user_auth import UserMixin, UserAuthMixin
"""
        if include_utility:
            user_model_code += """
from sqlalchemy_utility import BaseModel

class User(db.Model, BaseModel, UserMixin):
    __tablename__ = "users"
    name = db.Column(db.String(255), default="")
    role = db.Column(db.String(50), default="user")

class UserAuth(db.Model, BaseModel, UserAuthMixin):
    __tablename__ = "user_auth"
"""
        else:
            user_model_code += """
class User(db.Model, UserMixin):
    __tablename__ = "users"
    name = db.Column(db.String(255), default="")
    role = db.Column(db.String(50), default="user")

class UserAuth(db.Model, UserAuthMixin):
    __tablename__ = "user_auth"
"""
        write_file(app_pkg / "models" / "user.py", user_model_code)

    # 4. app/api/
    api_routes = """
from flask import Blueprint, jsonify

api_bp = Blueprint("api", __name__)

@api_bp.route("/health")
def health():
    return jsonify({"status": "healthy"})
"""
    write_file(app_pkg / "api" / "__init__.py", "from .routes import api_bp\n__all__ = ['api_bp']")
    write_file(app_pkg / "api" / "routes.py", api_routes)

    # 5. app/web/
    web_routes = """
from flask import Blueprint, render_template

web_bp = Blueprint("web", __name__)

@web_bp.route("/")
def index():
    return render_template("index.html")
"""
    write_file(app_pkg / "web" / "__init__.py", "from .routes import web_bp\n__all__ = ['web_bp']")
    write_file(app_pkg / "web" / "routes.py", web_routes)

    # Templates & Static
    index_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
    <link rel="stylesheet" href="{{{{ url_for('static', filename='css/style.css') }}}}">
</head>
<body>
    <main class="container">
        <h1>Welcome to {project_name}!</h1>
        <p>Your enterprise Flask Application Factory is ready to rock.</p>
        <div class="card">
            <h3>Quick Links</h3>
            <ul>
                <li><a href="/api/health">API Healthcheck (/api/health)</a></li>
                <li><a href="/auth/me">Auth Profile (/auth/me)</a></li>
                <li><a href="/users">User Management (/users)</a></li>
            </ul>
        </div>
    </main>
</body>
</html>
"""
    style_css = """
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 2rem; }
.container { max-width: 600px; margin: 4rem auto; }
.card { background: #1e293b; padding: 1.5rem; border-radius: 8px; margin-top: 1.5rem; }
a { color: #38bdf8; text-decoration: none; }
a:hover { text-decoration: underline; }
"""
    write_file(app_pkg / "templates" / "index.html", index_html)
    write_file(app_pkg / "static" / "css" / "style.css", style_css)

    # 6. app/__init__.py (Application Factory)
    app_init_code = """
from flask import Flask
from .config import Config, DevelopmentConfig
from .extensions import db
"""
    if include_auth:
        app_init_code += "from .extensions import user_auth\nfrom .models.user import User, UserAuth\n"
    if include_api:
        app_init_code += "from .extensions import ma, api_builder_ext\n"

    app_init_code += """
def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions:
    db.init_app(app)
"""
    if include_auth:
        app_init_code += "    user_auth.init_app(app, db=db, user_model=User, auth_model=UserAuth)\n"
    if include_api:
        app_init_code += "    ma.init_app(app)\n    api_builder_ext.init_app(app, db=db, ma=ma)\n"

    app_init_code += """
    # Register blueprints:
    from .api import api_bp
    from .web import web_bp
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(web_bp)

    with app.app_context():
        db.create_all()

    return app
"""
    write_file(app_pkg / "__init__.py", app_init_code)

    # 7. wsgi.py
    wsgi_code = """
import os
from dotenv import load_dotenv
from app import create_app

load_dotenv()

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
"""
    write_file(target_dir / "wsgi.py", wsgi_code)


def scaffold_project(
    project_name: str,
    target_path: Optional[str] = None,
    factory: bool = False,
    db: str = "sqlite",
    include_auth: bool = True,
    include_api: bool = True,
    include_utility: bool = True,
    init_git: bool = True,
) -> Path:
    """Scaffold a complete Flask project."""
    base_dir = Path(target_path or ".") / project_name
    base_dir.mkdir(parents=True, exist_ok=True)

    # Generate Common Files:
    write_file(base_dir / "requirements.txt", generate_requirements(include_auth, include_api, include_utility, db))
    write_file(base_dir / ".env.example", generate_env(project_name, db))
    write_file(base_dir / ".env", generate_env(project_name, db))
    write_file(base_dir / ".gitignore", generate_gitignore())

    readme_content = f"""# {project_name}

Generated with `flask-create-app` ({'Application Factory' if factory else 'Simple modular'} layout).

## Quick Start

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   flask run
   ```
"""
    write_file(base_dir / "README.md", readme_content)

    if factory:
        generate_factory_app(base_dir, project_name, db, include_auth, include_api, include_utility)
    else:
        generate_simple_app(base_dir, project_name, db, include_auth, include_api, include_utility)

    if init_git:
        try:
            subprocess.run(["git", "init"], cwd=base_dir, capture_output=True, check=False)
        except Exception:
            pass

    return base_dir