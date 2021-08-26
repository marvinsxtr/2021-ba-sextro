import json
import sys
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


def get_root_path() -> str:
    """
    Returns the root path of the repository.

    :return: The root path of the project
    """
    path = os.path.dirname(sys.modules['__main__'].__file__).split("/")
    return "/".join(path[:path.index("analyzer")])


def get_data_path(tool: str = "collector") -> str:
    """
    Returns the base path to the data folder.

    :param tool: The tool in the data folder (collector or analyzer)
    :return: The data base path
    """
    default_path = join(get_root_path(), "data", tool)
    data_path = os.environ.get("DATA_PATH", default_path)

    return data_path if data_path else default_path


def get_collector_res_path(owner: str = "", repo: str = "") -> str:
    """
    Returns the path of a repository in the data folder.

    :param collector: Whether to choose the collector or analyzer folder
    :param owner: The owner of the repository
    :param repo: The name of the repository
    :return: The path to the repository
    """
    base_path = get_data_path(tool="collector")
    return join(base_path, "res", owner, repo)


def get_analyzer_res_path() -> str:
    """
    Returns the result path of the analyzer data folder.

    :return: The path to the result folder
    """
    base_path = get_data_path(tool="analyzer")
    return join(base_path, "res")


def remove_keys(dictionary: Dict[str, Any], remove: str) -> Dict[str, Any]:
    """
    Removes a specific key from a dictionary.

    :param dictionary: Dictionary to delete the key from
    :param key: Key to delete from the dictionary
    """
    if isinstance(dictionary, dict):
        dictionary = {
            key: remove_keys(value, remove)
            for key, value in dictionary.items()
            if key not in remove
        }
    elif isinstance(dictionary, list):
        dictionary = [remove_keys(item, remove)
                      for item in dictionary
                      if item not in remove]
    return dictionary
