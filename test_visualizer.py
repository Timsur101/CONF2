import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Для корректного импорта, если нужно:
# sys.path.append(os.path.dirname(__file__))
from visualizer import load_config, get_commits_for_file, build_graph, generate_plantuml, visualize

class TestVisualizer(unittest.TestCase):

    @patch("visualizer.ConfigParser")
    def test_load_config(self, mock_cp):
        mock_inst = MagicMock()
        mock_inst.get.side_effect = ["/path/to/plantuml.jar", "/path/to/repo", "abc123"]
        mock_cp.return_value = mock_inst
        graph_tool, repo_path, file_hash = load_config("config.ini")
        self.assertEqual(graph_tool, "/path/to/plantuml.jar")
        self.assertEqual(repo_path, "/path/to/repo")
        self.assertEqual(file_hash, "abc123")

    @patch("visualizer.subprocess.check_output")
    def test_get_commits_for_file(self, mock_subproc):
        # Мокаем вывод для rev-list и ls-tree
        # Первый вызов: rev-list
        # Второй и далее: ls-tree 
        mock_subproc.side_effect = [
            b"commit1\ncommit2\n",
            b"100644 blob abc123\tfile.txt\n",
            b"100644 blob otherhash\tother.txt\n"
        ]
        commits = get_commits_for_file("/path/to/repo", "abc123")
        self.assertIn("commit1", commits)
        self.assertEqual(len(commits), 1)

    def test_build_graph(self):
        with patch("visualizer.get_commit_details") as mock_gcd:
            mock_gcd.side_effect = [
                ("commit1", [], "Initial commit"),
                ("commit2", ["commit1"], "Second commit")
            ]
            graph = build_graph("/repo", ["commit1", "commit2"])
            self.assertIn("commit1", graph)
            self.assertIn("commit2", graph)
            self.assertEqual(graph["commit2"]["parents"], ["commit1"])

    def test_generate_plantuml(self):
        graph = {
            "commit1": {"message": "Initial commit", "parents": []},
            "commit2": {"message": "Second commit", "parents": ["commit1"]}
        }
        puml = generate_plantuml(graph)
        self.assertIn("commit1", puml)
        self.assertIn("commit2", puml)
        self.assertIn("-->", puml)

    @patch("visualizer.subprocess.run")
    def test_visualize(self, mock_run):
        puml = "@startuml\n@enduml"
        path = visualize(puml, "/path/to/plantuml.jar")
        self.assertTrue(path.endswith(".png"))
        mock_run.assert_called_once()

if __name__ == "__main__":
    unittest.main()
