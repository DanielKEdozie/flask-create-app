"""Tests for flask-create-app scaffolding."""
import os
import shutil
import tempfile
from pathlib import Path
from click.testing import CliRunner
from flask_create_app.cli import main
from flask_create_app.generator import scaffold_project


def test_scaffold_simple_app():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = scaffold_project("simple_app", target_path=tmpdir, factory=False, init_git=False)
        assert (out_dir / "app.py").exists()
        assert (out_dir / "config.py").exists()
        assert (out_dir / "requirements.txt").exists()
        assert (out_dir / ".env").exists()

        # Verify syntax compiles cleanly:
        with open(out_dir / "app.py", "r", encoding="utf-8") as f:
            compile(f.read(), "app.py", "exec")
        with open(out_dir / "config.py", "r", encoding="utf-8") as f:
            compile(f.read(), "config.py", "exec")


def test_scaffold_factory_app():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = scaffold_project("factory_app", target_path=tmpdir, factory=True, init_git=False)
        assert (out_dir / "wsgi.py").exists()
        assert (out_dir / "app" / "__init__.py").exists()
        assert (out_dir / "app" / "config.py").exists()
        assert (out_dir / "app" / "extensions.py").exists()
        assert (out_dir / "app" / "models" / "user.py").exists()
        assert (out_dir / "app" / "api" / "routes.py").exists()
        assert (out_dir / "app" / "web" / "routes.py").exists()
        assert (out_dir / "app" / "templates" / "index.html").exists()

        # Verify syntax compiles cleanly on all generated python files:
        for py_file in out_dir.rglob("*.py"):
            with open(py_file, "r", encoding="utf-8") as f:
                compile(f.read(), str(py_file), "exec")


def test_cli_execution():
    runner = CliRunner()
    with runner.isolated_filesystem():
        res = runner.invoke(main, ["test_cli_project", "--factory", "--no-git"])
        assert res.exit_code == 0
        assert "Project created successfully" in res.output
        assert Path("test_cli_project/wsgi.py").exists()
        assert Path("test_cli_project/app/__init__.py").exists()