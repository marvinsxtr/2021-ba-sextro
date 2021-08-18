from genericpath import isdir
import multiprocessing
from os import listdir
from os.path import isfile, join
from typing import Any, Dict, List

from analyzer.src.statistics import Statistics
from analyzer.src.utils import get_res_path, load_json_file, remove_keys, save_json_file
from analyzer.src.metrics import Metrics
from analyzer.src.features import Features
from analyzer.src.tables import Tables
from analyzer.src.experiments import Experiment, Experiments

from tqdm import tqdm


class Analyzer:
    """
    This class contains methods for analyzing the collected metrics on the repositories.
    """

    @staticmethod
    def get_repos(repo_count: int, skip_repos: int) -> Dict[str, List[str]]:
        """
        Returns a dict mapping the repository paths to a list of result files.

        :param repo_count: Number of repositories to get
        :param skip_repos: Number of repositories to skip
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

        return {k: repos[k] for k in list(repos)[skip_repos:repo_count + skip_repos]}

    @staticmethod
    def analyze(
        repo_count: int,
        skip_repos: int,
        analyze_repos: bool,
        statistic_tests: bool,
        generate_tables: bool,
        experiment_names: List[str]
    ) -> None:
        """
        Analyzes a given number of repositories.

        :param repo_count: Number of repositories to analyze
        :param skip_repos: Number of repositories to skip
        :param generate_tables: Whether to generate the latex tables
        :param experiments: The experiments to run on the data
        """
        if analyze_repos:
            Analyzer.analyze_repos(repo_count, skip_repos, experiment_names)

        if statistic_tests:
            Statistics.analyze_results()

        if generate_tables:
            Tables.generate_latex_tables()

    @staticmethod
    def analyze_repos(repo_count: int, skip_repos: int, experiment_names: List[str]) -> None:
        """
        Collects the raw data for each experiment on the dataset.

        :param repo_count: Number of repositories to collect data of
        :param skip_repos: Number of repositories to skip
        """
        init_experiments = Experiments.initialized(experiment_names)
        result_experiments = Experiments.initialized(experiment_names)

        repos: Dict[str, List[str]] = Analyzer.get_repos(repo_count, skip_repos)

        processes = 2 * multiprocessing.cpu_count() + 1
        pool = multiprocessing.Pool(processes=processes)

        with tqdm(total=repo_count) as t:
            for path, files in repos.items():
                repo_result = pool.apply_async(
                    Analyzer.analyze_repo, args=(init_experiments, path, files))

                result_experiments.merge(repo_result.get())
                t.update()

        pool.close()
        pool.join()

        result = result_experiments.as_dict()
        save_json_file(result, get_res_path(tool="analyzer"), name="res_with_raw_values.json")

        filtered_result = remove_keys(result, "values")
        save_json_file(filtered_result, get_res_path(
            tool="analyzer"), name="res_without_raw_values.json")

    @staticmethod
    def analyze_repo(experiments: Experiments, path: str, files: List[str]) -> Experiments:
        """
        Analyzes a repository.

        :param experiments: The experiments to add the results to
        :param path: The path of the repository
        :param files: The list of result files in the repository
        """
        for file in files:
            Analyzer.analyze_file(experiments, path, file)

        return experiments

    @staticmethod
    def analyze_file(experiments: Experiments, path: str, name: str) -> None:
        """
        Analyzes a single result file.

        :param experiments: The experiments to add the results to
        :param path: Path to the result file
        :param name: Name of the result file
        """
        result_file = load_json_file(path, name)
        if not result_file:
            return

        nodes_experiment = experiments.get(Experiment.NODES)
        if nodes_experiment:
            for node in result_file["node"]:
                feature = Features.get_feature_by_token(node["name"])

                if feature is None:
                    continue

                new_node = Metrics(node["data"])
                nodes_experiment.merge_feature(feature, new_node)

        spaces_experiment = experiments.get(Experiment.SPACES)
        if spaces_experiment:
            for feature in Features.as_dict().keys():
                for space in result_file["rca"]:

                    if space["kind"] == "unit":
                        continue

                    is_inside = Analyzer.feature_in_space(feature, result_file["finder"], space)
                    new_space = Metrics(space["data"])

                    if is_inside:
                        spaces_experiment.merge_feature(feature, new_space)
                    else:
                        spaces_experiment.merge_feature("no_" + feature, new_space)

        files_experiment = experiments.get(Experiment.FILES)
        if files_experiment:
            for feature in Features.as_dict().keys():
                for space in result_file["rca"]:
                    if space["kind"] == "unit":
                        new_space = Metrics(space["data"])
                        files_experiment.merge_feature(feature, new_space)

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
