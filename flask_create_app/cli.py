"""Click CLI interface for flask-create-app."""
import click
from pathlib import Path
from .generator import scaffold_project


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("project_name", required=False)
@click.option("--factory", is_flag=True, default=False, help="Generate modular Application Factory structure.")
@click.option("--db", type=click.Choice(["sqlite", "postgres", "mysql"], case_sensitive=False), default="sqlite", help="Target database dialect.")
@click.option("--auth/--no-auth", default=True, help="Include flask-user-auth (dual token + session authentication).")
@click.option("--api/--no-api", default=True, help="Include flask-api-builder (RESTful CRUD endpoints & schemas).")
@click.option("--utility/--no-utility", default=True, help="Include sqlalchemy-utility (auto-slugs, timestamps, BaseModel).")
@click.option("--git/--no-git", default=True, help="Initialize a Git repository.")
def main(project_name, factory, db, auth, api, utility, git):
    """Scaffold modern production-ready Flask applications with one command."""
    if not project_name:
        project_name = click.prompt("Enter your project name", default="my_flask_app")

    project_name = project_name.strip().replace(" ", "_").replace("-", "_")

    layout_tag = "Application Factory" if factory else "Simple Modular"
    click.echo("")
    click.secho(f"🚀 Scaffolding Flask project '{project_name}' [{layout_tag}]...", fg="cyan", bold=True)

    target_dir = scaffold_project(
        project_name=project_name,
        factory=factory,
        db=db,
        include_auth=auth,
        include_api=api,
        include_utility=utility,
        init_git=git,
    )

    click.secho(f"\n✨ Project created successfully at ./{project_name}!\n", fg="green", bold=True)
    click.secho("Next steps:", fg="yellow", bold=True)
    click.echo(f"  1. cd {project_name}")
    click.echo("  2. python -m venv .venv")
    click.echo("     # Activate virtualenv:")
    click.echo("     # On Windows:      .venv\\Scripts\\activate")
    click.echo("     # On macOS/Linux:  source .venv/bin/activate")
    click.echo("  3. pip install -r requirements.txt")
    click.echo("  4. flask run\n")


if __name__ == "__main__":
    main()