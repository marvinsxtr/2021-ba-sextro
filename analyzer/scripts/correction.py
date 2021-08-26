from analyzer.src.utils import get_analyzer_res_path, load_json_file, save_json_file
from analyzer.src.features import Features
from analyzer.src.metrics import Metric


def bonferroni_correction() -> None:
    """This corrects the p-values by multiplying them with the total number of hypotheses."""
    test_data = load_json_file(get_analyzer_res_path(), "statistic_tests.json")
    if not test_data:
        return

    num_features = len(test_data["spaces"].keys())
    num_metrics = len(test_data["spaces"]["lifetimes"].keys())

    n = num_features * num_metrics

    for feature in Features.as_dict().keys():
        for metric in Metric.as_dict().keys():
            statistic_test = test_data["spaces"][feature][metric]["mann_whitney_u"]
            new_p_value = statistic_test["p_value"] * n
            statistic_test["corrected_p_value"] = new_p_value if new_p_value < 1.0 else 1.0

    save_json_file(test_data, get_analyzer_res_path(), "corrected_statistic_tests.json")


bonferroni_correction()
