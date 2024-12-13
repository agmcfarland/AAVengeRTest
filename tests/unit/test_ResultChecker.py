from unittest.mock import patch, Mock, call
import pytest
from os.path import join as pjoin
import pandas as pd
from lib.common import RunResultChecker


@pytest.fixture
def example_run_results(project_test_data_directory, scope = 'session', autouse = True):
	run_results = RunResultChecker(
		run_id = 'testrunid', run_tag = 'testruntag',
		time_stamp = '2_4_5_6', working_dir = project_test_data_directory, reference_output_path = ''
		)
	return run_results


def test_intitalize_result_checker(example_run_results):
	"""
	pytest -sv tests/unit/test_ResultChecker.py::test_intitalize_result_checker
	"""
	assert example_run_results.run_id == 'testrunid'

def test_read_in_sites(example_run_results, project_test_data_directory):
	"""
	pytest -sv tests/unit/test_ResultChecker.py::test_read_in_sites
	"""

	test_df = pd.read_excel(pjoin(project_test_data_directory, 'ete_correct_sites.xlsx'))

	with patch('pandas.read_excel') as mock_read_excel:

		mock_read_excel.return_value = test_df

		example_run_results._read_in_sites()

	assert str(type(example_run_results.sites) == "<class 'pandas.core.frame.DataFrame'>")

	assert example_run_results.sites.shape == (40, 30)

	assert example_run_results.sites_exist == True

def test_read_in_sites_not_exist(example_run_results):
	"""
	pytest -sv tests/unit/test_ResultChecker.py::test_read_in_sites_not_exist
	"""
	example_run_results.output_dir = '/path/doesntexist'

	example_run_results._read_in_sites()

	assert str(type(example_run_results.sites) == "<class 'pandas.core.frame.DataFrame'>")

	assert example_run_results.sites_exist == False


def test_characterize_site_features(example_run_results, project_test_data_directory):
	"""
	pytest -sv tests/unit/test_ResultChecker.py::test_characterize_site_features
	"""

	test_df = pd.read_excel(pjoin(project_test_data_directory, 'ete_correct_sites.xlsx'))

	with patch('pandas.read_excel') as mock_read_excel:

		mock_read_excel.return_value = test_df

		example_run_results._read_in_sites()


	example_run_results.characterize_sites_features()

	assert example_run_results.site_features == {'file_detected': True, 'n_subject': 1, 'n_sample': 1, 'n_refGenome': 1, 'n_posid': 40, 'n_vector': 1, 'n_repeat_name': 13, 'n_repeat_class': 7, 'n_nearestGene': 40, 'sum_sonicLengths': 42, 'sum_reads': 52, 'sum_nRepsObs': 40, 'sum_inGene': 31, 'sum_inExon': 2}


def test_characterize_site_features_no_sites_table_found(example_run_results):
	"""
	pytest -sv tests/unit/test_ResultChecker.py::test_characterize_site_features_no_sites_table_found
	"""
	example_run_results._read_in_sites()

	example_run_results.characterize_sites_features()

	assert example_run_results.site_features == {'file_detected': False, 'n_subject': 0, 'n_sample': 0, 'n_refGenome': 0, 'n_posid': 0, 'n_vector': 0, 'n_repeat_name': 0, 'n_repeat_class': 0, 'n_nearestGene': 0, 'sum_sonicLengths': 0, 'sum_reads': 0, 'sum_nRepsObs': 0, 'sum_inGene': 0, 'sum_inExon': 0}
























