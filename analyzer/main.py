import json
from argparse import Namespace, ArgumentParser

from analyzer.src.mappings import Mappings
from analyzer.src.analyzer import analyze


def main() -> None:
    parser = ArgumentParser(description='Analyzer')
    parser.add_argument('-n', '--repo_count', type=int, default=1,
                        help='Number of repos to analyze')

    args: Namespace = parser.parse_args()

    repo_count: int = args.repo_count

    mappings: Mappings = analyze(repo_count)

    print(json.dumps(mappings.avg(), indent=4))
