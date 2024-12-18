from unittest.mock import patch, Mock, call
import pytest
from os.path import join as pjoin
from lib.common import RunHandler, AAVengeRDockerRunner


def test_initalize_aavenger_test(example_run_handler_read_write):
    """
    pytest -sv tests/unit/test_aavenger_test.py::test_initalize_aavenger_test
    """

    example_run_handler_read_write.config_path = pjoin(
        example_run_handler_read_write.input_manager.raw_dir, "config.yml"
    )

    aavenger_run = AAVengeRDockerRunner(run_handler=example_run_handler_read_write)

    assert True
