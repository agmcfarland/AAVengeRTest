import docker
import shutil
import os
import pandas as pd
from os.path import join as pjoin
from lib.utils import make_time_stamp, make_stamped_run_id


class InputManager:
    """
    Class for data that is used by all runs. Purpose is to consolidate and check all inputs that will
    be used by all runs.
    """

    def __init__(
        self,
        working_dir,
        microb120_user,
        docker_image_name,
        aavenger_dir,
        source_mount,
        target_mount="/data",
    ):
        """
        target_mount default is /data because that is the name of the internal directory in the AAVengeR docker.
        """
        self.working_dir = working_dir

        self.aavenger_dir = aavenger_dir

        self.target_mount = target_mount

        self.source_mount = source_mount

        self.microb120_user = microb120_user

        self.docker_image_name = docker_image_name

        self.aavenger_config_path = pjoin(self.aavenger_dir)

        self.time_stamp = make_time_stamp()

    def _set_working_dir_tree(self):
        self.raw_dir = pjoin(self.working_dir, "raw")
        self.processed_dir = pjoin(self.working_dir, "processed", self.time_stamp)
        self.record_dir = pjoin(self.working_dir, "record")
        self.test_results_dir = pjoin(self.working_dir, "test_results")

    def _make_working_directories(self):
        os.makedirs(self.working_dir, exist_ok=True)
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.record_dir, exist_ok=True)
        os.makedirs(self.test_results_dir, exist_ok=True)

    def get_aavenger_version(self):
        with open(pjoin(self.aavenger_dir, "version", "version"), "r") as infile:
            self.aavenger_version = str(infile.readlines()[0]).replace("\n", "")

    def _delete_raw_dir(self):
        if os.path.exists(self.raw_dir):
            shutil.rmtree(self.raw_dir)

    def load_test_data_sheet(self, test_data_sheet_path):
        self.df_test_data = pd.read_csv(test_data_sheet_path)

    def validate_sample_sheet_paths(self):
        """
        sample sheet for each test run should exist
        """
        for _, run_ in self.df_test_data.iterrows():
            if not os.path.exists(run_.sample_sheet_path):
                raise ValueError(f"{run_.sample_sheet_path} not found")
                sys.exit()

    def validate_run_tags(self):
        """
        run tags must be unique
        """
        if not len(self.df_test_data["run_tag"].unique()) == self.df_test_data.shape[0]:
            raise ValueError("Duplicated values found in run_tag column")
            sys.exit()

    def set_record_run_path(self):
        self.record_run_path = pjoin(self.record_dir, f"{self.time_stamp}_record.csv")

    def record_run(self):
        self.set_record_run_path()
        self.run_record = self.df_test_data.copy()
        self.run_record["time_stamp"] = self.time_stamp
        self.run_record["working_dir"] = self.working_dir
        self.run_record["aavenger_version"] = self.aavenger_version
        self.run_record.to_csv(self.record_run_path, index=None)


class RunHandler:
    """
    Class for data that is run specific. Purpose is to do all work related to preparing information
    necessary for a single aavenger run right up to running it.
    """

    def __init__(
        self,
        input_manager,
        run_id,
        random_seed_value,
        number_of_reads,
        n_cpus,
        config_preset,
        sample_sheet_path,
        run_tag,
    ):
        self.input_manager = input_manager
        self.run_id = run_id
        self.random_seed_value = random_seed_value
        self.number_of_reads = number_of_reads
        self.config_preset = config_preset
        self.n_cpus = n_cpus

        self.read_files = {
            "R1": {"raw": "Undetermined_S0_R1_001.fastq.gz"},
            "R2": {"raw": "Undetermined_S0_R2_001.fastq.gz"},
            "I1": {"raw": "Undetermined_S0_I1_001.fastq.gz"},
        }

        self.run_tag = run_tag

        self.stamped_run_id = make_stamped_run_id(
            input_manager.time_stamp, self.run_id, self.run_tag
        )  # f'{input_manager.time_stamp}_{self.run_id}_{self.run_tag}'

        self.aavenger_output_dir = pjoin(
            self.input_manager.processed_dir, self.stamped_run_id
        )

        self.sample_sheet = pd.read_csv(sample_sheet_path, sep="\t")

    def write_sample_sheet(self):
        self.sample_sheet.to_csv(
            pjoin(self.input_manager.raw_dir, "sample_sheet.tsv"), sep="\t", index=None
        )

    def pull_sequencing_run(self):
        """
        Hardcoded to microb120 and the Illumina sequencing folder
        """
        for read_type_ in self.read_files.keys():
            system_call = f"scp {self.input_manager.microb120_user}@microb120.med.upenn.edu:/media/sequencing/Illumina/{self.run_id}/Data/Intensities/BaseCalls/{self.read_files[read_type_]['raw']} {self.input_manager.raw_dir}"

            os.system(system_call)

    def downsample_reads(self):
        """ """
        for read_type_ in self.read_files.keys():
            self.read_files[read_type_]["downsampled"] = (
                "downsampled_" + self.read_files[read_type_]["raw"]
            )

            input_read = pjoin(
                self.input_manager.raw_dir, self.read_files[read_type_]["raw"]
            )

            output_read = pjoin(
                self.input_manager.raw_dir, self.read_files[read_type_]["downsampled"]
            )

            system_call = f"reformat.sh in={input_read} out={output_read} reads={self.number_of_reads} ow=t sampleseed={self.random_seed_value}"

            os.system(system_call)

    def make_config_file(self):
        """
        Requires self.downsample_reads() has been run to create the dictionary it uses to assign read names to the config file. This is intended.
        """

        self.config_path = pjoin(self.input_manager.raw_dir, "config.yml")

        with open(self.config_path, "w") as outfile:
            with open(
                pjoin(self.input_manager.aavenger_dir, "config.yml"), "r"
            ) as infile:
                for l in infile:
                    if l.startswith("mode: integrase"):
                        if self.config_preset == "integrase":
                            outfile.write("mode: integrase\n")
                        elif self.config_preset == "AAV":
                            outfile.write("mode: AAV\n")

                    elif l.startswith("outputDir"):
                        outfile.write(f"outputDir: {self.aavenger_output_dir}\n")

                    elif l.startswith("softwareDir"):
                        outfile.write(
                            f"softwareDir: {self.input_manager.aavenger_dir}\n"
                        )

                    elif l.startswith("sequencingRunID"):
                        outfile.write(f"sequencingRunID: {self.stamped_run_id}\n")

                    elif l.startswith("demultiplex_anchorReadsFile"):
                        outfile.write(
                            f"demultiplex_anchorReadsFile: {pjoin(self.input_manager.raw_dir, self.read_files['R2']['downsampled'])}\n"
                        )

                    elif l.startswith("demultiplex_adriftReadsFile"):
                        outfile.write(
                            f"demultiplex_adriftReadsFile: {pjoin(self.input_manager.raw_dir, self.read_files['R1']['downsampled'])}\n"
                        )

                    elif l.startswith("demultiplex_index1ReadsFile"):
                        outfile.write(
                            f"demultiplex_index1ReadsFile: {pjoin(self.input_manager.raw_dir, self.read_files['I1']['downsampled'])}\n"
                        )

                    elif l.startswith("demultiplex_sampleDataFile"):
                        outfile.write(
                            f"demultiplex_sampleDataFile: {pjoin(self.input_manager.raw_dir, 'sample_sheet.tsv')}\n"
                        )

                    elif l.startswith("buildStdFragments_createMultiHitClusters"):
                        outfile.write(
                            f"buildStdFragments_createMultiHitClusters: True\n"
                        )

                    elif l.find("_CPUs:") > -1:
                        new_cpus = l.replace("_CPUs:", f"_CPUs: {self.n_cpus} #")
                        outfile.write(new_cpus)

                    else:
                        outfile.write(l)


class AAVengeRDockerRunner:
    """
    Wrapping some existing variables in data objects designed for the docker library.
    Requires that run_handler have data available from downsample_reads() and make_config_file()

    Purpose is solely to run the aavenger docker with preconfigured inputs.
    """

    def __init__(self, run_handler):
        self.run_handler = run_handler
        self.mounts = [
            {
                "type": "bind",
                "source": f"{self.run_handler.input_manager.source_mount}",  # Path on the host
                "target": f"{self.run_handler.input_manager.target_mount}",  # Path in the container
            }
        ]
        self.environment = {
            "AAVENGER_DIR": self.run_handler.input_manager.aavenger_dir,  # Ensure these are capitalized
            "AAVENGER_CONFIG_PATH": pjoin(
                self.run_handler.config_path
            ),  # Ensure these are capitalized
        }

    def run(self):
        client = docker.from_env()

        try:
            container = client.containers.run(
                image=self.run_handler.input_manager.docker_image_name,
                mounts=[docker.types.Mount(**mount) for mount in self.mounts],
                environment=self.environment,
                detach=False,
                stdout=True,
                stderr=True,
            )
            print(container.decode("utf-8"))  # Print container output
        except docker.errors.ContainerError as e:
            print(f"ContainerError: {e}")
            print(f"Command: {e.command}")
            print(f"Exit code: {e.exit_status}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise


class RunResultChecker:
    """
    Builds ALL info from a _record.csv file
    Handles checking the results of a run
    self.run_record_path = run_record_path
    """

    # def __init__(self, run_id, run_tag, time_stamp, working_dir, record_row):
    def __init__(self, record_row):
        self.run_id = record_row.run_id

        self.run_tag = record_row.run_tag

        self.working_dir = record_row.working_dir

        self.time_stamp = record_row.time_stamp

        self.aavenger_version = str(record_row.aavenger_version)

        self.stamped_run_id = make_stamped_run_id(
            self.time_stamp, self.run_id, self.run_tag
        )

        self.run_output_dir = pjoin(
            self.working_dir, "processed", self.time_stamp, self.stamped_run_id
        )

        self.test_results_dir = pjoin(self.working_dir, "test_results", self.time_stamp)

        self.record_identfier = record_row.to_frame().T

        self.record_identfier = self.record_identfier[
            [
                "run_id",
                "random_seed_value",
                "number_of_reads",
                "config_preset",
                "run_tag",
                "time_stamp",
                "aavenger_version",
            ]
        ]

        self.sites_feature_to_test = [
            "file_detected",
            "shape_rows",
            "shape_columns",
            "n_subject",
            "n_sample",
            "n_refGenome",
            "n_posid",
            "n_vector",
            "n_repeat_name",
            "n_repeat_class",
            "n_nearestGene",
            "sum_sonicLengths",
            "sum_reads",
            "sum_nRepsObs",
            "sum_inGene",
            "sum_inExon",
        ]

    def make_test_results_dir(self):
        os.makedirs(self.test_results_dir, exist_ok=True)

    def _read_in_reference_output_path(self):
        pass

    def _read_in_sites(self):
        try:
            self.sites = pd.read_excel(
                pjoin(self.run_output_dir, "annotateRepeats", "sites.xlsx")
            )
            self.sites_exist = True
        except:
            self.sites = pd.DataFrame()
            self.sites_exist = False

    def characterize_sites_features(self):
        """ """
        self.site_features = {}

        for feature_ in self.sites_feature_to_test:
            if feature_.startswith("file_"):
                self.site_features[feature_] = [self.sites_exist]
            if feature_.startswith("n_"):
                self.site_features[feature_] = [0]
            if feature_.startswith("sum_"):
                self.site_features[feature_] = [0]
            if feature_.startswith("shape_"):
                self.site_features[feature_] = [0]

        if self.sites_exist:
            self.sites["nRepsObs"] = self.sites["nRepsObs"].fillna(
                0
            )  # nRepsObs is blank for dual detections

            # dimensions of the sites file
            self.site_features["shape_rows"] = [self.sites.shape[0]]
            self.site_features["shape_columns"] = [self.sites.shape[1]]

            # count unique features
            for feature_ in [
                "subject",
                "sample",
                "refGenome",
                "posid",
                "vector",
                "repeat_name",
                "repeat_class",
                "nearestGene",
            ]:
                self.site_features[f"n_{feature_}"] = [
                    len(self.sites[feature_].unique())
                ]

            # sum features
            for feature_ in ["sonicLengths", "reads", "nRepsObs", "inGene", "inExon"]:
                self.site_features[f"sum_{feature_}"] = [sum(self.sites[feature_])]

    def make_sites_df(self):
        df_site_results = pd.concat(
            [
                self.record_identfier.reset_index(drop=True),
                pd.DataFrame(self.site_features).reset_index(drop=True),
            ],
            axis=1,
        )

        return df_site_results

    def _read_in_multihitclusters(self):
        pass

    def _read_in_anchorreadclusters(self):
        pass

    def check_output_exists(self):
        pass

    def difference_with_reference(self):
        pass


class CompareResults:
    def __init__(self, test_results_path, expected_results_path):
        """
        inputs are paths to directories that contain test outputs that will be either the actual or expected results.
        Files will need to match the hardocde file names
        """
        self.test_results_path = test_results_path
        self.expected_results_path = expected_results_path
        self.identifier_columns = [
            "run_id",
            "random_seed_value",
            "number_of_reads",
            "config_preset",
            "run_tag",
        ]  # , 'time_stamp', 'aavenger_version']
        self.results = {"sites": {"raw": "", "all": "", "only_different": ""}}

    def compare_sites(self):
        """ """
        df_actual = pd.read_csv(pjoin(self.test_results_path, "site_features.csv"))

        df_expected = pd.read_csv(
            pjoin(self.expected_results_path, "site_features.csv")
        )

        self.results["sites"]["raw"] = self.merge_expected_actual_sites(
            df_actual=df_actual,
            df_expected=df_expected,
            identifier_columns=self.identifier_columns,
        )

        df_actual = df_actual.drop(columns=["time_stamp", "aavenger_version"])

        df_expected = df_expected.drop(columns=["time_stamp", "aavenger_version"])

        df_difference = self.merge_expected_actual_sites(
            df_actual=df_actual,
            df_expected=df_expected,
            identifier_columns=self.identifier_columns,
        )

        feature_columns = [
            i for i in df_expected.columns.tolist() if i not in self.identifier_columns
        ]

        df_results = self.build_compare_table(
            df_difference=df_difference,
            feature_columns=feature_columns,
            identifier_columns=self.identifier_columns,
        )

        self.results["sites"]["all"] = df_results

        self.results["sites"]["only_different"] = df_results[
            df_results["difference"] != 0
        ]

    def build_compare_table(self, df_difference, feature_columns, identifier_columns):
        """
        df_difference: merged df_actual and df_expected where measured values are tagged with _expected or _actual.
        feature_columns: list of columns of measured values to be compared
        identifier_columns: list of columns with data that should be exactly the same for both expected and actual tables.
        """
        df_results = pd.DataFrame()

        for _, result_pair in df_difference.iterrows():
            df_identifier = pd.DataFrame()

            for feat_ in feature_columns:
                result = {
                    "feature": [feat_],
                    "actual": [result_pair[f"{feat_}_actual"]],
                    "expected": [result_pair[f"{feat_}_expected"]],
                }

                df_identifier = pd.concat([df_identifier, pd.DataFrame(result)], axis=0)

            df_identifier["run_id"] = result_pair.run_id
            df_identifier["random_seed_value"] = result_pair.random_seed_value
            df_identifier["number_of_reads"] = result_pair.number_of_reads
            df_identifier["config_preset"] = result_pair.config_preset
            df_identifier["run_tag"] = result_pair.run_tag
            df_identifier["difference"] = (
                df_identifier["expected"] - df_identifier["actual"]
            )

            df_results = pd.concat([df_results, df_identifier], axis=0)

        # reorder output
        column_reorder = identifier_columns
        for i in ["feature", "actual", "expected", "difference"]:
            column_reorder.append(i)

        df_results = df_results[column_reorder]

        return df_results

    def merge_expected_actual_sites(self, df_actual, df_expected, identifier_columns):
        """
        identifier_columns: list of columns with data that should be exactly the same for both expected and actual tables.
        """
        return df_actual.merge(
            df_expected,
            on=identifier_columns,
            how="outer",
            suffixes=("_actual", "_expected"),
        )

    def write_comparisons(self):
        for k, v in self.results.items():
            v["raw"].to_csv(
                pjoin(self.test_results_path, f"{k}_raw_comparisons.csv"), index=None
            )
            v["all"].to_csv(
                pjoin(self.test_results_path, f"{k}_all_comparisons.csv"), index=None
            )
            v["only_different"].to_csv(
                pjoin(self.test_results_path, f"{k}_difference_comparisons.csv"),
                index=None,
            )

    @staticmethod
    def check_expected_data_exists(expected_results_path):
        expected_data = ["site_features.csv"]
        for i in expected_data:
            i_data_path = pjoin(expected_results_path, i)
            if not os.path.exists(i_data_path):
                raise ValueError(f"{i_data_path} does not exist")
