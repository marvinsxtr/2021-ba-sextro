import argparse

from analyzer.src.analyzer import analyze


def main():
  parser = argparse.ArgumentParser(description='Analyzer')
  parser.add_argument('-n', '--repo_count', type=int, default=1, help='Number of repos to analyze')

  args = parser.parse_args()

  repo_count = args.repo_count

  analyze(repo_count)
