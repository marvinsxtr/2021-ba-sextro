import json
import os
from os.path import join
from typing import Any, Dict, Optional


def load_json_file(path: str) -> Optional[Dict[str, Any]]:
    """
    Load the contents of a json file as a dict.

    :param path: Path of the file to load
    :return: Dict of the JSON if the file exists
    """
    try:
        with open(path, "r", encoding="utf-8") as json_file:
            data: Dict[str, Any] = json.load(json_file)
        return data
    except:
        return None


def get_data_path() -> str:
    """
    Returns the base path to the data folder.

    :return: The data base path
    """
    return os.environ.get("DATA_PATH", "./data/")


def get_res_path(owner: str = "", repo: str = "") -> str:
    """
    Returns the path of a repository in the data folder.

    :param owner: The owner of the repository
    :param repo: The name of the repository
    :return: The path to the repository
    """
    return join(get_data_path(), "res", owner, repo)
