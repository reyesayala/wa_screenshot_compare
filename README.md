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
> **Notes:** Including the -h flag for programs using command line flags will display a description of all the flags.

### screenshot_compare.ini

This is a setting file used by config.py to pass arguments into programs. The file is partitioned such that each section corresponds to a program in this repository. A DEFAULT section exists where arguments common to multiple programs can be listed under DEFAULT.

Note that to use arguments under the DEFAULT section, you will need to replace relevant variables under config.py to apply your desired changes. 

The following settings/arguments can be altered: 

**DEFAULT:**

- timeout - (optional) Specify duration before timeout for each site, in seconds. Default is 30 seconds.
  - This argument can replace c_timeout and a_timeout.
- picsout - Directory to the output of the screenshots.
  - This argument can replace current_pics_dir and archive_pics_dir.
- current_urls_csv - Input CSV file with current URLs. 
- method - Which method to take the screenshots: 0 for chrome, 1 for puppeteer, 2 for cutycapt.
  - This argument can replace c_method and a_method.
- keep_cookies - (optional) Specify to NOT remove cookies. Default removes cookies.
  - This argument can replace c_keep_cookies and a_keep_cookies.
- screen_height & screen_width - (optional) Specify to take screenshots of a certain size; affects browser viewport as well. Default height is 768, and default width is 1024.
  - These arguments can replace c_screen_height, c_screen_width, a_screen_height, and a_screen_width.

**read_seed:**

* seed_list - The CSV file with the seed URLs. 
* current_urls_csv - The CSV file to write the URLs.
* collection_id - ID of the archive.
* name - Name of the archive.
* sort - (optional) Include to sort the output.

**create_archive_urls:**

* current_urls_csv - Input CSV file with current URLs. 
* archive_urls_csv - The CSV file to write the archive URLs.
* remove_banner - Specify "1" to remove banner, "0" otherwise.

**current_screenshot:** 

* current_pics_dir - Directory to output the screenshots.
* current_index_csv - The CSV file to write the index.
* c_method - Which method to take the screenshots: 0 for chrome, 1 for puppeteer, 2 for cutycapt.
* c_screen_height & c_screen_width - (optional) Specify to take screenshots of a certain size; affects browser viewport as well. Default height is 768, and default width is 1024.
* c_timeout - (optional) Specify duration before timeout for each site, in seconds. Default is 30 seconds.
* c_keep_cookies  - (optional) Specify to NOT remove cookies. Default removes cookies.
* c_chrome_args - (optional) Additional arguments for pyppeteer chrome. Ex. c_chrome_args = ["--disable-gpu ", "--no-sandbox"]
* c_range_min & c_range_max - Specify to take screenshots between these lines, inclusive. Setting arguments to 'None' takes screenshots of everything.

**archive_screenshot:**

* archive_pics_dir - Directory to output the screenshots.
* archive_index_csv - The CSV file to write the index.
* a_method - Which method to take the screenshots: 0 for chrome, 1 for puppeteer, 2 for cutycapt.
* a_screen_height & a_screen_width - (optional) Specify to take screenshots of a certain size; affects browser viewport as well. Default height is 768, and default width is 1024.
* a_timeout - (optional) Specify duration before timeout for each site, in seconds. Default is 30 seconds.
* a_keep_cookies  - (optional) Specify to NOT remove cookies. Default removes cookies.
* a_chrome_args - (optional) Additional arguments for pyppeteer chrome. Ex. a_chrome_args = ["--disable-gpu ", "--no-sandbox"]
* a_range_min & a_range_max - Specify to take screenshots between these lines, inclusive. Setting arguments to 'None' takes screenshots of everything.

**get_file_names:**

* file_names_csv - The CSV file to write the urls and file names. 
* print - (optional) Include to print urls and file names to stdout, default doesn't print.

**calculate_similarity:**

* scores_file_csv - The CSV file to write the results of the comparisons.
* ssim - (optional) Include to calculate structural similarity.
* mse - (optional) Include to calculate mean square error.
* vector - (optional) Include to calculate vector comparison score.
* similarity_print - (optional) Include to print results to stdout.

### read_seed.py

This program takes a CSV file with the seed website URLs and outputs it into another CSV.
> A valid seed csv file should have the URLs as the first column, other columns are ignored.
> The output CSV file will have three columns, archive ID, URL ID, and URL.

Command syntax: 
```
python3 read_seed.py
```
### create_archive_urls.py
This program takes the CSV from read_seed.py and gets the Archive-It archive URL.  
> The output CSV file will have three columns, archive ID, URL ID, and URL.

Command syntax: 
```
python3 create_archive_urls.py
```
### current_screenshot.py
This program takes the CSV with the current website URLS and takes screenshots. The output CSV will have six columns: archive ID, URL ID, URL, site status, site message, and screenshot message: 
* site_status - Contains 'LIVE' if the URL can be reached or redirects, and 'FAIL' if the URL could not be reached (ex. 404).
* site_message - A reason on why site_status was 'LIVE' or 'FAIL'. Such as 'Redirected to http://......' or 'HTTPError: 404'.
* screenshot_message - a message on whether the screenshot was successful. If site_status is 'FAIL' then screenshot_message is automatically 'Screenshot unsuccessful'. Another common message is 'Navigation Timeout Exceeded'.
> As of right now, method=0 and 2 are deprecated

Command syntax: 
```
python3 current_screenshot.py
```
### archive_screenshot.py
This program takes the CSV with the archive website URLS and takes screenshots. The output CSV will have seven columns, archive ID, URL ID, capture date, URL, site status, site message, and screenshot message.
* site_status - Contains 'LIVE' if the URL can be reached or redirects, and 'FAIL' if the URL could not be reached (ex. 404).
* site_message - A reason on why site_status was 'LIVE' or 'FAIL'. Such as 'Redirected to http://......' or 'HTTPError: 404'.
* screenshot_message - a message on whether the screenshot was successful. If site_status is 'FAIL' then screenshot_message is automatically 'Screenshot unsuccessful'. Another common message is 'Navigation Timeout Exceeded'.
> As of right now, method=0 and 2 are deprecated

Command syntax:
```
python3 archive_screenshot.py
```
### get_file_names.py
This program outputs a CSV file which maps the current and archive URLs with their respective screenshots.
> The output CSV will have four columns, current URl, archive URL, current screenshot file name, archive screenshot file name.

Command syntax:
```
python3 get_file_names.py
```
### randomly_select_screenshots.py
This program outputs a CSV file where each current screenshot is mapped to only one archive screenshot.
> The output CSV will essentially be the same as the output of get_file_names.py

command syntax:
```
python3 randomly_select_screenshots.py --csv=file_names.csv --out=selected_file_names.csv --num=5 --total=1000
```
Arguments:
* csv - The CSV file with screenshot file names.
* out - The CSV file to write the newly selected file names.
* num - Number of random screenshots to take for each ID.
* total - Total number of screenshots to take.
* recent - TODO take the screenshot of the most recent archive instead

### calculate_similarity.py
This program gets all the screenshots and calls functions in similarity_measures.py to calculate the image similarity socres.
> The output CSV will have five to seven columns, current URl, archive URL, current screenshot file name, archive screenshot file name, structural similarty score, mean squared error, vector comparison score.

command syntax:
```
python3 calculate_similarity.py
```
### similarity_measures.py
Contains functions used by calculate_similarity.py which will be used to calculate the scores.

### crop_banners_from_images.py
This program crops banners from website images. The user must supply the dimensions of the banner. For example, in order to remove banner from British Library UK OA collection, with screenshots that measure 1024 x 768, use the following dimensions: (0,43,1024,768). The resulting image will have the banner cropped and will be 1024 x 725. The Pillow imaging library must be installed in Python. For more information on this library, see: https://auth0.com/blog/image-processing-in-python-with-pillow/

command syntax:
```
python3 crop_banners_from_images.py --input_dir=pics_archived_banners/ --output_dir=pics_archived_no_banners/ --new_dimensions=0,43,1024,768
```
Arguments:
* input_dir - directory of screenshots with banners that need to be removed
* output_dir - directory where screenshots without the banners will be saved
* new_dimensions - dimensions of the banner to remove


## Authors
* **Brenda Reyes Ayala** 
* **James Sun**
* **Qiufeng Du**
* **Tasbire Saiyera**
## License
todo

## Acknowledgments 
todo