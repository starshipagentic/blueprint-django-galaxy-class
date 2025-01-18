import os
import shutil
import typer
from rich.console import Console
from rich.prompt import Prompt

app = typer.Typer()
console = Console()

def remove_if_exists(path):
    """Safely remove a file or directory if it exists."""
    if os.path.isfile(path):
        os.remove(path)
        console.print(f"[red]Removed file: {path}[/red]")
    elif os.path.isdir(path):
        shutil.rmtree(path)
        console.print(f"[red]Removed directory: {path}[/red]")

@app.command()
def destroy():
    """Remove development files and directories."""
    
    # Get app name from user
    app_name = Prompt.ask("\n[bold red]Enter your app name to destroy")
    
    # Confirm destruction
    confirmation = Prompt.ask(
        "\n[bold red]Type 'DESTROY' to confirm deletion of development files",
        default=""
    )
    
    if confirmation != "DESTROY":
        console.print("\n[yellow]Destruction cancelled[/yellow]")
        raise typer.Exit()
    
    # Files to remove
    files_to_remove = [
        "manage.py",
        "requirements.txt",
        "setup.py",
        "behave.ini",
        "db.sqlite3",
        "pytest.ini",
        ".gitignore"
    ]
    
    # Directories to remove
    dirs_to_remove = [
        "venv",
        "tests",
        "features",
        app_name,
        "config"
    ]
    
    console.print("\n[bold red]Initiating destruction sequence...[/bold red]")
    
    # Remove files
    for file in files_to_remove:
        remove_if_exists(file)
    
    # Remove directories
    for directory in dirs_to_remove:
        remove_if_exists(directory)
    
    console.print("\n[bold red]Destruction complete![/bold red]")

if __name__ == "__main__":
    app()
