from argparse import Namespace, ArgumentParser
from typing import Dict
from os.path import join

from analyzer.src.utils import get_res_path, save_json_file
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
    result = {k: v.as_dict() for k, v in mappings.items()}

    save_json_file(result, get_res_path(tool="analyzer"), name="res.json")
