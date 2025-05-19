import asyncio
import logging
import os
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    DirectoryTree,
    Footer,
    Label,
    ListItem,
    ListView,
    Static,
)

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class CustomDirectoryTree(DirectoryTree):
    """A custom directory tree that handles file selection."""

    # BINDINGS = [
    #     ("right", "expand", "Expand"),
    #     ("left", "collapse", "Collapse"),
    # ]

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

    def action_expand(self) -> None:
        """Expand the current node if it's a directory."""
        if self.cursor_node:
            if not self.cursor_node.is_expanded:
                self.cursor_node.expand()
                self.refresh()
            else:
                # if expanded, change root path to the current node
                self.path = Path(self.cursor_node.data.path)
                self.refresh()

    def action_collapse(self) -> None:
        """Collapse the current node if it's a directory.
        如果目前在 root，則切換到 root 的 parent。
        """
        if self.cursor_node:
            if self.cursor_node.is_expanded:
                self.cursor_node.collapse()
                self.refresh()
            # self.action_page_down()
            # self.move_cursor_to_line(2, animate=True)
            # 如果目前在 root 節點
            if self.cursor_node.parent is None:
                # 取得目前 root 路徑
                current_root = Path(self.path)
                parent_root = current_root.parent
                # 如果還有上層目錄就切換
                if parent_root != current_root:
                    self.path = str(parent_root)


class DirectoryTreeApp(App):
    BINDINGS = [
        # Binding("right", "expand", "Expand"),
        # Binding("left", "collapse", "Collapse"),
        # Binding("enter", "select_path", "Select Path"),
        Binding("right", "expand", "Expand Folder", priority=True),
        Binding("left", "collapse", "Collapse Folder", priority=True),
        Binding("a", "select_path", "Select Path"),
        Binding("d", "delete_path", "Delete Path"),
        Binding(
            "tab",
            "switch_container",
            "Switch Panel",
            priority=True,
        ),  # New binding
        Binding("q", "quit", "Quit"),
        # Binding("f", "toggle_files", "Toggle Files"),
    ]

    CSS = """
    .header1 {
        background: blue 50%;
        border: white;
        text-align: center; /* Center text horizontally */
        align: center middle; /* Center text vertically */
    }
    .header2 {
        background: red 50%;
        border: white;
        text-align: center; /* Center text horizontally */
        align: center middle; /* Center text vertically */
    }
    .list-view {
        height: 100%;
        width: 100%;
        background: red 50%;
        border: white;
    }
    .directory-tree {
        height: 100%;
        width: 100%;
        background: blue 50%;
        border: white;
    }
    """

    def __init__(self):
        super().__init__()
        self.selected_paths = None
        self.selected_path = None
        self.list_view = ListView(classes="list-view")
        self.directory_tree = CustomDirectoryTree(os.getcwd(), classes="directory-tree")

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(classes="column"):
                yield Static("Filebrowser", classes="header1")
                yield self.directory_tree
            with Vertical(classes="column"):
                yield Static("Selected Paths", classes="header2")
                yield self.list_view
        yield Footer()

    def action_select_path(self) -> None:
        """Handle path selection."""
        tree = self.query_one(CustomDirectoryTree)
        logger.debug(f"Cursor node: {tree.cursor_node}")

        # Get the selected path
        selected_path = str(tree.cursor_node.data.path)

        # Check if the path already exists in the ListView
        for item in self.list_view.children:
            # Access the Label inside the ListItem
            label = item.query_one(Label)
            if label.renderable == selected_path:
                logger.debug(f"Path already exists in ListView: {selected_path}")
                return

        # Add the unique path to the ListView
        self.list_view.append(
            ListItem(Label(selected_path)),
        )
        logger.debug(f"Added path to ListView: {selected_path}")

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
        # list all the selected paths
        selected_paths = []
        for item in self.list_view.children:
            # Access the Label inside the ListItem
            label = item.query_one(Label)
            selected_paths.append(Path(str(label.renderable)))

        self.selected_paths = selected_paths

        self.exit()
        pending = asyncio.all_tasks()
        for task in pending:
            task.cancel()

    def action_delete_path(self) -> None:
        """Handle path deletion."""
        if self.focused is self.list_view:
            index = self.list_view.index
            self.list_view.pop(index)

    def action_switch_container(self) -> None:
        """Switch focus between the directory tree and the list view."""
        if self.focused is self.query_one(CustomDirectoryTree):
            # Switch focus to the ListView
            self.set_focus(self.list_view)
            logger.debug("Switched focus to ListView.")
        else:
            # Switch focus to the DirectoryTree
            tree = self.query_one(CustomDirectoryTree)
            self.set_focus(tree)
            logger.debug("Switched focus to DirectoryTree.")

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Check if an action may run."""
        if action == "expand" and self.focused is self.list_view:
            return False
        if action == "collapse" and self.focused is self.list_view:
            return False
        if action == "select_path" and self.focused is self.list_view:
            return False
        if action == "delete_path" and self.focused is self.directory_tree:
            return False
        if action == "switch_container":
            return True
        return True
