from typing import Any, Dict
from analyzer.src.statistics import Tests
from os.path import join

from analyzer.src.experiments import Experiment
from analyzer.src.utils import get_res_path, load_json_file
from analyzer.src.features import Features
from analyzer.src.metrics import Metric


class Tables:
    @staticmethod
    def generate_tables() -> None:
        """Generates LaTeX tables from the results."""
        statistics = load_json_file(get_res_path(tool="analyzer"), name="statistic_tests.json")
        if not statistics:
            return

        for experiment in Experiment.as_dict().keys():
            if not statistics.get(experiment):
                continue

            for test in Tests.as_list():

                Tables.generate_table(statistics, experiment, test,)

    @staticmethod
    def generate_table(statistics: Dict[str, Any], experiment: str, test: str) -> None:
        """
        Generate a table file for one feature.

        :param statistics: The content of the staticstics file
        :param experiment: Experiment name
        :param test: Name of the statistic test
        """
        with open(join(get_res_path(tool="analyzer"), f"tables_{experiment}_{test}.txt"), "w+", encoding="utf-8") as tables:
            for feature in Features.as_dict().keys():
                rows = list()
                for metric in Metric.as_dict().keys():
                    test_results = statistics[experiment][feature][metric].get(test)
                    if not test_results:
                        continue

                    pvalue = test_results["p_value"]
                    rejected = "Rejected" if pvalue < 0.05 else "Not rejected"

                    significance = "-"
                    if pvalue < 0.1:
                        significance = "."
                    if pvalue < 0.05:
                        significance = "*"
                    if pvalue < 0.01:
                        significance = "**"
                    if pvalue < 0.001:
                        significance = "***"

                    metric = metric.replace("_", "\_")

                    if pvalue < 0.0001:
                        pvalue = "{:0.5e}".format(pvalue)
                    else:
                        pvalue = round(pvalue, 5)

                    rows.append(
                        f"$H0_{{\\textrm{{{feature}, {metric}}}}}$ & ${pvalue}$ & {rejected} & ${significance}$ \\\\")

                tables.write("""
\\begin{{table}}
\\begin{{center}}
\\begin{{tabular}}{{ l l l l l }}
\\toprule
\\textbf{{Name}} & \\textbf{{p-value}} & \\textbf{{Decision}} & \\textbf{{Significance}} \\\\ 
\\midrule
{0}
\\end{{tabular}}
\\caption[Significance and p-values for the feature "{1}" in code spaces]{{$H0$: No significant difference in each metric between code spaces with feature usage and without. Significance and p-value for the feature "{2}" obtained by applying a Mann-Whitney U test.  (Significance codes: 0 "***" 0.001 "**" 0.01 "*" 0.05 "." 0.1 "–" 1)}}
\\label{{tab:{3}_{4}}}
\\end{{center}}
\\end{{table}}
                    """.format("\n".join(rows), feature, feature, feature, metric))
