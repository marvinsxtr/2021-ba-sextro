import json
import os
from os.path import join
from typing import Any, Dict, Optional


def load_json_file(path: str) -> Optional[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as json_file:
            data: Dict[str, Any] = json.load(json_file)
        return data
    except:
        return None


def get_data_path() -> str:
    return os.environ.get("DATA_PATH", "./data/")


def get_res_path(owner: str = "", repo: str = "") -> str:
    return join(get_data_path(), "res", owner, repo)
