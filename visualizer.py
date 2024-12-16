import os
import subprocess
import configparser

def read_config(config_path):
    """Чтение конфигурационного файла."""
    config = configparser.ConfigParser()
    config.read(config_path)
    return config['settings']

def get_commits_with_file(repo_path, file_hash):
    """
    Получение коммитов, связанных с файлом по его хешу.
    Возвращает список [(хеш, сообщение)].
    """
    os.chdir(repo_path)  # Переходим в директорию репозитория
    result = subprocess.run(
        ["git", "log", "--all", "--pretty=format:%H|%s", "--", file_hash],
        capture_output=True, text=True
    )
    commits = result.stdout.strip().split("\n")
    return [line.split("|") for line in commits]

def generate_plantuml_graph(commits):
    """
    Генерация текста для графа в формате PlantUML.
    Узлы графа - сообщения коммитов.
    """
    plantuml_text = ["@startuml"]
    for i in range(len(commits) - 1):
        plantuml_text.append(f'"{commits[i][1]}" --> "{commits[i + 1][1]}"')
    plantuml_text.append("@enduml")
    return "\n".join(plantuml_text)

def save_plantuml_file(content, filename="output/graph.puml"):
    os.makedirs("output", exist_ok=True)  # Создаёт папку, если её нет
    with open(filename, "w") as file:
        file.write(content)
    print(f"PlantUML файл сохранён: {filename}")


def visualize_graph(plantuml_path, puml_file):
    """
    Запуск PlantUML для визуализации графа.
    Требует установленный Java и plantuml.jar.
    """
    subprocess.run(["java", "-jar", plantuml_path, puml_file])

def main():
    # 1. Чтение конфигурации
    config = read_config("config.ini")
    visualizer_path = config["visualizer_path"]
    repo_path = config["repository_path"]
    file_hash = config["file_hash"]

    # 2. Получение коммитов с упоминанием файла
    commits = get_commits_with_file(repo_path, file_hash)
    if not commits:
        print("Нет коммитов для указанного файла!")
        return

    # 3. Построение графа зависимостей
    plantuml_graph = generate_plantuml_graph(commits)
    save_plantuml_file(plantuml_graph)

    # 4. Визуализация графа
    visualize_graph(visualizer_path, "graph.puml")

if __name__ == "__main__":
    main()
