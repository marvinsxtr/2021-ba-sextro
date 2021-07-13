from os import listdir
from os.path import isfile, join

from analyzer.src.utils import get_res_path, load_json_file


def analyze(repo_count: int):
  analyzed_repos: int = 0
  owners: list = listdir(get_res_path())

  for owner in owners:
    repos: list = listdir(get_res_path(owner=owner))

    for repo in repos:

      if analyzed_repos > repo_count:
        return

      repo_path: str = get_res_path(owner=owner, repo=repo)

      result_files: list = [f for f in listdir(repo_path) if isfile(join(repo_path, f))]

      for result_file in result_files:
        _contents: dict = load_json_file(join(repo_path, result_file))
        # TODO

      analyzed_repos += 1
