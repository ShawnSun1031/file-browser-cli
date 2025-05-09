import asyncio
import logging
import os
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import DirectoryTree

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CustomDirectoryTree(DirectoryTree):
    """A custom directory tree that handles file selection."""

    BINDINGS = [
        ("right", "expand", "Expand"),
        ("left", "collapse", "Collapse"),
    ]

    def on_directory_tree_file_selected(self, event):
        """Handle file selection event."""
        self._handle_selection(event)

    def on_directory_tree_directory_selected(self, event):
        """Handle directory selection event."""
        self._handle_selection(event)

    def _handle_selection(self, event):
        """Handle both file and directory selection."""
        try:
            if not event or not hasattr(event, "path"):
                logger.error("Invalid event or missing path attribute")
                self.app.selected_path = None
                return

            path = Path(event.path)
            if not path.exists():
                logger.error(f"Path does not exist: {path}")
                self.app.selected_path = None
                return

            logger.debug(f"Path selected: {path}")
            self.app.selected_path = path

        except Exception as e:
            logger.error(f"Error handling selection: {e}")
            self.app.selected_path = None
        finally:
            # Ensure the app exits after handling selection
            self.app.exit()
            pending = asyncio.all_tasks()
            for task in pending:
                task.cancel()

    def action_expand(self) -> None:
        """Expand the current node if it's a directory."""
        if self.cursor_node and not self.cursor_node.is_expanded:
            self.cursor_node.expand()
            self.refresh()

    def action_collapse(self) -> None:
        """Collapse the current node if it's a directory."""
        if self.cursor_node and self.cursor_node.is_expanded:
            self.cursor_node.collapse()
            self.refresh()


class DirectoryTreeApp(App):
    BINDINGS = [
        Binding("enter", "select_path", "Select Path"),
        Binding("right", "expand", "Expand Folder"),
        Binding("left", "collapse", "Collapse Folder"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.selected_path = None

    def compose(self) -> ComposeResult:
        yield CustomDirectoryTree("./")

    def action_select_path(self) -> None:
        """Handle path selection."""
        tree = self.query_one(CustomDirectoryTree)
        logger.debug(f"Cursor node: {tree.cursor_node}")

        if tree.cursor_node:
            try:
                # Get the path from the node's data
                node_data = tree.cursor_node.data
                logger.debug(f"Node data type: {type(node_data)}")
                logger.debug(f"Node data: {node_data}")

                # The path is stored in the node's data
                if node_data.loaded:
                    # Try to get the path from the node's data
                    if hasattr(node_data, "path"):
                        path_str = str(node_data.path)
                    else:
                        # If no path attribute, try to get it from the node's label
                        path_str = str(tree.cursor_node.label)

                    logger.debug(f"Path string: {path_str}")
                    self.exit()

                    # Create the path object and resolve it
                    try:
                        # Convert to absolute path
                        abs_path = os.path.abspath(path_str)
                        logger.debug(f"Absolute path: {abs_path}")

                        path = Path(abs_path)
                        if not path.exists():
                            logger.error(f"Path does not exist: {path}")
                            self.selected_path = None
                        else:
                            self.selected_path = path
                            logger.debug(f"Selected path: {self.selected_path}")
                            # Exit the app after successful selection
                            self.exit()
                    except Exception as e:
                        logger.error(f"Error resolving path: {e}")
                        self.selected_path = None
                        self.exit()
                else:
                    logger.error("No node data available")
                    self.selected_path = None
                    self.exit()
            except Exception as e:
                logger.error(f"Error selecting path: {e}")
                self.selected_path = None
                self.exit()

    def action_expand(self) -> None:
        """Expand the current directory."""
        tree = self.query_one(CustomDirectoryTree)
        tree.action_expand()

    def action_collapse(self) -> None:
        """Collapse the current directory."""
        tree = self.query_one(CustomDirectoryTree)
        tree.action_collapse()

    def action_quit(self) -> None:
        """Handle quit action."""
        self.selected_path = None
        self.exit()
