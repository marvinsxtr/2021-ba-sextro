import json
import os
from os.path import join
from typing import Any, Dict, Optional


def load_json_file(path: str, name: str) -> Optional[Dict[str, Any]]:
    """
    Load the contents of a json file as a dict.

    :param path: Path of the file to load
    :param name: Name of the file
    :return: Dict of the json if the file exists
    """
    try:
        with open(join(path, name), "r", encoding="utf-8") as json_file:
            data: Dict[str, Any] = json.load(json_file)
        return data
    except:
        return None


def save_json_file(data: Dict[str, Any], path: str, name: str) -> None:
    """
    Saves a dictionary in a json file

    :param data: Dictionary to be saved in a json file
    :param path: Path to save the dictionary at
    :param name: Name of the json file
    """
    try:
        os.makedirs(path, exist_ok=True)
        with open(join(path, name), "w+", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)
    except:
        return None


def get_data_path(tool: str = "collector") -> str:
    """
    Returns the base path to the data folder.

    :param tool: The tool in the data folder (collector or analyzer)
    :return: The data base path
    """
    default_path = join("./data", tool)
    data_path = os.environ.get("DATA_PATH", default_path)

    return data_path if data_path else default_path


def get_res_path(tool: Optional[str] = None, owner: str = "", repo: str = "") -> str:
    """
    Returns the path of a repository in the data folder.

    :param owner: The owner of the repository
    :param repo: The name of the repository
    :return: The path to the repository
    """
    base_path = get_data_path() if tool is None else get_data_path(tool=tool)
    return join(base_path, "res", owner, repo)
