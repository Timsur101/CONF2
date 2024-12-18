#!/usr/bin/env python3
import subprocess
import tempfile
import os
from configparser import ConfigParser

def load_config(config_path):
    cfg = ConfigParser()
    cfg.read(config_path)
    # Имена в config.ini должны совпадать, например:
    # [DEFAULT]
    # visualizer_path = C:\путь\к\plantuml.jar
    # repository_path = C:\путь\к\репозиторию
    # file_hash = <хеш_файла>
    graph_tool = cfg.get("DEFAULT", "visualizer_path")
    repo_path = cfg.get("DEFAULT", "repository_path")
    file_hash = cfg.get("DEFAULT", "file_hash")
    return graph_tool, repo_path, file_hash

def get_commits_for_file(repo_path, file_hash):
    # Используем опцию -C для указания пути к репо
    cmd = f'git -C "{repo_path}" rev-list --all'
    commits = subprocess.check_output(cmd, shell=True).decode("utf-8").split()

    relevant_commits = []
    for c in commits:
        ls_cmd = f'git -C "{repo_path}" ls-tree -r {c}'
        ls_out = subprocess.check_output(ls_cmd, shell=True).decode("utf-8")
        for line in ls_out.splitlines():
            parts = line.strip().split()
            # Формат: <mode> blob <hash> <tab> file
            # parts[0] = mode, parts[1] = "blob", parts[2] = blob_hash, далее имя файла
            if len(parts) >= 3 and parts[1] == "blob":
                blob_h = parts[2]
                if blob_h == file_hash:
                    relevant_commits.append(c)
                    break
    return list(set(relevant_commits))

def get_commit_details(repo_path, commit_hash):
    # Используем двойные кавычки для формата
    # %H - hash, %P - parents, %s - subject
    cmd = f'git -C "{repo_path}" log --pretty=format:"%H %P %s" -1 {commit_hash}'
    out = subprocess.check_output(cmd, shell=True).decode("utf-8")
    parts = out.split(' ', 2)
    chash = parts[0]
    parents = parts[1].split() if len(parts) > 1 else []
    message = parts[2] if len(parts) > 2 else ""
    return chash, parents, message

def build_graph(repo_path, commits):
    graph = {}
    for c in commits:
        chash, parents, msg = get_commit_details(repo_path, c)
        graph[chash] = {
            "message": msg.strip(),
            "parents": parents
        }
    return graph

def generate_plantuml(graph):
    lines = ["@startuml", "skinparam packageStyle rectangle"]
    # Добавляем масштабирование
    lines.append("scale 15")  # или lines.append("scale 300dpi")

    nodes = {}
    for commit, data in graph.items():
        msg = data["message"]
        short_msg = msg[:50].replace("[", "(").replace("]", ")")
        nodes[commit] = f"[{short_msg}]"

    for commit, data in graph.items():
        if data["parents"]:
            for p in data["parents"]:
                if p in nodes:
                    lines.append(f"{nodes[p]} --> {nodes[commit]}")

    lines.append("@enduml")
    return "\n".join(lines)


def visualize(plantuml_text, graph_tool_path):
    # Сохраняем исходник диаграммы PlantUML
    puml_path = os.path.join(os.path.dirname(__file__), "graph.puml")
    with open(puml_path, "w", encoding="utf-8") as f:
        f.write(plantuml_text)
    # Вызываем PlantUML
    cmd = f'java -jar "{graph_tool_path}" "{puml_path}"'
    subprocess.run(cmd, shell=True, check=True)
    # По умолчанию PlantUML создаст graph.png в той же директории
    png_file = puml_path.replace(".puml", ".png")
    return png_file

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "config.ini")
    graph_tool, repo_path, file_hash = load_config(config_path)
    commits = get_commits_for_file(repo_path, file_hash)
    graph = build_graph(repo_path, commits)
    puml = generate_plantuml(graph)
    result_img = visualize(puml, graph_tool)
    print("Граф сгенерирован:", result_img)
