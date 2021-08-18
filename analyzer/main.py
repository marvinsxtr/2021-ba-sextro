from argparse import Namespace, ArgumentParser
from typing import List

from analyzer.src.analyzer import Analyzer


def main() -> None:
    """Runs the `analyzer` and saves the results."""
    parser = ArgumentParser(description='Analyzer')

    parser.add_argument('-n', '--repo_count', type=int, default=1,
                        help='Number of repos to analyze')
    parser.add_argument('-s', '--skip_repos', type=int, default=0,
                        help='Number of repos to skip')
    parser.add_argument('-a', '--analyze_repos', action='store_true',
                        help='Whether to analyze the repositories')
    parser.add_argument('-t', '--statistic_tests', action='store_true',
                        help='Whether to conduct the statistical tests')
    parser.add_argument('-g', '--generate_tables', action='store_true',
                        help='Whether to generate LaTeX tables')
    parser.add_argument('-e', '--experiment_names', type=str, default="nodes,spaces,files",
                        help='Which experiments to run')

    args: Namespace = parser.parse_args()

    repo_count: int = args.repo_count
    skip_repos: int = args.skip_repos
    analyze_repos: bool = args.analyze_repos
    statistic_tests: bool = args.statistic_tests
    generate_tables: bool = args.generate_tables
    experiment_names: List[str] = args.experiment_names.split(",")

    Analyzer.analyze(repo_count, skip_repos, analyze_repos,
                     statistic_tests, generate_tables, experiment_names)
