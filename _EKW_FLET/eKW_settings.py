import json


def read_settings(logs: bool = False) -> dict:
    path = "src/download_config.json"
    jsonloaded = dict()

    with open(path, "r", encoding="utf-8") as file:
        jsonloaded = json.load(file)

    if logs:
        for key, val in jsonloaded.items():
            print(f"{key}: {val}")

    return jsonloaded

def write_settings(params: dict):
    path = "src/download_config.json"

    with open(path, "w", encoding="utf-8") as file:
        json.dump(params, file, ensure_ascii=False, indent=1)


def write_unfinished_tasks(tasks: dict):
    path = "src/unfinished_tasks.json"

    with open(path, "w", encoding="utf-8") as file:
        json.dump(tasks, file, ensure_ascii=False, indent=1)

def read_unfinished_tasks(logs=False):
    path = "src/unfinished_tasks.json"
    jsonloaded = dict()

    with open(path, "r", encoding="utf-8") as file:
        jsonloaded = json.load(file)

    if logs:
        for val in jsonloaded.values():
            print(f"{val}")

    return jsonloaded





if __name__ == "__main__":
    read_settings(True)
    read_unfinished_tasks(True)