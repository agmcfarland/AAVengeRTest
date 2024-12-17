#!/bin/bash
conda activate AAVengeRTest

# INPUTS START
REPO_URL="https://github.com/helixscript/AAVengeR"
DST_PATH="/data" # where AAVengeR will be downloaded to
GENOME_DATA_FOLDER='/data/AAVengeR/data' # existing data location with genomeAnntations and referenceGenomes
AAVENGER_TO_TEST="AAVengeR_totest" # new name of the pulled AAVengeR folder
# INPUTS END

echo "Starting set up"

# Download the repository as a ZIP archive
echo "Downloading the repository as a ZIP archive..."
curl -L "${REPO_URL}/archive/refs/heads/main.zip" -o "${DST_PATH}/AAVengeR-main.zip"

# Remove existing AAVengeR_TO_TEST if it exists
if [ -e "${DST_PATH}/${AAVENGER_TO_TEST}" ]; then
	echo "Removing existing ${AAVENGER_TO_TEST}"
	rm -R "${DST_PATH}/${AAVENGER_TO_TEST}"
fi

# Extract the ZIP archive
echo "Extracting the ZIP archive..."
unzip "${DST_PATH}/AAVengeR-main.zip" -d $DST_PATH
mv "${DST_PATH}/AAVengeR-main" "${DST_PATH}/${AAVENGER_TO_TEST}"

# Cleanup
echo "Cleaning up..."
rm "${DST_PATH}/AAVengeR-main.zip" 

# Sym link large data folders to latest repository extract folder
# genome annotations (repeat tables, TU, exons)
ln -s "${GENOME_DATA_FOLDER}/genomeAnnotations" "${DST_PATH}/${AAVENGER_TO_TEST}/data/genomeAnnotations"

# referenceGenomes (blat, bwa2 index files)
ln -s "${GENOME_DATA_FOLDER}/referenceGenomes" "${DST_PATH}/${AAVENGER_TO_TEST}/data/referenceGenomes"

echo "Set up finished"

echo 'Testing version:'
head "${DST_PATH}/${AAVENGER_TO_TEST}/version/version"


# Packaged test data (small) (15 mins)
AAVengeRTest \
--output_dir /data/aavenger_stability_testing/packaged_test_data \
--test_data_sheet /data/AAVengeRTest/tests/data/ete_correct_input_sheet.csv \
--expected_output_dir /data/aavenger_stability_testing/data/packaged_test_data/expected_results \
--microb120_user agmcfarland \
--docker_image_name aavenger_docker_v3 \
--aavenger_dir $DST_PATH/$AAVENGER_TO_TEST \
--docker_source_mount /data \
--docker_target_mount /data

# Fast test data (Small subsets of jones ad09 (15 mins), jones lod (15 mins), persaud (19 mins), and topo (24 mins@30))
AAVengeRTest \
--output_dir /data/aavenger_stability_testing/fast_test_1 \
--test_data_sheet /data/aavenger_stability_testing/data/fast_test_1/testing_input_1.csv \
--microb120_user agmcfarland \
--docker_image_name aavenger_docker_v3 \
--aavenger_dir $DST_PATH/$AAVENGER_TO_TEST \
--docker_source_mount /data \
--docker_target_mount /data


# sudo rm -R /data/aavenger_stability_testing/fast_test_1