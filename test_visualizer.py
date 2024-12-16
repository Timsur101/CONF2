import os
import pytest
from visualizer import (
    read_config,
    get_commits_with_file,
    generate_plantuml_graph,
    save_plantuml_file
)

# Создаём тестовый config.ini для тестов
TEST_CONFIG_FILE = "test_config.ini"
TEST_REPO_PATH = "./test_repo"  # Укажите путь к тестовому репозиторию
TEST_HASH = "example_file.txt"  # Тестовый файл в репозитории


@pytest.fixture
def sample_config():
    """Фикстура для создания тестового config.ini."""
    with open(TEST_CONFIG_FILE, "w") as f:
        f.write("[settings]\n")
        f.write(f"visualizer_path = /path/to/plantuml.jar\n")
        f.write(f"repository_path = {TEST_REPO_PATH}\n")
        f.write(f"file_hash = {TEST_HASH}\n")
    yield TEST_CONFIG_FILE
    os.remove(TEST_CONFIG_FILE)


def test_read_config(sample_config):
    """Тестирование функции чтения конфигурации."""
    config = read_config(sample_config)
    assert config["visualizer_path"] == "/path/to/plantuml.jar"
    assert config["repository_path"] == TEST_REPO_PATH
    assert config["file_hash"] == TEST_HASH


def test_get_commits_with_file(monkeypatch):
    """Тестирование функции получения коммитов с файлом."""

    def mock_run(*args, **kwargs):
        """Мок для подмены вызова subprocess.run."""
        class MockResult:
            stdout = "a1b2c3d4|Fix bug in file\nb5c6d7e8|Update file content"
        return MockResult()

    monkeypatch.setattr("subprocess.run", mock_run)

    commits = get_commits_with_file(TEST_REPO_PATH, TEST_HASH)
    assert len(commits) == 2
    assert commits[0] == ["a1b2c3d4", "Fix bug in file"]
    assert commits[1] == ["b5c6d7e8", "Update file content"]


def test_generate_plantuml_graph():
    """Тестирование генерации текста PlantUML-графа."""
    commits = [["a1b2c3d4", "Fix bug in file"], ["b5c6d7e8", "Update file content"]]
    result = generate_plantuml_graph(commits)
    expected = '@startuml\n"Fix bug in file" --> "Update file content"\n@enduml'
    assert result.strip() == expected


def test_save_plantuml_file(tmpdir):
    """Тестирование сохранения PlantUML-файла."""
    content = '@startuml\nA --> B\n@enduml'
    file_path = os.path.join(tmpdir, "test_graph.puml")
    save_plantuml_file(content, file_path)

    assert os.path.exists
