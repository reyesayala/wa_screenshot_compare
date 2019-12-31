#!/bin/bash
#SBATCH --time=48:00:00
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=2
#SBATCH --mem=4096

# fill in the variables with the necessary values and paths to certain files, the paths can be relative to where the script is being run
# this is the bash script for the regular collections, make sure the path for wa_screenshot_compare is from the master branch.
# NOTE if path of any variable contains a space, enclose it with double quotes  ex. working_directory="../Idle No More/"


# REQUIRED path to wa_screenshot_compare    ex. scripts_path=../../wa_screenshot_compare
scripts_path=../../wa_screenshot_compare

# REQUIRED path to current_urls.csv generated from read_seed.py
current_urls_path=index/current_urls.csv 

# REQUIRED path to directory that contains all the current screenshots, and path to current_index.csv. needed for calculate similarity
pics_current_path=pics_current/
current_index_path=index/current_index.csv

# REQUIRED path to a directory to store all output. the index folder and the pics_archive_* folders will be created here, and the index files and screenshots will then be put into those folders
working_directory=./

# REQUIRED number of instances of archive_screenshot.py to be run at once, recommended 5
num_instances=5


# uncomment the code below to automatically create the folders 
# leave them commented if folders exist already
# NOTE files inside those folders may be overwritten if program creates a file of the same name
#mkdir $working_directory/index


# creating archive_urls.csv
python3 "$scripts_path"/create_archive_urls.py --csv="$current_urls_path" --out="$working_directory"index/archive_urls.csv

# number of lines in archive_urls.csv rounded up to the nearest 1000 
max_num_lines=$(( $(( $(( $( wc -l < "$working_directory"/index/archive_urls.csv ) / 1000 )) + 1 )) * 1000 ))

# make the folders for batches, no action is done if folders exists already
# if folder contains files of the same name, they may be over written
mkdir "$working_directory"/pics_archive_combined
counter=1000
while [ $counter -le "$max_num_lines" ]
do
    mkdir "$working_directory"/pics_archive_$counter
    counter=$(($counter + 1000))                                                                                                                    
done 


# running the screenshotting code
# awaits at a certain number of instances and at the last instance
counter=1000
while [ $counter -le "$max_num_lines" ]
do
    if [ $(( $counter % ( $(($num_instances * 1000)) ) )) -eq 0 ] || [ $counter -eq "$max_num_lines" ]
    then
        python3 "$scripts_path"/archive_screenshot.py --csv="$working_directory"/index/archive_urls.csv --indexcsv="$working_directory"/index/archive_index_$counter.csv --picsout="$working_directory"/pics_archive_$counter --method=1 --range=$(($counter - 999)),$counter --banner
    else
        python3 "$scripts_path"/archive_screenshot.py --csv="$working_directory"/index/archive_urls.csv --indexcsv="$working_directory"/index/archive_index_$counter.csv --picsout="$working_directory"/pics_archive_$counter --method=1 --range=$(($counter - 999)),$counter --banner &
    fi

    counter=$(($counter + 1000))
done

# move screenshots into one folder, concat all index to one file
counter=1000
touch "$working_directory"/index/archive_index_combined.csv
sed -n 1p "$working_directory"/index/archive_index_$counter.csv > "$working_directory"/index/archive_index_combined.csv

while [ $counter -le "$max_num_lines" ]
do
    sed -n 2,1005p "$working_directory"/index/archive_index_$counter.csv >> "$working_directory"/index/archive_index_combined.csv
    cp "$working_directory"/pics_archive_$counter/*.png "$working_directory"/pics_archive_combined
    counter=$(($counter + 1000))
done


# comparison code
python3 "$scripts_path"/get_file_names.py --currcsv="$current_index_path" --archcsv="$working_directory"/index/archive_index_combined.csv --out="$working_directory"/index/filenames.csv
python3 "$scripts_path"/calculate_similarity.py --csv="$working_directory"/index/filenames.csv --currdir="$pics_current_path" --archdir="$working_directory"/pics_archive_combined --out="$working_directory"/index/scores.csv --ssim --mse --vec
