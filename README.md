# Web Archiving Screenshot Compare
Utilities for creating screenshots of archived websites and their live counterparts and compares the two screenshots.

## Getting Started
Some packages such as pyppeteer run best on python 3.6. The necessary packages are listed in environment.yml.

Instructions on how to install Anaconda for python can be found [here](https://docs.anaconda.com/anaconda/install/linux/).

Once anaconda is installed, import the environment with.
```
conda env create -f environment.yml
```
Activating and deactivating the anaconda environment.
```
conda activate python3_6
conda deactivate
```

## Usage
> **Notes:** Including the -h flag in any of the programs will display a description of all the command line flags.

### read_seed.py
This program takes a CSV file with the seed website URLs and outputs it into another CSV or a DB.
> A valid seed csv file should have the URLs as the first column, other columns are ignored.
> The output CSV file will have three columns, archive ID, URL ID, and URL.

Command syntax: 
```
python3 read_seed.py --csv=your/directory/Collection-seed-list.csv --db=urls.db --out=current_urls.csv --ext=1234
--name="Collection Name" --sort
```
Arguments:
* csv - The CSV file with the seed URLs. Interchangeable with --db as only one type of input is allowed.
* db - The DB file to store the URLs.
* out - The CSV file to write the URLs.
* ext - ID of the archive.
* name - Name of the archive.
* sort - (optional) Include to sort the output.

### create-archive_urls.py
This program takes the CSV or DB from the previous program and gets the Archive-It archive URL.  
> The output CSV file will have three columns, archive ID, URL ID, and URL.

Command syntax: 
```
python3 create_archive_urls.py --csv=current_urls.csv --db=urls.db --out=archive_urls.csv --banner
```
Arguments:
* csv - Input CSV file with current URLs. Interchangeable with --db as only one type of input is allowed.
* db - Input DB file with URLs, output is automatically inserted in db.
* out - The CSV file to write the URLs.
* banner - (optional) Include to generate URLs that has the banner, default removes banner.

### current_screenshot.py
This program takes the CSV or DB with the current website URLS and takes screenshots
> The output CSV will have four columns, archive ID, URL ID, success code, and URL.
> As of right now, method=1 takes the most consistent screenshots.

Command syntax: 
```
python3 current_screenshots.py --csv=current_urls.csv --db=urls.db --picsout=current_pics/ --indexcsv=current_index.csv --method=0 --timeout=30
```
Arguments:
* csv - Input CSV file with current URLs.
* db - Input DB file with URLs.
* picsout - Directory to output the screenshots.
* indexcsv - The CSV file to write the index.
* method - Which method to take the screenshots, 0 for chrome, 1 for puppeteer, 2 for cutycapt.
* timeout - (optional) Specify duration before timeout for each site, in seconds, default 30 seconds.

