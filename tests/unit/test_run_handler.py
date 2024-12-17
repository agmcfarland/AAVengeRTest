from unittest.mock import patch, Mock, call
import pytest
from os.path import join as pjoin
import os
from lib.common import InputManager, RunHandler
from pathlib import Path


def test_run_handler_initialization(mocked_input_manager, example_run_handler):
	"""
	pytest -sv tests/unit/test_run_handler.py::test_run_handler_initialization
	"""

	# Initialize run_handler with mocked_input_manager
	handler = example_run_handler

	# Assertions to ensure properties are correctly set
	assert handler.input_manager.working_dir == 'test_working_dir'
	assert handler.run_id == "test_run"
	assert handler.random_seed_value == 42
	assert handler.number_of_reads == 1000
	assert handler.config_preset == "integrase"
	assert handler.input_manager.raw_dir == 'test_working_dir/raw'
	# This is created when run_handler is inititated
	assert handler.read_files['R1']['raw'] == 'Undetermined_S0_R1_001.fastq.gz'
	assert handler.read_files['R2']['raw'] == 'Undetermined_S0_R2_001.fastq.gz'
	assert handler.read_files['I1']['raw'] == 'Undetermined_S0_I1_001.fastq.gz'

	assert handler.run_tag == 'example_run_tag'

	assert str(type(handler.sample_sheet)) == "<class 'pandas.core.frame.DataFrame'>"


@patch('os.system')
def test_scp_pull_from_microb120(mock_os_system, mocked_input_manager, example_run_handler):
	"""
	pytest -sv tests/unit/test_run_handler.py::test_scp_pull_from_microb120
	"""
	handler = example_run_handler

	handler.pull_sequencing_run()

	expected_calls = [
		(
			call("scp test_user@microb120.med.upenn.edu:/media/sequencing/Illumina/test_run/Data/Intensities/BaseCalls/Undetermined_S0_R1_001.fastq.gz test_working_dir/raw")
		),
		(
			call("scp test_user@microb120.med.upenn.edu:/media/sequencing/Illumina/test_run/Data/Intensities/BaseCalls/Undetermined_S0_R2_001.fastq.gz test_working_dir/raw")
		),
		(
			call("scp test_user@microb120.med.upenn.edu:/media/sequencing/Illumina/test_run/Data/Intensities/BaseCalls/Undetermined_S0_I1_001.fastq.gz test_working_dir/raw")
		)
	]

	assert mock_os_system.call_count == 3

	mock_os_system.assert_has_calls([call for call in expected_calls], any_order = False)


@patch('os.system')
def test_reformat_reads(mock_os_system, mocked_input_manager, example_run_handler):
	"""
	pytest -sv tests/unit/test_run_handler.py::test_reformat_reads
	"""

	handler = example_run_handler

	handler.downsample_reads()

	assert mock_os_system.call_count == 3

	expected_calls = [
		(
			call("reformat.sh in=test_working_dir/raw/Undetermined_S0_R1_001.fastq.gz out=test_working_dir/raw/downsampled_Undetermined_S0_R1_001.fastq.gz reads=1000 ow=t sampleseed=42")
		),
		(
			call("reformat.sh in=test_working_dir/raw/Undetermined_S0_R2_001.fastq.gz out=test_working_dir/raw/downsampled_Undetermined_S0_R2_001.fastq.gz reads=1000 ow=t sampleseed=42")
		),
		(
			call("reformat.sh in=test_working_dir/raw/Undetermined_S0_I1_001.fastq.gz out=test_working_dir/raw/downsampled_Undetermined_S0_I1_001.fastq.gz reads=1000 ow=t sampleseed=42")
		),
		]

	mock_os_system.assert_has_calls([call for call in expected_calls], any_order = False)


def test_write_sample_sheet(example_run_handler_read_write):
	"""
	pytest -sv tests/unit/test_run_handler.py::test_write_sample_sheet
	"""
	example_run_handler_read_write.write_sample_sheet()
	assert os.path.exists(pjoin(example_run_handler_read_write.input_manager.raw_dir, 'sample_sheet.tsv'))


def test_make_config_file_integrase(example_run_handler_read_write, project_test_data_directory):
	"""
	pytest -sv tests/unit/test_run_handler.py::test_make_config_file_integrase
	"""

	example_run_handler_read_write.input_manager.aavenger_dir = project_test_data_directory

	# This will happen after
	
	example_run_handler_read_write.read_files['R1']['downsampled'] = 'Undetermined_S0_R1_001.fastq.gz'
	
	example_run_handler_read_write.read_files['R2']['downsampled'] = 'Undetermined_S0_R2_001.fastq.gz'
	
	example_run_handler_read_write.read_files['I1']['downsampled'] = 'Undetermined_S0_I1_001.fastq.gz'	


	example_run_handler_read_write.make_config_file()

	with open(example_run_handler_read_write.config_path, 'r') as infile:
		for l in infile:
			if l.startswith('mode: '):
				assert l == 'mode: integrase\n'

			if l.startswith('core_CPUs'):
				assert l == f"core_CPUs: {example_run_handler_read_write.n_cpus} # 15\n"

			if l.startswith('outputDir'):
				assert l == f"outputDir: {example_run_handler_read_write.aavenger_output_dir}\n"

			if l.startswith('softwareDir'):
				assert l == f'softwareDir: {example_run_handler_read_write.input_manager.aavenger_dir}\n'

			if l.startswith('sequencingRunID'):
				assert l == f"sequencingRunID: {example_run_handler_read_write.stamped_run_id}\n"

			if l.startswith('demultiplex_anchorReadsFile'):
				assert l == f"demultiplex_anchorReadsFile: {pjoin(example_run_handler_read_write.input_manager.raw_dir, example_run_handler_read_write.read_files['R2']['downsampled'])}\n"

			if l.startswith('demultiplex_adriftReadsFile'):
				assert l == f"demultiplex_adriftReadsFile: {pjoin(example_run_handler_read_write.input_manager.raw_dir, example_run_handler_read_write.read_files['R1']['downsampled'])}\n"

			if l.startswith('demultiplex_index1ReadsFile'):
				assert l == f"demultiplex_index1ReadsFile: {pjoin(example_run_handler_read_write.input_manager.raw_dir, example_run_handler_read_write.read_files['I1']['downsampled'])}\n"

			if l.startswith('demultiplex_sampleDataFile'):
				assert l == f"demultiplex_sampleDataFile: {pjoin(example_run_handler_read_write.input_manager.raw_dir, 'sample_sheet.tsv')}\n"
			
			if l.startswith('buildStdFragments_createMultiHitClusters'):
				assert l == f"buildStdFragments_createMultiHitClusters: True\n"

def test_make_config_file_aav(example_run_handler_read_write, project_test_data_directory):
	"""
	pytest -sv tests/unit/test_run_handler.py::test_make_config_file_aav
	"""

	example_run_handler_read_write.input_manager.aavenger_dir = project_test_data_directory

	# This will happen after
	
	example_run_handler_read_write.read_files['R1']['downsampled'] = 'Undetermined_S0_R1_001.fastq.gz'
	
	example_run_handler_read_write.read_files['R2']['downsampled'] = 'Undetermined_S0_R2_001.fastq.gz'
	
	example_run_handler_read_write.read_files['I1']['downsampled'] = 'Undetermined_S0_I1_001.fastq.gz'	

	example_run_handler_read_write.config_preset = 'AAV'

	example_run_handler_read_write.make_config_file()

	with open(example_run_handler_read_write.config_path, 'r') as infile:
		for l in infile:
			if l.startswith('mode: '):
				assert l == 'mode: AAV\n'

			if l.startswith('core_CPUs'):
				assert l == f"core_CPUs: {example_run_handler_read_write.n_cpus} # 15\n"

			if l.startswith('outputDir'):
				assert l == f"outputDir: {example_run_handler_read_write.aavenger_output_dir}\n"

			if l.startswith('softwareDir'):
				assert l == f'softwareDir: {example_run_handler_read_write.input_manager.aavenger_dir}\n'

			if l.startswith('sequencingRunID'):
				assert l == f"sequencingRunID: {example_run_handler_read_write.stamped_run_id}\n"

			if l.startswith('demultiplex_anchorReadsFile'):
				assert l == f"demultiplex_anchorReadsFile: {pjoin(example_run_handler_read_write.input_manager.raw_dir, example_run_handler_read_write.read_files['R2']['downsampled'])}\n"

			if l.startswith('demultiplex_adriftReadsFile'):
				assert l == f"demultiplex_adriftReadsFile: {pjoin(example_run_handler_read_write.input_manager.raw_dir, example_run_handler_read_write.read_files['R1']['downsampled'])}\n"

			if l.startswith('demultiplex_index1ReadsFile'):
				assert l == f"demultiplex_index1ReadsFile: {pjoin(example_run_handler_read_write.input_manager.raw_dir, example_run_handler_read_write.read_files['I1']['downsampled'])}\n"

			if l.startswith('demultiplex_sampleDataFile'):
				assert l == f"demultiplex_sampleDataFile: {pjoin(example_run_handler_read_write.input_manager.raw_dir, 'sample_sheet.tsv')}\n"
			
			if l.startswith('buildStdFragments_createMultiHitClusters'):
				assert l == f"buildStdFragments_createMultiHitClusters: True\n"












