# """Tests for the file browser module.

# This module contains tests for the file browser functionality, including
# file selection, directory navigation, and error handling.
# """

# import os
# import sys
# import tempfile
# from pathlib import Path
# from unittest.mock import MagicMock, PropertyMock, patch

# import pytest
# from textual.widgets import DirectoryTree


# from file_browser import CustomDirectoryTree, DirectoryTreeApp


# # Test Fixtures
# @pytest.fixture
# def temp_dir():
#     """Create a temporary directory for testing."""
#     with tempfile.TemporaryDirectory() as tmp_dir:
#         yield Path(tmp_dir)


# @pytest.fixture
# def test_file(temp_dir):
#     """Create a test file in the temporary directory."""
#     test_file = temp_dir / "test.txt"
#     test_file.touch()
#     return test_file


# @pytest.fixture
# def mock_tree_with_node(request):
#     """Create a mock tree with a configured node.

#     Usage:
#         @pytest.mark.parametrize("mock_tree_with_node", [
#             {"path": "test.txt"},
#             {"label": "test.txt", "data": None},
#             {"data": MagicMock(path="test.txt")},
#         ], indirect=True)
#     """
#     mock_tree = MagicMock(spec=CustomDirectoryTree)
#     mock_node = MagicMock()

#     config = request.param if hasattr(request, "param") else {}
#     if "path" in config:
#         mock_data = MagicMock()
#         mock_data.path = config["path"]
#         mock_node.data = mock_data
#     elif "data" in config:
#         mock_node.data = config["data"]
#     if "label" in config:
#         mock_node.label = config["label"]

#     mock_tree.cursor_node = mock_node
#     return mock_tree


# class TestFileBrowser:
#     """Test suite for the file browser functionality."""

#     def test_directory_tree_app_initializes_with_no_selection(self):
#         """Test that DirectoryTreeApp initializes with no selected path."""
#         app = DirectoryTreeApp()
#         assert app.selected_path is None

#     def test_custom_directory_tree_is_instance_of_directory_tree(self):
#         """Test that CustomDirectoryTree is a subclass of DirectoryTree."""
#         with patch("textual.app.App.run"):
#             app = DirectoryTreeApp()
#         tree = CustomDirectoryTree("./")
#         assert isinstance(tree, DirectoryTree)

#     @pytest.mark.asyncio
#     async def test_file_selection_sets_selected_path(self, temp_dir, test_file):
#         """Test that selecting a file sets the selected_path property."""
#         async with DirectoryTreeApp().run_test() as pilot:
#             tree = CustomDirectoryTree(str(temp_dir))
#             await pilot.app.mount(tree)
#             await pilot.pause()

#             tree.on_directory_tree_file_selected(MagicMock(path=str(test_file)))
#             assert pilot.app.selected_path == test_file

#     @pytest.mark.asyncio
#     async def test_directory_selection_sets_selected_path(self, temp_dir):
#         """Test that selecting a directory sets the selected_path property."""
#         async with DirectoryTreeApp().run_test() as pilot:
#             tree = CustomDirectoryTree(str(temp_dir))
#             await pilot.app.mount(tree)

#             test_dir = temp_dir / "test_dir"
#             test_dir.mkdir()
#             await pilot.pause()

#             tree.on_directory_tree_file_selected(MagicMock(path=str(test_dir)))
#             assert pilot.app.selected_path == test_dir

#     @pytest.mark.parametrize(
#         "error_class,error_message",
#         [
#             (PermissionError, "Permission denied"),
#             (OSError, "Operation not permitted"),
#             (Exception, "Unexpected error"),
#         ],
#     )
#     @pytest.mark.asyncio
#     async def test_error_handling_during_file_selection(
#         self, error_class, error_message, mock_tree_with_node
#     ):
#         """Test that errors during file selection are handled gracefully."""
#         async with DirectoryTreeApp().run_test() as pilot:
#             with (
#                 patch.object(pilot.app, "query_one", return_value=mock_tree_with_node),
#                 patch.object(Path, "exists", side_effect=error_class(error_message)),
#                 patch("file_browser.logger.error") as mock_logger,
#             ):
#                 pilot.app.action_select_path()
#                 mock_logger.assert_called_with(f"Error resolving path: {error_message}")
#                 assert pilot.app.selected_path is None

#     @pytest.mark.asyncio
#     async def test_exception_in_file_selection_event_handler(self):
#         """Test that exceptions in the file selection event handler are caught."""
#         async with DirectoryTreeApp().run_test() as pilot:
#             tree = CustomDirectoryTree("./")
#             await pilot.app.mount(tree)

#             mock_event = MagicMock()
#             type(mock_event).path = PropertyMock(side_effect=Exception("Test error"))

#             with (
#                 patch.object(pilot.app, "exit"),
#                 patch("file_browser.logger.error") as mock_logger,
#             ):
#                 tree.on_directory_tree_file_selected(mock_event)
#                 mock_logger.assert_called_with(
#                     "Error handling path selection: Test error"
#                 )
#                 assert pilot.app.selected_path is None

#     @pytest.mark.parametrize(
#         "node_data,expected_result,expected_logs",
#         [
#             (None, None, ["Cursor node"]),
#             (
#                 MagicMock(path="test.txt"),
#                 "test.txt",
#                 [
#                     "Cursor node",
#                     "Node data type",
#                     "Node data",
#                     "Path string",
#                     "Absolute path",
#                     "Selected path",
#                 ],
#             ),
#             (MagicMock(), None, ["Cursor node", "Node data type", "Node data"]),
#         ],
#     )
#     @pytest.mark.asyncio
#     async def test_node_data_handling_with_logging(
#         self, node_data, expected_result, expected_logs, temp_dir
#     ):
#         """Test handling of different node data scenarios with logging verification."""
#         async with DirectoryTreeApp().run_test() as pilot:
#             if expected_result:
#                 test_file = temp_dir / expected_result
#                 test_file.touch()
#                 if hasattr(node_data, "path"):
#                     node_data.path = str(test_file)
#                 expected_result = test_file

#             mock_tree = MagicMock(spec=CustomDirectoryTree)
#             mock_node = MagicMock()
#             mock_node.data = node_data
#             mock_tree.cursor_node = mock_node

#             with (
#                 patch.object(pilot.app, "query_one", return_value=mock_tree),
#                 patch("file_browser.logger.debug") as mock_logger,
#                 patch.object(pilot.app, "exit"),
#             ):
#                 pilot.app.action_select_path()

#                 # Verify all expected log messages were called
#                 log_calls = [call.args[0] for call in mock_logger.mock_calls]
#                 for expected_log in expected_logs:
#                     assert any(expected_log in log for log in log_calls), (
#                         f"Expected log containing '{expected_log}' not found in {log_calls}"
#                     )

#                 assert pilot.app.selected_path == expected_result

#     @pytest.mark.parametrize(
#         "event,expected_result",
#         [
#             (None, None),
#             (MagicMock(), None),
#             (MagicMock(path="test.txt"), "test.txt"),
#         ],
#     )
#     @pytest.mark.asyncio
#     async def test_event_handling_with_different_events(
#         self, event, expected_result, temp_dir
#     ):
#         """Test handling of different event scenarios."""
#         async with DirectoryTreeApp().run_test() as pilot:
#             tree = CustomDirectoryTree(str(temp_dir))
#             await pilot.app.mount(tree)

#             if expected_result:
#                 test_file = temp_dir / expected_result
#                 test_file.touch()
#                 if hasattr(event, "path"):
#                     event.path = str(test_file)
#                 expected_result = test_file

#             with patch.object(pilot.app, "exit"):
#                 tree.on_directory_tree_file_selected(event)
#                 assert pilot.app.selected_path == expected_result

#     @pytest.mark.asyncio
#     async def test_quit_action_clears_selection(self):
#         """Test that quit action clears the selected path."""
#         async with DirectoryTreeApp().run_test() as pilot:
#             pilot.app.action_quit()
#             assert pilot.app.selected_path is None

#     @pytest.mark.asyncio
#     async def test_app_initialization_mounts_directory_tree(self):
#         """Test that app initialization properly mounts the directory tree."""
#         async with DirectoryTreeApp().run_test() as pilot:
#             tree = CustomDirectoryTree("./")
#             await pilot.app.mount(tree)
#             assert pilot.app.selected_path is None
#             mounted_tree = pilot.app.query_one(DirectoryTree)
#             assert isinstance(mounted_tree, CustomDirectoryTree)

#     def test_main_function_runs_app(self):
#         """Test that the main function runs the app."""
#         with patch("textual.app.App.run") as mock_run:
#             app = DirectoryTreeApp()
#             app.run()
#             mock_run.assert_called_once()

#     @pytest.mark.asyncio
#     async def test_file_selection_debug_logging(self, temp_dir):
#         """Test debug logging when a file is selected."""
#         async with DirectoryTreeApp().run_test() as pilot:
#             tree = CustomDirectoryTree(str(temp_dir))
#             await pilot.app.mount(tree)

#             test_file = temp_dir / "test.txt"
#             test_file.touch()

#             with patch("file_browser.logger.debug") as mock_debug:
#                 tree.on_directory_tree_file_selected(MagicMock(path=str(test_file)))
#                 mock_debug.assert_called_with(f"Path selected: {test_file}")
#                 assert pilot.app.selected_path == test_file

#     @pytest.mark.asyncio
#     async def test_node_label_fallback(self):
#         """Test using node label when node data has no path attribute."""
#         async with DirectoryTreeApp().run_test() as pilot:
#             # Create a mock node with data that has no path attribute
#             mock_tree = MagicMock(spec=CustomDirectoryTree)
#             mock_node = MagicMock()
#             # Create a mock data object without a path attribute
#             mock_data = MagicMock(
#                 spec=object
#             )  # spec=object ensures no default attributes
#             mock_node.data = mock_data
#             mock_node.label = "test.txt"
#             mock_tree.cursor_node = mock_node

#             with (
#                 patch.object(pilot.app, "query_one", return_value=mock_tree),
#                 patch.object(Path, "exists", return_value=True),
#                 patch("file_browser.logger.debug") as mock_debug,
#             ):
#                 pilot.app.action_select_path()

#                 # Verify debug logs
#                 debug_calls = [call.args[0] for call in mock_debug.mock_calls]
#                 assert any("Path string: test.txt" in call for call in debug_calls)

#                 # Verify the path was set using the label
#                 assert pilot.app.selected_path is not None
#                 assert pilot.app.selected_path.name == "test.txt"

#     @pytest.mark.asyncio
#     async def test_no_node_data_available(self):
#         """Test error handling when no node data is available."""
#         async with DirectoryTreeApp().run_test() as pilot:
#             mock_tree = MagicMock()
#             mock_tree.cursor_node = MagicMock()
#             mock_tree.cursor_node.data = None

#             with (
#                 patch.object(pilot.app, "query_one", return_value=mock_tree),
#                 patch("file_browser.logger.error") as mock_error,
#             ):
#                 pilot.app.action_select_path()
#                 mock_error.assert_called_with("No node data available")
#                 assert pilot.app.selected_path is None

#     @pytest.mark.parametrize(
#         "mock_tree_with_node",
#         [
#             {"path": "test.txt"},
#             {"label": "test.txt", "data": None},
#             {"data": MagicMock(path="test.txt")},
#         ],
#         indirect=True,
#     )
#     @pytest.mark.asyncio
#     async def test_mock_tree_with_node_fixture(self, mock_tree_with_node):
#         """Test the mock_tree_with_node fixture with different configurations."""
#         async with DirectoryTreeApp().run_test() as pilot:
#             with patch.object(pilot.app, "query_one", return_value=mock_tree_with_node):
#                 pilot.app.action_select_path()
#                 # The test passes if no exceptions are raised
#                 assert True

#     @pytest.mark.asyncio
#     async def test_folder_expansion(self):
#         """Test expanding a folder using the right arrow key."""
#         async with DirectoryTreeApp().run_test() as pilot:
#             tree = CustomDirectoryTree("./")
#             await pilot.app.mount(tree)
#             await pilot.pause()

#             # Create a mock node that is not expanded
#             mock_node = MagicMock()
#             mock_node.is_expanded = False
#             mock_node.expand = MagicMock()

#             # Mock the cursor_node property
#             with patch.object(
#                 tree, "cursor_node", new_callable=PropertyMock, return_value=mock_node
#             ):
#                 tree.action_expand()
#                 mock_node.expand.assert_called_once()

#     @pytest.mark.asyncio
#     async def test_folder_collapse(self):
#         """Test collapsing a folder using the left arrow key."""
#         async with DirectoryTreeApp().run_test() as pilot:
#             tree = CustomDirectoryTree("./")
#             await pilot.app.mount(tree)
#             await pilot.pause()

#             # Create a mock node that is expanded
#             mock_node = MagicMock()
#             mock_node.is_expanded = True
#             mock_node.collapse = MagicMock()

#             # Mock the cursor_node property
#             with patch.object(
#                 tree, "cursor_node", new_callable=PropertyMock, return_value=mock_node
#             ):
#                 tree.action_collapse()
#                 mock_node.collapse.assert_called_once()

#     @pytest.mark.asyncio
#     async def test_path_selection(self, temp_dir):
#         """Test selecting both files and folders."""
#         async with DirectoryTreeApp().run_test() as pilot:
#             tree = CustomDirectoryTree(str(temp_dir))
#             await pilot.app.mount(tree)
#             await pilot.pause()

#             # Create a test file and directory
#             test_file = temp_dir / "test.txt"
#             test_file.touch()
#             test_dir = temp_dir / "test_dir"
#             test_dir.mkdir()

#             # Select file
#             tree.on_directory_tree_file_selected(MagicMock(path=str(test_file)))
#             assert pilot.app.selected_path == test_file

#             # Select directory
#             tree.on_directory_tree_file_selected(MagicMock(path=str(test_dir)))
#             assert pilot.app.selected_path == test_dir
