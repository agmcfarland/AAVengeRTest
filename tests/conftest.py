from unittest.mock import Mock
from os.path import join as pjoin
import pytest
import os
import pathlib
from lib.common import RunHandler, InputManager


@pytest.fixture
def setup_temp_dir(tmp_path, scope="session", autouse=True):
    """
    Fixture to set up a temporary dir for testing.
    """
    temp_dir = tmp_path / "test_dir"
    temp_dir.mkdir()
    return temp_dir


@pytest.fixture
def mocked_input_manager(scope="session", autouse=True):
    mock_input_manager = Mock()
    mock_input_manager.working_dir = "test_working_dir"
    mock_input_manager.microb120_user = "test_user"
    mock_input_manager.docker_image_name = "test_docker"
    mock_input_manager.aavenger_dir = "test_aavenger"
    mock_input_manager.source_mount = "/path/to/target"
    mock_input_manager.target_mount = "/data"
    mock_input_manager.processed_dir = pjoin(
        mock_input_manager.working_dir, "processed"
    )
    mock_input_manager.raw_dir = pjoin(mock_input_manager.working_dir, "raw")

    return mock_input_manager


@pytest.fixture
def example_run_handler(mocked_input_manager, scope="session", autouse=True):
    handler = RunHandler(
        input_manager=mocked_input_manager,
        run_id="test_run",
        random_seed_value=42,
        number_of_reads=1000,
        config_preset="integrase",
        sample_sheet_path=pathlib.Path(__file__).parent
        / "data"
        / "CompletedSampleSheet.tsv",
        n_cpus=8,
        run_tag="example_run_tag",
    )
    return handler


@pytest.fixture
def example_input_test_sheet(scope="session", autouse=True):
    return pd.DataFrame(
        {
            "run_id": ["runid1", "runid2"],
            "random_seed_value": [3, 4],
            "number_of_reads": [3000, 4000],
            "config_preset": ["integrase", "integrase"],
            "sample_sheet_path": [
                "/path/to/sample_sheet1.tsv",
                "/path/to/sample_sheet2.tsv",
            ],
            "n_CPUs": [8, 8],
            "run_tag": ["runtag1", "runtag2"],
            "reference_output": [],
        }
    )


@pytest.fixture
def example_input_manager_read_write(setup_temp_dir, scope="session", autouse=True):
    """
    Real file structure set up
    """
    example_input_manager = InputManager(
        working_dir=setup_temp_dir,
        microb120_user="test_user",
        docker_image_name="test_docker",
        aavenger_dir="test_aavenger",
        source_mount="/path/to/target",
        target_mount="/data",
    )

    example_input_manager._set_working_dir_tree()

    example_input_manager._make_working_directories()

    return example_input_manager


@pytest.fixture
def example_run_handler_read_write(
    example_input_manager_read_write, scope="session", autouse=True
):
    """
    Real file structure set up
    """
    handler = RunHandler(
        input_manager=example_input_manager_read_write,
        run_id="test_run",
        random_seed_value=42,
        number_of_reads=1000,
        config_preset="integrase",
        sample_sheet_path=pathlib.Path(__file__).parent
        / "data"
        / "CompletedSampleSheet.tsv",
        n_cpus=8,
        run_tag="example_run_tag",
    )
    return handler


@pytest.fixture
def project_test_data_directory(scope="session", autouse=True):
    return pathlib.Path(__file__).parent / "data"


# @pytest.fixture
# def example_aavenger_base_config_file(scope = 'session', autouse = True):
#
