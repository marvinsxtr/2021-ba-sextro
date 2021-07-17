from os import listdir
from os.path import isfile, join
from typing import Any, Dict, List

from analyzer.src.mappings import Mappings
from analyzer.src.utils import get_res_path, load_json_file
from analyzer.src.halstead import Halstead
from analyzer.src.features import Features


def analyze(repo_count: int) -> Mappings:
    mappings = Mappings()

    analyzed_repos: int = 0
    owners: List[str] = listdir(get_res_path())

    for owner in owners:
        repos: List[str] = listdir(get_res_path(owner=owner))

        for repo in repos:

            if analyzed_repos > repo_count:
                continue

            analyzed_repos += 1

            repo_path: str = get_res_path(owner=owner, repo=repo)
            result_files: List[str] = [f for f in listdir(repo_path) if isfile(join(repo_path, f))]

            for result_file in result_files:
                findings: List[Dict[str, Any]] = load_json_file(join(repo_path, result_file))

                for finding in findings:

                    if finding["tool"] == "rca":
                        feature = Features.get_feature_by_token(finding["identifier"])
                        new: Halstead = Halstead.from_data(finding["data"]["halstead"])

                        mappings.merge(feature, new)
    return mappings
