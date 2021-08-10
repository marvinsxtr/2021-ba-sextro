from genericpath import isdir
from analyzer.src.statistics import Statistics
from os import listdir
from os.path import isfile, join
from typing import Any, Dict, List

from analyzer.src.mapping import Mapping
from analyzer.src.utils import get_res_path, load_json_file, save_json_file
from analyzer.src.metrics import Metrics
from analyzer.src.features import Features
from analyzer.src.tables import generate_latex_tables


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
            owner_path = get_res_path(owner=owner)
            if isdir(owner_path):
                owned_repos: List[str] = listdir(owner_path)

                for owned_repo in owned_repos:
                    repo_path: str = get_res_path(owner=owner, repo=owned_repo)
                    if isdir(repo_path):
                        repos[repo_path] = [f for f in listdir(
                            repo_path) if isfile(join(repo_path, f))]

        return {k: repos[k] for k in list(repos)[:repo_count]}

    @staticmethod
    def get_experiments() -> Dict[str, Mapping]:
        """
        Returns the initialized values for different experiments.

        :return: The initialized experiment values.
        """
        node_experiment = Mapping({k: Metrics(None) for k in Features.as_dict().keys()})

        double_features = [val for val in Features.as_dict().keys() for _ in (0, 1)]
        space_experiment = Mapping({k if i % 2 else "no_" + k: Metrics(None)
                                    for i, k in enumerate(double_features)})

        return {
            "nodes": node_experiment,
            "spaces": space_experiment
        }

    @staticmethod
    def analyze(repo_count: int, generate_tables: bool) -> None:
        """
        Analyzes a given number of repositories.

        :param repo_count: Number of repositories to analyze
        :param generate_tables: Whether to generate the latex tables
        """
        experiments = Analyzer.get_experiments()
        repos: Dict[str, List[str]] = Analyzer.get_repos(repo_count)

        for repo_path, result_files in repos.items():
            for result_file in result_files:
                Analyzer.analyze_file(experiments, repo_path, result_file)

        result = {k: v.as_dict() for k, v in experiments.items()}
        save_json_file(result, get_res_path(tool="analyzer"), name="res.json")

        Statistics.analyze(result)

        if generate_tables:
            generate_latex_tables()

    @staticmethod
    def analyze_file(mappings: Dict[str, Mapping], path: str, name: str) -> None:
        """
        Analyzes a single result file.

        :param mappings: The mappings to apply the results to
        :param path: Path to the result file
        :param name: Name of the result file
        """
        result_file = load_json_file(path, name)
        if not result_file:
            return

        for node in result_file["node"]:
            feature = Features.get_feature_by_token(node["name"])

            if feature is None:
                continue

            new_node = Metrics(node["data"])
            mappings["nodes"].merge(feature, new_node)

        for feature in Features.as_dict().keys():
            for space in result_file["rca"]:

                if space["kind"] == "unit":
                    continue

                is_inside = Analyzer.feature_in_space(feature, result_file["finder"], space)
                new_space = Metrics(space["data"])

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
            if Features.get_feature_by_token(finding["name"]) == feature and \
                    finding["start_line"] >= space["start_line"] and \
                    finding["end_line"] <= space["end_line"]:
                return True
        return False
