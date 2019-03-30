# Web Archiving Screenshot Compare
Utilities for creating screenshots of archived websites and their live counterparts and compares the two screenshots.

## Getting Started
Some packages such as pyppeteer run best on python 3.6. The necessary packages are listed in environment.yml

Instructions on how to install Anaconda for python can be found [here](https://docs.anaconda.com/anaconda/install/linux/)

Once anaconda is installed, import the environment with
```
conda env create -f environment.yml
```
Activating and deactivating the anaconda environment
```
conda activate python3_6
conda deactivate
```

## Usage
> **Notes:** Including the -h flag in any of the programs will display a description of all the command line flags

### read_seed.py
This program takes a CSV file with the seed website URLs and outputs it into another CSV or a DB.

> A valid seed csv file should have the urls as the first column, other columns are ignored.
> The output CSV file will have three columns, archive ID, url ID, and url.

Command syntax: 
```
python3 read_seed.py --csv=your/directory/Collection-seed-list.csv --db=urls.db --out=current_urls.csv --ext=1234
--name="Collection Name" --sort
```
Arguments:
* csv - The CSV file with the seed urls.
* db - The DB file to store the urls.
* out - The CSV file to write the urls.
* ext - ID of the archive.
* name - Name of the archive.
* sort - (optional) Include to sort the output.











