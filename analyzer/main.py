import json
from argparse import Namespace, ArgumentParser
from typing import Dict

from analyzer.src.mapping import Mapping
from analyzer.src.analyzer import Analyzer


def main() -> None:
    """Runs the `analyzer` and prints the results."""
    parser = ArgumentParser(description='Analyzer')
    parser.add_argument('-n', '--repo_count', type=int, default=1,
                        help='Number of repos to analyze')

    args: Namespace = parser.parse_args()
    repo_count: int = args.repo_count

    mappings: Dict[str, Mapping] = Analyzer.analyze(repo_count)

    print(json.dumps({k: v.avg() for k, v in mappings.items()}, indent=4))
