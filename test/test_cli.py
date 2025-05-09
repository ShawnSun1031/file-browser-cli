"""Tests for the CLI module.

This module contains tests for the command-line interface functionality,
including file creation, error handling, and logging.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from cli import FileCreator, app, get_selected_path
from file_browser import DirectoryTreeApp


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def test_file(tmp_path):
    """Create a test file path in a temporary directory."""
    return tmp_path / "test_file.py"


@pytest.fixture
def nested_test_file(tmp_path):
    """Create a test file path in a nested temporary directory."""
    return tmp_path / "deep" / "nested" / "dir" / "test_file.py"


@pytest.fixture
def mock_browser_app():
    """Create a mock DirectoryTreeApp with a selected path."""
    app = MagicMock(spec=DirectoryTreeApp)
    app.selected_path = None
    return app


class TestFileCreator:
    """Tests for the FileCreator class."""

    def test_create_file_success(self, test_file):
        """Test successful file creation using FileCreator."""
        file_creator = FileCreator(MagicMock(spec=DirectoryTreeApp))
        file_creator.create_file(test_file)
        assert test_file.exists()

    def test_create_file_error(self, test_file):
        """Test error handling in FileCreator."""
        file_creator = FileCreator(MagicMock(spec=DirectoryTreeApp))
        with patch.object(
            Path, "touch", side_effect=PermissionError("Permission denied")
        ):
            with pytest.raises(PermissionError):
                file_creator.create_file(test_file)


class TestPathSelection:
    """Tests for path selection functionality."""

    def test_get_selected_path(self, test_file, mock_browser_app):
        """Test getting selected path from browser."""
        mock_browser_app.selected_path = test_file
        with patch("cli.DirectoryTreeApp", return_value=mock_browser_app):
            result = get_selected_path()
            assert result == test_file


class TestCodeCreation:
    """Tests for code creation functionality."""

    def test_create_code_successful(self, cli_runner, test_file):
        """Test successful code file creation."""
        with patch("cli.get_selected_path", return_value=test_file):
            result = cli_runner.invoke(app, ["code", "create"])
            assert result.exit_code == 0
            assert f"Created new file: {test_file}" in result.stdout
            assert test_file.exists()

    def test_create_code_no_selection(self, cli_runner):
        """Test code creation when no file is selected."""
        with patch("cli.get_selected_path", return_value=None):
            result = cli_runner.invoke(app, ["code", "create"])
            assert result.exit_code == 0
            assert "No file was selected." in result.stdout

    def test_create_code_directory_creation(self, cli_runner, nested_test_file):
        """Test directory creation during code creation."""
        with patch("cli.get_selected_path", return_value=nested_test_file):
            result = cli_runner.invoke(app, ["code", "create"])
            assert result.exit_code == 0
            assert nested_test_file.parent.exists()
            assert nested_test_file.exists()

    @pytest.mark.parametrize(
        "error_class,error_message",
        [
            (PermissionError, "Permission denied"),
            (OSError, "Operation not permitted"),
            (Exception, "Unexpected error"),
        ],
    )
    def test_create_code_error_handling(
        self, cli_runner, test_file, error_class, error_message
    ):
        """Test error handling during code creation with different error types."""
        with (
            patch("cli.get_selected_path", return_value=test_file),
            patch.object(Path, "touch", side_effect=error_class(error_message)),
        ):
            result = cli_runner.invoke(app, ["code", "create"])
            assert result.exit_code == 0
            assert f"Error creating file: {error_message}" in result.stdout
            assert not test_file.exists()


class TestLogging:
    """Tests for logging functionality."""

    def test_create_code_logging(self, cli_runner, test_file):
        """Test logging during successful code creation."""
        with (
            patch("cli.get_selected_path", return_value=test_file),
            patch("cli.logger.debug") as mock_debug,
            patch("cli.logger.error") as mock_error,
        ):
            result = cli_runner.invoke(app, ["code", "create"])
            mock_debug.assert_called_with(f"Selected path from browser: {test_file}")
            mock_error.assert_not_called()
            assert result.exit_code == 0

    def test_create_code_error_logging(self, cli_runner, test_file):
        """Test logging during code creation error."""
        with (
            patch("cli.get_selected_path", return_value=test_file),
            patch.object(
                Path, "touch", side_effect=PermissionError("Permission denied")
            ),
            patch("cli.logger.debug") as mock_debug,
            patch("cli.logger.error") as mock_error,
        ):
            result = cli_runner.invoke(app, ["code", "create"])
            mock_debug.assert_called_with(f"Selected path from browser: {test_file}")
            mock_error.assert_called_with("Error creating file: Permission denied")
            assert result.exit_code == 0

    def test_create_code_no_selection_logging(self, cli_runner):
        """Test logging when no file is selected."""
        with (
            patch("cli.get_selected_path", return_value=None),
            patch("cli.logger.debug") as mock_debug,
            patch("cli.logger.error") as mock_error,
        ):
            result = cli_runner.invoke(app, ["code", "create"])
            mock_debug.assert_called_with("Selected path from browser: None")
            mock_error.assert_called_with("No file was selected")
            assert result.exit_code == 0


def test_main():
    """Test the main function."""
    with patch("cli.app") as mock_app:
        from cli import main

        main()
        mock_app.assert_called_once()
