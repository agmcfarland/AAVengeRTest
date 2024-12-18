import sys
import shutil
from os.path import join as pjoin
import os
import pandas as pd
from lib.utils import make_time_stamp, parse_cli_arguments, Logger
from lib.common import (
    InputManager,
    RunHandler,
    AAVengeRDockerRunner,
    RunResultChecker,
    CompareResults,
)
from unittest.mock import Mock


def main():
    args = parse_cli_arguments()

    # args = Mock()
    # args.output_dir = '/data/aavenger_stability_testing'

    # args.test_data_sheet = '/data/AAVengeRTest/tests/data/ete_incorrect_input_sheet.csv'
    # args.test_data_sheet = '/data/AAVengeRTest/tests/data/ete_correct_input_sheet.csv'
    # args.test_data_sheet = '/data/aavenger_stability_testing/data/testing_input_1.csv'

    # args.expected_output_dir = '/data/aavenger_stability_testing/data/packaged_test_data/expected_results'

    # args.microb120_user = 'agmcfarland'
    # args.docker_image_name = 'aavenger_docker_v3'
    # args.aavenger_dir = '/data/AAVengeR'
    # args.docker_source_mount = '/data'
    # args.docker_target_mount = '/data'

    global_input_parameters = InputManager(
        working_dir=pjoin(args.output_dir, "AAVengeRTest_output"),
        microb120_user=args.microb120_user,
        docker_image_name=args.docker_image_name,
        aavenger_dir=args.aavenger_dir,
        source_mount=args.docker_source_mount,
        target_mount=args.docker_target_mount,
    )

    if args.expected_output_dir != "":
        CompareResults.check_expected_data_exists(args.expected_output_dir)

    with Logger(
        time_stamp=global_input_parameters.time_stamp,
        log_dir=pjoin(args.output_dir, "AAVengeRTest_log"),
        log_file="AAVengerTest",
    ) as logger:
        global_input_parameters._set_working_dir_tree()

        global_input_parameters._make_working_directories()

        logger.info(f"AAVengeRTest")

        logger.info("Arguments parsed:")

        logger.info(args)

        global_input_parameters.load_test_data_sheet(
            test_data_sheet_path=args.test_data_sheet
        )

        global_input_parameters.validate_sample_sheet_paths()

        global_input_parameters.validate_run_tags()

        global_input_parameters.get_aavenger_version()

        global_input_parameters.record_run()

        for _, run_ in global_input_parameters.df_test_data.iterrows():
            logger.info(f"Starting new run")

            logger.info(f"Run info: {run_}")

            global_input_parameters._delete_raw_dir()

            global_input_parameters._make_working_directories()

            test_run_handler = RunHandler(
                input_manager=global_input_parameters,
                run_id=run_.run_id,
                random_seed_value=run_.random_seed_value,
                number_of_reads=run_.number_of_reads,
                n_cpus=run_.n_CPUs,
                config_preset=run_.config_preset,
                sample_sheet_path=run_.sample_sheet_path,
                run_tag=run_.run_tag,
            )

            test_run_handler.write_sample_sheet()

            logger.info(f"{test_run_handler.input_manager.__dict__}")

            test_run_handler.pull_sequencing_run()

            test_run_handler.downsample_reads()

            test_run_handler.make_config_file()

            logger.info(f"Starting test")

            logger.info(f"{test_run_handler.__dict__}")

            docker_client = AAVengeRDockerRunner(run_handler=test_run_handler)

            try:
                docker_client.run()

            except:
                logger.debug(f"Failed on {run_}")
                break

            logger.info(f"Finished test")

        # Calculate values for all tested features
        # global_input_parameters.time_stamp = '2024_12_12_10_11_27' # troubleshooting
        # global_input_parameters._set_working_dir_tree() # troubleshooting
        # global_input_parameters._make_working_directories() # troubleshooting
        logger.info(f"Extracting run results")

        global_input_parameters.set_record_run_path()

        df_record = pd.read_csv(global_input_parameters.record_run_path)

        df_site_results = pd.DataFrame()

        for _, record_row_ in df_record.iterrows():
            run_result = RunResultChecker(record_row=record_row_)

            run_result.make_test_results_dir()

            run_result._read_in_sites()

            run_result.characterize_sites_features()

            df_site_results = pd.concat(
                [df_site_results, run_result.make_sites_df()], axis=0
            )

        df_site_results.to_csv(
            pjoin(run_result.test_results_dir, "site_features.csv"), index=None
        )

        # Compare results
        # run_result = Mock  # troublshooting
        # run_result.test_results_dir = '/data/aavenger_stability_testing/packaged_test_data/AAVengeRTest_output/test_results/2024_12_16_14_47_51' # troublshooting
        if args.expected_output_dir != "":
            logger.info(f"Comparing run results to expected values")

            result_comparison = CompareResults(
                test_results_path=run_result.test_results_dir,
                expected_results_path=args.expected_output_dir,
            )

            result_comparison.compare_sites()

            result_comparison.write_comparisons()

            print(f"Test results stored in {run_result.test_results_dir}")

        logger.info(f"Finished AAVengeRTest")


if __name__ == "__main__":
    main()
