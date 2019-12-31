#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
#SBATCH --mem=2048


# fill in the variables with the values and paths respective to the path of this script
# NOTE if path of any variable contains a space, enclose it with double quotes

# path to wa_screenshot_compare    ex. scripts_path=../../wa_screenshot_compare
scripts_path=            #../wa_screenshot_compare

# path to where the seed is    ex. current_seed_path=../seeds/target-qa-dataset-oa-subset.csv
current_seed_path=       #../../seeds/target-qa-dataset-oa-subset.csv

# path to directory to store all the output files. the index folder and pics_current folder will be created here, and all the index files and screenshots will be generated in those folders
working_directory=       #./

# name of the archive, use double quotes to surround the name
archive_name=            #"UK archive"

# code below automatically creates the folders
# NOTE files inside those folders may be overwritten
# no action if folder already exists
mkdir $working_directory/pics_current
mkdir $working_directory/index


python3 "$scripts_path"/read_seed.py --csv="$current_seed_path" --out="$working_directory"/index/current_urls.csv --name="$archive_name" --sort
python3 "$scripts_path"/current_screenshot.py --csv="$working_directory"/index/current_urls.csv --indexcsv="$working_directory"/index/current_index.csv --picsout="$working_directory"/pics_current
