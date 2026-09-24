"""Click CLI interface for flask-create-app."""
import click
from pathlib import Path
from .generator import scaffold_project


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("project_name", required=False)
@click.option("--factory", is_flag=True, default=False, help="Generate modular Application Factory structure.")
@click.option("--here", "-c", is_flag=True, default=False, help="Generate structure directly in current directory without creating a subfolder.")
@click.option("--db", type=click.Choice(["sqlite", "postgres", "mysql"], case_sensitive=False), default="sqlite", help="Target database dialect.")
@click.option("--auth/--no-auth", default=True, help="Include flask-user-auth (dual token + session authentication).")
@click.option("--api/--no-api", default=True, help="Include flask-api-builder (RESTful CRUD endpoints & schemas).")
@click.option("--utility/--no-utility", default=True, help="Include sqlalchemy-utility (auto-slugs, timestamps, BaseModel).")
@click.option("--git/--no-git", default=True, help="Initialize a Git repository.")
def main(project_name, factory, here, db, auth, api, utility, git):
    """Scaffold modern production-ready Flask applications with one command.

    To scaffold into the CURRENT directory without creating a subfolder:
      flask-create-app .
      or
      flask-create-app --here

    To scaffold into a NEW subfolder:
      flask-create-app my_project
    """
    is_current_dir = here or (project_name is not None and project_name.strip() == ".")

    if not project_name and not here:
        current_name = Path.cwd().resolve().name
        project_name = click.prompt(
            f"Enter project name (or '.' for current directory '{current_name}')",
            default="."
        )
        if project_name.strip() == ".":
            is_current_dir = True

    if is_current_dir:
        resolved_dir = Path.cwd().resolve()
        clean_name = resolved_dir.name.strip().replace(" ", "_").replace("-", "_")
        app_name = clean_name or "flask_app"
        target_arg = "."
        target_path = str(resolved_dir)
        display_target = f"current directory ({resolved_dir.name})"
    else:
        app_name = project_name.strip().replace(" ", "_").replace("-", "_")
        target_arg = app_name
        target_path = None
        display_target = f"./{app_name}"

    layout_tag = "Application Factory" if factory else "Simple Modular"
    click.echo("")
    click.secho(f">> Scaffolding Flask project '{app_name}' [{layout_tag}] in {display_target}...", fg="cyan", bold=True)

    out_dir = scaffold_project(
        project_name=target_arg,
        target_path=target_path,
        factory=factory,
        db=db,
        include_auth=auth,
        include_api=api,
        include_utility=utility,
        init_git=git,
    )

    if is_current_dir:
        click.secho("\n[+] Project structure generated successfully in current directory!\n", fg="green", bold=True)
    else:
        click.secho(f"[+] Project created successfully at ./{app_name}!\n", fg="green", bold=True)

    click.secho("Next steps:", fg="yellow", bold=True)
    step = 1
    if not is_current_dir:
        click.echo(f"  {step}. cd {app_name}")
        step += 1
    click.echo(f"  {step}. python -m venv .venv")
    click.echo("     # Activate virtualenv:")
    click.echo("     # On Windows:      .venv\\Scripts\\activate")
    click.echo("     # On macOS/Linux:  source .venv/bin/activate")
    step += 1
    click.echo(f"  {step}. pip install -r requirements.txt")
    step += 1
    click.echo(f"  {step}. flask run\n")


if __name__ == "__main__":
    main()