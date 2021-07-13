import json
import os
from os.path import join


def load_json_file(path: str) -> dict:
  try:
    with open(path, "r", encoding="utf-8") as json_file:
      data = json.load(json_file)
    return data
  except:
    return {}


def get_data_path() -> str:
  return os.environ.get("DATA_PATH", "./data/")


def get_res_path(owner="", repo="") -> str:
  return join(get_data_path(), "res", owner, repo)
