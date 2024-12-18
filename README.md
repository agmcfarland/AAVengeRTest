# AAVengeRTest


[![Lint](https://github.com/agmcfarland/AAVengeRTest/actions/workflows/black.yml/badge.svg)](https://github.com/agmcfarland/Bartender/actions/AAVengeRTest/black.yml)

[![TestsConda](https://github.com/agmcfarland/AAVengeRTest/actions/workflows/conda-deployment.yml/badge.svg)](https://github.com/agmcfarland/AAVengeRTest/actions/workflows/conda-deployment.yml)

[![codecov](https://codecov.io/gh/agmcfarland/AAVengeRTest/graph/badge.svg?token=h0353eSj1d)](https://codecov.io/gh/agmcfarland/AAVengeRTest)


Test AAVengeR against different versions using whole or subsets of sequencing data from the Bushman Lab.   

# Usage

```
usage: AAVengeRTest [-h] [--output_dir] [--test_data_sheet] [--expected_output_dir] [--microb120_user] [--docker_image_name] [--aavenger_dir] [--docker_source_mount] [--docker_target_mount]

options:
  -h, --help            show this help message and exit
  --output_dir
  --test_data_sheet
  --expected_output_dir
  --microb120_user
  --docker_image_name
  --aavenger_dir
  --docker_source_mount
  --docker_target_mount
```

# Installation

```sh
# Set ssh permission so connection to microb120 is passwordless
# <redacted>

# allow docker to be used passwordless
sudo gpasswd -a $USER docker
newgrp docker

# install AAVengeRTest
```

# Inputs

## test_data_sheet

todo

## expected_output_dir

todo