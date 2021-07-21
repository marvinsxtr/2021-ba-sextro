import json
from os import listdir
from os.path import isfile, join
from typing import Any, Dict, List

from analyzer.src.mapping import Mapping
from analyzer.src.utils import get_res_path, load_json_file
from analyzer.src.halstead import Halstead
from analyzer.src.features import Features


class Analyzer:
    @staticmethod
    def get_repos(repo_count: int) -> Dict[str, List[str]]:
        owners: List[str] = listdir(get_res_path())
        repos: Dict[str, List[str]] = dict()

        for owner in owners:
            owned_repos: List[str] = listdir(get_res_path(owner=owner))

            for owned_repo in owned_repos:
                repo_path: str = get_res_path(owner=owner, repo=owned_repo)
                repos[repo_path] = [f for f in listdir(repo_path) if isfile(join(repo_path, f))]

        return {k: repos[k] for k in list(repos)[:repo_count]}

    @staticmethod
    def get_mappings() -> Dict[str, Mapping]:
        node_mappings = Mapping({k: Halstead() for k in Features.as_dict().keys()})

        double_features = [val for val in Features.as_dict().keys() for _ in (0, 1)]
        space_mappings = Mapping({k if i % 2 else "no_" + k: Halstead()
                                  for i, k in enumerate(double_features)})

        return {
            "nodes": node_mappings,
            "spaces": space_mappings
        }

    @staticmethod
    def analyze(repo_count: int) -> Dict[str, Mapping]:
        mappings = Analyzer.get_mappings()

        repos: Dict[str, List[str]] = Analyzer.get_repos(repo_count)

        for repo_path, result_files in repos.items():
            for result_file in result_files:
                file_path = join(repo_path, result_file)
                Analyzer.analyze_file(mappings, file_path)

        return mappings

    @staticmethod
    def analyze_file(mappings: Dict[str, Mapping], file_path: str) -> None:
        result_file: Dict[str, Any] = load_json_file(file_path)

        for node in result_file["node"]:
            feature = Features.get_feature_by_token(node["name"])

            if feature is None:
                continue

            new_node: Halstead = Halstead.from_data(node["data"]["halstead"])
            mappings["nodes"].merge(feature, new_node)

        for space in result_file["rca"]:

            if space["kind"] == "unit":
                continue

            for finding in result_file["finder"]:

                feature = Features.get_feature_by_token(finding["name"])
                new_space: Halstead

                if feature is None:
                    continue

                # size_ratio = (finding["end_line"] - finding["start_line"] + 1) \
                #     / (space["end_line"] - space["start_line"] + 1)
                # if size_ratio < 0.1:
                #     continue

                if finding["start_line"] >= space["start_line"] and \
                        finding["end_line"] <= space["end_line"]:

                    new_space = Halstead.from_data(space["data"]["halstead"])
                    mappings["spaces"].merge(feature, new_space)

                if finding["end_line"] < space["start_line"] or \
                        finding["start_line"] > space["end_line"]:
                    new_space = Halstead.from_data(space["data"]["halstead"])
                    mappings["spaces"].merge("no_" + feature, new_space)
