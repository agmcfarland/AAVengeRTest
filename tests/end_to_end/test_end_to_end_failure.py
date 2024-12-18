import shutil
import os
from os.path import join as pjoin


def test_fail(setup_temp_dir):
    """
    Test behavior of docker when AAVengeR fails inside of the docker container.
    """

    print(setup_temp_dir)
