from analyzer.src.statistics import Tests
from os.path import join

from analyzer.src.experiments import Experiment
from analyzer.src.utils import get_res_path, load_json_file
from analyzer.src.features import Features
from analyzer.src.metrics import Metric


class Tables:
    @staticmethod
    def generate_latex_tables() -> None:
        """Generates LaTeX tables from the results."""
        statistics = load_json_file(get_res_path(tool="analyzer"), name="tst.json")
        table_number = 1

        if not statistics:
            return

        for experiment in Experiment.as_dict().keys():
            if not statistics.get(experiment):
                continue

            for test in Tests.as_list():
                for sample_size in ["same_sample_size", "different_sample_size"]:
                    with open(join(get_res_path(tool="analyzer"), f"tables_{experiment}_{test}_{sample_size}.txt"), "w+", encoding="utf-8") as tables:
                        for feature in Features.as_dict().keys():
                            rows = list()
                            for metric in Metric.as_dict().keys():
                                test_results = statistics[experiment][feature][metric].get(
                                    f"{test}_{sample_size}")
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
\\label{{table{3}}}
\\end{{center}}
\\end{{table}}
                            """.format("\n".join(rows), feature, feature, table_number))
