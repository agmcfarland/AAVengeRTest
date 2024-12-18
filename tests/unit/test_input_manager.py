import os
import shutil
import pytest
from unittest.mock import patch
from os.path import join as pjoin
import pandas as pd
from lib.common import InputManager


def test_set_working_dir_tree(setup_temp_dir):
    working_dir = setup_temp_dir
    manager = InputManager(
        working_dir, "test_user", "test_docker", "path/to/AAVengeR", None, None
    )

    # Call the private method to set the dir structure
    manager._set_working_dir_tree()

    assert manager.microb120_user == "test_user"
    assert manager.docker_image_name == "test_docker"
    assert manager.raw_dir == pjoin(working_dir, "raw")
    assert manager.processed_dir == pjoin(working_dir, "processed", manager.time_stamp)
    assert manager.record_dir == pjoin(working_dir, "record")
    assert manager.test_results_dir == pjoin(working_dir, "test_results")


def test_make_working_directories(setup_temp_dir):
    working_dir = setup_temp_dir
    manager = InputManager(working_dir, None, None, "path/to/AAVengeR", None, None)
    manager._set_working_dir_tree()

    # Call the private method to create directories
    manager._make_working_directories()

    assert os.path.exists(manager.working_dir)
    assert os.path.exists(manager.raw_dir)
    assert os.path.exists(manager.processed_dir)
    assert os.path.exists(manager.test_results_dir)


def test_delete_raw_dir(setup_temp_dir):
    working_dir = setup_temp_dir
    manager = InputManager(working_dir, None, None, "path/to/AAVengeR", None, None)
    manager._set_working_dir_tree()
    manager._make_working_directories()

    # Ensure raw dir exists before deletion
    assert os.path.exists(manager.raw_dir)

    # Call the private method to delete the raw dir
    manager._delete_raw_dir()

    assert not os.path.exists(manager.raw_dir)


def test_example_input_manager(example_input_manager_read_write):
    """
    pytest -sv tests/unit/test_input_manager.py::test_example_input_manager
    """
    assert os.path.exists(example_input_manager_read_write.working_dir)
    assert os.path.exists(example_input_manager_read_write.raw_dir)
    assert os.path.exists(example_input_manager_read_write.processed_dir)
    assert os.path.exists(example_input_manager_read_write.record_dir)
    assert os.path.exists(example_input_manager_read_write.test_results_dir)


def test_project_test_data_directory(project_test_data_directory):
    """
    pytest -sv tests/unit/test_input_manager.py::test_project_test_data_directory
    """
    assert os.path.exists(project_test_data_directory)


def test_load_test_data_sheet(
    example_input_manager_read_write, project_test_data_directory
):
    """
    pytest -sv tests/unit/test_input_manager.py::test_load_test_data_sheet
    """
    example_input_manager_read_write.load_test_data_sheet(
        pjoin(project_test_data_directory, "ete_correct_input_sheet.csv")
    )

    assert (
        str(type(example_input_manager_read_write.df_test_data))
        == "<class 'pandas.core.frame.DataFrame'>"
    )


def test_validate_test_data_input_sheet(
    example_input_manager_read_write, project_test_data_directory
):
    """
    pytest -sv tests/unit/test_input_manager.py::test_validate_test_data_input_sheet
    """
    example_input_manager_read_write.load_test_data_sheet(
        pjoin(project_test_data_directory, "ete_correct_input_sheet.csv")
    )

    example_input_manager_read_write.validate_sample_sheet_paths()

    example_input_manager_read_write.validate_run_tags()


def test_validate_test_data_input_sheet_errors(
    example_input_manager_read_write, project_test_data_directory
):
    """
    pytest -sv tests/unit/test_input_manager.py::test_validate_test_data_input_sheet_errors
    """
    example_input_manager_read_write.load_test_data_sheet(
        pjoin(project_test_data_directory, "ete_correct_input_sheet.csv")
    )

    with pytest.raises(ValueError) as e_info:
        example_input_manager_read_write.df_test_data["run_tag"] = ["one", "one"]
        example_input_manager_read_write.validate_run_tags()

    with pytest.raises(ValueError) as e_info:
        example_input_manager_read_write.df_test_data["sample_sheet_path"] = [
            "/doesnotexist/here.tsv",
            "/doesnotexist/here.tsv",
        ]
        example_input_manager_read_write.validate_sample_sheet_paths()


def test_validate_test_data_input_sheet(
    example_input_manager_read_write, project_test_data_directory, setup_temp_dir
):
    """
    pytest -sv tests/unit/test_input_manager.py::test_validate_test_data_input_sheet
    """
    example_input_manager_read_write.load_test_data_sheet(
        pjoin(project_test_data_directory, "ete_correct_input_sheet.csv")
    )

    example_input_manager_read_write.validate_sample_sheet_paths()

    example_input_manager_read_write.validate_run_tags()


def test_validate_test_data_record_run(
    example_input_manager_read_write, project_test_data_directory, setup_temp_dir
):
    """
    pytest -sv tests/unit/test_input_manager.py::test_validate_test_data_record_run
    """
    example_input_manager_read_write.load_test_data_sheet(
        pjoin(project_test_data_directory, "ete_correct_input_sheet.csv")
    )

    example_input_manager_read_write.validate_sample_sheet_paths()

    example_input_manager_read_write.validate_run_tags()

    example_input_manager_read_write.record_run_path = setup_temp_dir

    example_input_manager_read_write.aavenger_version = "2.1.1"

    example_input_manager_read_write.record_run()

    assert example_input_manager_read_write.run_record.shape == (2, 11)
