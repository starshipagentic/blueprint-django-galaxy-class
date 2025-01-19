import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import subprocess
import sys
import os
import platform
import time

console = Console()
app = typer.Typer(help="Project LIFTOFF - Documentation Generator")
commands = typer.Typer()
app.add_typer(commands, name="")

ASCII_ART = """
🚀 PROJECT LIFTOFF 🚀
====================
Initiating Documentation Sequence...
"""

def install_vscode_cli_macos():
    """Attempt to install VS Code CLI tools on macOS."""
    # Check if VS Code is installed
    vscode_path = "/Applications/Visual Studio Code.app"
    if not os.path.exists(vscode_path):
        console.print("[red]VS Code is not installed in /Applications.[/red]")
        return False

    cli_source = "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
    cli_target = "/usr/local/bin/code"

    try:
        # Remove existing symlink if it exists
        if os.path.exists(cli_target):
            console.print("[yellow]Removing existing VS Code CLI link...[/yellow]")
            subprocess.run(['sudo', 'rm', cli_target], check=True)

        # Create new symlink
        console.print("[yellow]Installing VS Code CLI tools...[/yellow]")
        subprocess.run(['sudo', 'ln', '-s', cli_source, cli_target], check=True)
        
        # Verify installation
        result = subprocess.run(['which', 'code'], capture_output=True, text=True)
        if result.stdout.strip():
            console.print("[green]Successfully installed VS Code command line tools.[/green]")
            return True
        else:
            console.print("[red]Installation seemed to succeed but 'code' command not found.[/red]")
            return False
            
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to install VS Code command line tools: {str(e)}[/red]")
        return False

def open_markdown(file_path):
    """Open a markdown file in the default viewer."""
    try:
        if platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', file_path], check=True)
            return True
        else:
            console.print("[yellow]Opening Markdown files is currently only supported on macOS.[/yellow]")
            return False
    except subprocess.CalledProcessError:
        console.print(f"[red]Failed to open {file_path}[/red]")
        return False

def fill_mission(debug=False, dry_run=False):
    """Use aider to fill out MISSION.md"""
    console.print("\n[cyan]Let's define the mission of your project.[/cyan]")
    console.print("[yellow]First, review the current MISSION.md[/yellow]")
    
    # Open MISSION.md in default markdown viewer
    if open_markdown("MISSION.md"):
        # Wait for user to indicate they're ready to proceed
        Prompt.ask("\nPress Enter when you've reviewed the mission", default="")
    
    console.print("[yellow]Now we'll work with the Droid Assistant to complete the remaining sections.[/yellow]")
    
    mission_prompt = """Please help complete the remaining sections in MISSION.md based on the GOAL that's already defined. Write detailed, specific content for each section."""

    run_aider(mission_prompt, ["MISSION.md"], debug=debug, dry_run=dry_run)
    raise typer.Exit()

def check_aider_installation():
    """Check if aider is installed and accessible, install if missing."""
    try:
        import aider
        return True
    except ImportError:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[yellow]Installing Droid Assistant...[/yellow]", total=None)
            try:
                # Install aider with all optional dependencies
                subprocess.run([sys.executable, "-m", "pip", "install", "aider-chat[all]>=0.71.1"], 
                             check=True,
                             capture_output=True)
                progress.stop()
                console.print("[green]Successfully installed Droid Assistant.[/green]")
                return True
            except subprocess.CalledProcessError as e:
                progress.stop()
                console.print("[red]Failed to install Droid Assistant.[/red]")
                console.print(f"[red]Error: {str(e)}[/red]")
                return False


def run_aider(prompt, files_to_add, debug=False, dry_run=False):
    """Run Droid Assistant using aider's Python API."""
    if not check_aider_installation():
        raise typer.Exit(code=1)
        
    from aider.coders import Coder
    from aider.models import Model
    from aider.io import InputOutput
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        try:
            # Create a progress task
            task = progress.add_task("Droid is thinking...", total=None)
            
            # Initialize aider components
            model = Model("claude-3-5-sonnet-20241022")
            io = InputOutput(yes=True)  # Auto-confirm changes
            
            if debug:
                console.print(f"[yellow]Sending initial prompt: {prompt}[/yellow]")
            
            # Create coder instance with additional options
            coder = Coder.create(
                main_model=model,
                fnames=files_to_add,
                io=io,
                auto_commits=True,
                dry_run=dry_run
            )
            
            if dry_run:
                console.print("[yellow]Running in dry-run mode - no files will be modified[/yellow]")
            
            # Execute the prompt
            progress.stop()
            result = coder.run(prompt)
            
            if debug:
                console.print("[dim]Aider completed processing[/dim]")
            
            # Check if MISSION.md was modified
            try:
                with open("MISSION.md", "r") as f:
                    current_content = f.read()
                    if "[Describe the specific problem" not in current_content:
                        console.print("[green]✓ Mission sections have been updated[/green]")
            except Exception as e:
                if debug:
                    console.print(f"[red]Error checking MISSION.md: {str(e)}[/red]")
            
            # Ask about additional changes
            while True:
                more_changes = Prompt.ask("\nWould you like to make more changes?", choices=["y", "n"], default="n")
                if more_changes.lower() == "n":
                    break
                
                new_prompt = Prompt.ask("What changes would you like to make")
                if new_prompt.lower() == "none":
                    break
                    
                progress.start()
                progress.update(task, description="Droid is thinking...")
                result = coder.run(new_prompt)
                progress.stop()
                
        except KeyboardInterrupt:
            progress.stop()
            console.print("\n[yellow]Operation cancelled by user.[/yellow]")
            raise typer.Exit(code=1)
        except Exception as e:
            progress.stop()
            console.print(f"[red]Error running aider: {str(e)}[/red]")
            raise typer.Exit(code=1)

@commands.command(help="Push changes to GitHub repository")
def push(
    message: str = typer.Option(None, "--message", "-m", help="Commit message"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug output")
):
    """Push changes to GitHub repository."""
    try:
        if message is None:
            message = Prompt.ask("Enter commit message")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[yellow]Pushing changes...[/yellow]", total=None)
            
            # Add all changes
            if debug:
                console.print("[yellow]Adding changes...[/yellow]")
            subprocess.run(["git", "add", "."], check=True)
            
            # Commit changes
            if debug:
                console.print(f"[yellow]Committing with message: {message}[/yellow]")
            subprocess.run(["git", "commit", "-m", message], check=True)
            
            # Push changes
            if debug:
                console.print("[yellow]Pushing to remote...[/yellow]")
            subprocess.run(["git", "push"], check=True)
            
            progress.stop()
            console.print("[green]Successfully pushed changes to GitHub![/green]")
            
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error pushing changes: {str(e)}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        raise typer.Exit(code=1)

@commands.command(help="Launch the documentation process")
def launch(
    debug: bool = typer.Option(False, "--debug", help="Enable debug output"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without modifying files")
):
    """Launch the documentation process."""
    console.print(Panel(ASCII_ART, style="bold blue"))
    
    # Fill out the mission and exit
    console.print("\n[bold cyan]Step 1: Defining the Mission[/bold cyan]")
    fill_mission(debug=debug, dry_run=dry_run)

if __name__ == "__main__":
    try:
        app()
    except typer.Exit:
        # Only launch if no command was provided (sys.argv has length 1)
        if len(sys.argv) == 1:
            launch()
        else:
            raise
