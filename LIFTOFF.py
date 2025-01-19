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

def fill_mission(use_voice=False, debug=False, dry_run=False):
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

def check_api_key():
    """Check if ANTHROPIC_API_KEY is set, load from .env if exists, or prompt user."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    # If not in environment, try to load from .env
    if not api_key:
        env_path = os.path.join(os.getcwd(), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('ANTHROPIC_API_KEY='):
                        api_key = line.split('=')[1].strip().strip('"').strip("'")
                        break
    
    # If still no API key, prompt user and save to .env
    if not api_key:
        console.print("[yellow]No Anthropic API key found.[/yellow]")
        api_key = Prompt.ask("Please enter your Anthropic API key")
        
        # Save to .env file
        env_path = os.path.join(os.getcwd(), '.env')
        with open(env_path, 'a') as f:
            f.write(f'\nANTHROPIC_API_KEY="{api_key}"')
        console.print("[green]API key saved to .env file[/green]")
    
    # Set for current session
    os.environ['ANTHROPIC_API_KEY'] = api_key
    return True

def check_aider_installation():
    """Check if aider is installed and accessible, install if missing."""
    try:
        import aider
        # Check API key after confirming aider is installed
        return check_api_key()
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


def run_aider(prompt, files_to_add, use_voice=False, debug=False, dry_run=False):
    """Run Droid Assistant using aider's Python API."""
    if not check_aider_installation():
        console.print("[red]Failed to setup required components.[/red]")
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
            coder.run("/map-refresh")
            result = coder.run(prompt)
            coder.run("/map-refresh")
            
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
                coder.run("/map-refresh")
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

@app.command(help="Launch the documentation process")
def launch(
    debug: bool = typer.Option(False, "--debug", help="Enable debug output"),
    voice: bool = typer.Option(False, "--voice", help="Enable voice interaction"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without modifying files")
):
    """Launch the documentation process."""
    console.print(Panel(ASCII_ART, style="bold blue"))
    
    # Fill out the mission and exit
    console.print("\n[bold cyan]Step 1: Defining the Mission[/bold cyan]")
    fill_mission(use_voice=voice, debug=debug, dry_run=dry_run)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context,
    debug: bool = typer.Option(False, "--debug", help="Enable debug output"),
    voice: bool = typer.Option(False, "--voice", help="Enable voice interaction"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without modifying files")):
    """Main callback that runs if no command is provided"""
    if ctx.invoked_subcommand is None:
        launch(debug=debug, voice=voice, dry_run=dry_run)

if __name__ == "__main__":
    app()
