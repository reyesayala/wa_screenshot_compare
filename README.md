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
This program takes the CSV or DB with the current website URLS and takes screenshots. The output CSV will have six columns: archive ID, URL ID, URL, site status, site message, and screenshot message: 
* site_status - Contains 'LIVE' if the URL can be reached or redirects, and 'FAIL' if the URL could not be reached (ex. 404).
* site_message - A reason on why site_status was 'LIVE' or 'FAIL'. Such as 'Redirected to http://......' or 'HTTPError: 404'.
* screenshot_message - a message on whether the screenshot was successful. If site_status is 'FAIL' then screenshot_message is automatically 'Screenshot unsuccessful'. Another common message is 'Navigation Timeout Exceeded'.
> As of right now, method=1 takes the most consistent screenshots.

Command syntax: 
```
python3 current_screenshots.py --csv=current_urls.csv --db=urls.db --picsout=current_pics/ --indexcsv=current_index.csv --method=0 --timeout=30
```
Arguments:
* csv - Input CSV file with current URLs. Interchangeable with --db as only one type of input is allowed.
* db - Input DB file with URLs.
* picsout - Directory to output the screenshots.
* indexcsv - The CSV file to write the index.
* method - Which method to take the screenshots, 0 for chrome, 1 for puppeteer, 2 for cutycapt.
* timeout - (optional) Specify duration before timeout for each site, in seconds, default 30 seconds.

### archive_screenshot.py
This program takes the CSV or DB with the archive website URLS and takes screenshots. The output CSV will have seven columns, archive ID, URL ID, capture date, URL, site status, site message, and screenshot message.
* site_status - Contains 'LIVE' if the URL can be reached or redirects, and 'FAIL' if the URL could not be reached (ex. 404).
* site_message - A reason on why site_status was 'LIVE' or 'FAIL'. Such as 'Redirected to http://......' or 'HTTPError: 404'.
* screenshot_message - a message on whether the screenshot was successful. If site_status is 'FAIL' then screenshot_message is automatically 'Screenshot unsuccessful'. Another common message is 'Navigation Timeout Exceeded'.
> As of right now, method=1 takes the most consistent screenshots.

Command syntax:
```
python3 archive_screenshot.py --csv=archive_csv.csv --db=urls.db --picsout=archive_pics/ --indexcsv=archive_index.csv --method= 0 --timeout=30 --lazy=1
```
Arguments:
* csv - Input CSV file with archive URLs. Interchangeable with --db as only one type of input is allowed.
* db - Input DB file with URLs.
* picsout - Directory to output the screenshots.
* indexcsv - The CSV file to write the index.
* method - Which method to take the screenshots, 0 for chrome, 1 for puppeteer, 2 for cutycapt.
* timeout - (optional) Specify duration before timeout for each site, in seconds, default 30 seconds.
* lazy - (optional) Makes the program continue to the next archive after taking n pictures.

### get_file_names.py
This program outputs a CSV file which maps the current and archive URLs with their respective screenshots.
> The output CSV will have four columns, current URl, archive URL, current screenshot file name, archive screenshot file name.

Command syntax:
```
python3 get_file_names.py --currcsv=current_index/ --archcsv=archive_index/ --db=urls.db --out=file_names.csv --print
```
Arguments:
* currcsv - The CSV file with the current screenshots index.
* archcsv - The CSV file with the archive screenshots index.
* db - Input DB file with urls. Interchangeable with using --currcsv and --archcsv since only one type of input is allowed. 
* out - The CSV file to write the urls and file names. 
* print - (optional) Include to print urls and file names to stdout, default doesn't print.

### randomly_select_screenshots.py
This program outputs a CSV file where each current screenshot is mapped to only one archive screenshot.
> The output CSV will essentially be the same as the output of get_file_names.py

command syntax:
```
python3 randomly_select_screenshots.py --csv=file_names.csv --out=selected_file_names.csv
```
Arguments:
* csv - The CSV file with screenshot file names.
* out - The CSV file to write the newly selected file names.

### calculate_similarity.py
This program gets all the screenshots and calls functions in similarity_measures.py to calculate the image similarity socres.
> The output CSV will have five to seven columns, current URl, archive URL, current screenshot file name, archive screenshot file name, structural similarty score, mean squared error, vector comparison score.

command syntax:
```
python3 calculate_similarity.py --csv=file_names.csv --currdir=current_pics/ --archdir=archive_pics/ --out=score.csv --ssim --mse --vec --print
```
Arguments:
* csv - The CSV file with screenshot file names.
* currdir - Directory with screenshots of the current websites.
* archdir - Directory with screenshots of the archive websites.
* out - The CSV file to write the results of the comparisons.
* ssim - (optional) Include to calculate structural similarity.
* mse - (optional) Include to calculate mean square error.
* vec - (optional) Include to calculate vector comparison score.
* print - (optional) Include to print results to stdout.

### similarity_measures.py
Contains functions used by calculate_similarity.py which will be used to calculate the scores.

### crop_banners_from_images.py
This program crops banners from website images. The user must supply the dimensions of the banner. For example, in order to remove banner from British Library UK OA collection, with screenshots that measure 1024 x 768, use the following dimensions: (0,43,1024,768). The resulting image will have the banner cropped and will be 1024 x 725. The Pillow imaging library must be installed in Python. For more information on this library, see: https://auth0.com/blog/image-processing-in-python-with-pillow/

command syntax:
```
python3 crop_banners_from_images.py --input_dir pics_archived_banners/ --output_dir pics_archived_no_banners/ --new_dimensions=0,43,1024,768
```
Arguments:
* input_dir - directory of screenshots with banners that need to be removed
* output_dir - directory where screenshots without the banners will be saved
* new_dimensions - dimensions of the banner to remove


## Authors
* **Brenda Reyes Ayala** 
* **James Sun**
## License
todo

## Acknowledgments 
todo
