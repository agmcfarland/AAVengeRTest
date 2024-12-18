from unittest.mock import patch, Mock, call
import pytest
from os.path import join as pjoin
import os
import pandas as pd
from lib.common import CompareResults


@pytest.fixture
def example_compare_results(
    project_test_data_directory, setup_temp_dir, scope="session", autouse=True
):
    results = CompareResults(
        test_results_path=project_test_data_directory,
        expected_results_path=project_test_data_directory,
    )

    return results


def test_init_compare_results(example_compare_results, project_test_data_directory):
    """
    pytest -sv tests/unit/test_CompareResults.py::test_init_compare_results
    """
    assert example_compare_results.results["sites"]["all"] == ""
    assert example_compare_results.results["sites"]["only_different"] == ""
    assert example_compare_results.results["sites"]["raw"] == ""


def test_sites_comparison(example_compare_results, project_test_data_directory):
    """
    pytest -sv tests/unit/test_CompareResults.py::test_sites_comparison
    """

    results = example_compare_results

    df_mock_actual = pd.read_csv(
        pjoin(project_test_data_directory, "ete_expected_site_features.csv")
    )

    df_mock_expected = pd.read_csv(
        pjoin(project_test_data_directory, "ete_expected_site_features_differing.csv")
    )

    with patch("pandas.read_csv") as mock_read_csv:
        mock_read_csv.side_effect = [df_mock_actual, df_mock_expected]

        results.compare_sites()

        assert results.results["sites"]["raw"].shape == (2, 41)

        assert results.results["sites"]["all"].shape == (32, 9)

        assert results.results["sites"]["only_different"].shape == (4, 9)


def test_write_comparisons(example_compare_results, project_test_data_directory):
    """
    pytest -sv tests/unit/test_CompareResults.py::test_write_comparisons
    """

    example_compare_results.results["sites"]["raw"] = pd.DataFrame()
    example_compare_results.results["sites"]["all"] = pd.DataFrame()
    example_compare_results.results["sites"]["only_different"] = pd.DataFrame()

    with patch("pandas.DataFrame.to_csv") as mock_to_csv:
        example_compare_results.write_comparisons()

        expected_calls = [
            (
                pjoin(project_test_data_directory, "sites_raw_comparisons.csv"),
                {"index": None},
            ),
            (
                pjoin(project_test_data_directory, "sites_all_comparisons.csv"),
                {"index": None},
            ),
            (
                pjoin(project_test_data_directory, "sites_difference_comparisons.csv"),
                {"index": None},
            ),
        ]

        mock_to_csv.assert_has_calls(
            [call(args, **kwargs) for args, kwargs in expected_calls]
        )

        # print(mock_to_csv.mock_calls)
        # print(expected_calls)


def test_check_expected_files_exists(project_test_data_directory):
    """
    pytest -sv tests/unit/test_CompareResults.py::test_check_expected_files_exists
    """

    with patch("os.path.exists") as mock_os_path_exists:
        mock_os_path_exists.return_value = True

        CompareResults.check_expected_data_exists("/fake/path")


def test_check_expected_files_does_not_exists(project_test_data_directory):
    """
    pytest -sv tests/unit/test_CompareResults.py::test_check_expected_files_does_not_exists
    """
    with pytest.raises(ValueError) as e_info:
        CompareResults.check_expected_data_exists("/fake/path")
