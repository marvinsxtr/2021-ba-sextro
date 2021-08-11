from argparse import Namespace, ArgumentParser

from analyzer.src.analyzer import Analyzer


def main() -> None:
    """Runs the `analyzer` and saves the results."""
    parser = ArgumentParser(description='Analyzer')

    parser.add_argument('-n', '--repo_count', type=int, default=1,
                        help='Number of repos to analyze')
    parser.add_argument('-s', '--skip_repos', type=int, default=0,
                        help='Number of repos to skip')
    parser.add_argument('-t', '--generate_tables', action='store_true',
                        help='Whether to generate LaTeX tables')

    args: Namespace = parser.parse_args()

    repo_count: int = args.repo_count
    skip_repos: int = args.skip_repos
    generate_tables: bool = args.generate_tables

    Analyzer.analyze(repo_count, skip_repos, generate_tables)
