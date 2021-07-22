import json
from os import listdir
from os.path import isfile, join
from typing import Any, Dict, List

from analyzer.src.mapping import Mapping
from analyzer.src.utils import get_res_path, load_json_file
from analyzer.src.halstead import Halstead
from analyzer.src.features import Features


class Analyzer:
    """
    This class contains methods for analyzing the collected metrics on the repositories.
    """

    @staticmethod
    def get_repos(repo_count: int) -> Dict[str, List[str]]:
        """
        Returns a dict mapping the repository paths to a list of result files.

        :param repo_count: Number of repositories to get
        :return: Dict mapping repository paths to result files
        """
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
        """
        Returns the initialized mappings for different experiments.

        :return: The initialized mappings.
        """
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
        """
        Analyzes a given number of repositories.

        :param repo_count: Number of repositories to analyze
        :returns: The mappings for each experiment with the final data
        """
        mappings = Analyzer.get_mappings()

        repos: Dict[str, List[str]] = Analyzer.get_repos(repo_count)

        for repo_path, result_files in repos.items():
            for result_file in result_files:
                file_path = join(repo_path, result_file)
                Analyzer.analyze_file(mappings, file_path)

        return mappings

    @staticmethod
    def analyze_file(mappings: Dict[str, Mapping], file_path: str) -> None:
        """
        Analyzes a single result file.

        :param mappings: The mappings to apply the results to
        :param file_path: Path to the result file
        """
        result_file: Dict[str, Any] = load_json_file(file_path)

        for node in result_file["node"]:
            feature = Features.get_feature_by_token(node["name"])

            if feature is None:
                continue

            new_node: Halstead = Halstead.from_data(node["data"]["halstead"])
            mappings["nodes"].merge(feature, new_node)

        for feature in Features.as_dict().keys():
            for space in result_file["rca"]:

                if space["kind"] == "unit":
                    continue

                is_inside = Analyzer.feature_in_space(feature, result_file["finder"], space)
                new_space = Halstead.from_data(space["data"]["halstead"])

                if is_inside:
                    mappings["spaces"].merge(feature, new_space)
                else:
                    mappings["spaces"].merge("no_" + feature, new_space)

    @staticmethod
    def feature_in_space(
        feature: str,
        findings: List[Dict[str, Any]],
        space: Dict[str, Any]
    ) -> bool:
        """
        :param feature: Name of the feature to look for
        :param findings: List of findings in the file
        :param space: Dict of the space to be searched

        :return: Whether or not the feature could be found in the given space
        """
        for finding in findings:
            # size_ratio = (finding["end_line"] - finding["start_line"] + 1) \
            #     / (space["end_line"] - space["start_line"] + 1)
            # if size_ratio < 0.1:
            #     continue

            if Features.get_feature_by_token(finding["name"]) == feature and \
                    finding["start_line"] >= space["start_line"] and \
                    finding["end_line"] <= space["end_line"]:
                return True
        return False
