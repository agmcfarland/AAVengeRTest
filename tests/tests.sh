conda activate AAVengeRTest

cd /data/AAVengeRTest


python -m pytest -sv tests/unit/test_input_manager.py

python -m pytest -sv tests/unit/test_run_handler.py

python -m pytest -sv tests/unit/test_ResultChecker.py

python -m pytest -sv tests/unit/test*

python -m pytest -sv tests


# coverage -m pytest -sv  tests/end_to_end/test_ete2.py::test_run1_and_run2_run3_run4

# coverage run -m pytest -sv tests/test_*.py && coverage report -m

# python -m slipcover -m pytest -sv  tests/end_to_end/test_ete2.py::test_run1_and_run2_run3_run4

# python -m slipcover -m pytest -sv tests/unit/test_*.py

# pytest tests/end_to_end --cov

# pytest tests --cov

AAVengeRTest \
--output_dir /data/aavenger_stability_testing/packaged_test_data \
--test_data_sheet /data/AAVengeRTest/tests/data/ete_correct_input_sheet.csv \
--expected_output_dir /data/aavenger_stability_testing/data/packaged_test_data/expected_results \
--microb120_user agmcfarland \
--docker_image_name aavenger_docker_v3 \
--aavenger_dir /data/AAVengeR \
--docker_source_mount /data \
--docker_target_mount /data






