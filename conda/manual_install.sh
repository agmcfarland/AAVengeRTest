
cd /data/AAVengeRTest

conda create -n AAVengeRTest

conda activate AAVengeRTest

conda config --add channels conda-forge 

conda config --add channels bioconda

conda config --add channels defaults

conda config --set channel_priority strict

mamba install anaconda::ipython=8.27.0 -y #installs python 3.12.17 

mamba install bioconda::bbmap -y

pip install pandas biopython numpy pytest pytest-cov openpyxl docker

conda env export --no-builds > environment.yml

# editable install of AAVengeRTest
cd /data/AAVengeRTest

python -m pip install -e .