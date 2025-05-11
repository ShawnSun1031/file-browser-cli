"""Command-line interface for file operations.

This module provides a CLI interface for file operations using Typer.
It includes commands for creating new files with a file browser interface.
"""

import logging
from pathlib import Path
from typing import Optional

import typer
from typer import Typer

from file_browser_cli.file_browser import DirectoryTreeApp

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Typer apps
app = Typer(help="File operations CLI")
code_app = Typer(help="Code file operations")
app.add_typer(code_app, name="code")


class FileCreator:
    """Handles file creation operations."""

    def __init__(self, browser_app: DirectoryTreeApp):
        """Initialize the file creator.

        Args:
            browser_app: The file browser application instance.
        """
        self.browser_app = browser_app

    def create_file(self, path: Path) -> None:
        """Create a new file at the specified path.

        Args:
            path: The path where the file should be created.

        Raises:
            Exception: If file creation fails.
        """
        try:
            # Ensure the parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            # Create the file
            path.touch()
            typer.echo(f"Created new file: {path}")
        except Exception as e:
            logger.error(f"Error creating file: {e}")
            typer.echo(f"Error creating file: {e}", err=True)
            raise


def get_selected_path() -> Optional[Path]:
    """Get the selected path from the file browser.

    Returns:
        Optional[Path]: The selected path or None if no path was selected.
    """

    browser_app = DirectoryTreeApp()
    browser_app.run()

    return browser_app.selected_path


@code_app.command("create")
def create_code() -> None:
    """Create a new code file with file browser selection.

    This command opens a file browser interface to select a location
    for the new file. The file will be created at the selected location.
    """
    selected_path = get_selected_path()
    logger.debug(f"Selected path from browser: {selected_path}")

    if not selected_path:
        logger.error("No file was selected")
        typer.echo("No file was selected.")
        return

    file_creator = FileCreator(DirectoryTreeApp())
    try:
        file_creator.create_file(selected_path)
    except Exception:
        # Error is already logged and echoed in create_file
        pass


@app.callback(invoke_without_command=True)
def main():
    """
    Manage users in the awesome CLI app.
    """
    create_code()


if __name__ == "__main__":
    app()
