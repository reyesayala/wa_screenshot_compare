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
This program takes a CSV file with the seed website URLs and outputs it into another CSV.
> A valid seed csv file should have the URLs as the first column, other columns are ignored.
> The output CSV file will have three columns, archive ID, URL ID, and URL.

Command syntax: 
```
python3 read_seed.py --csv=your/directory/Collection-seed-list.csv --db=urls.db --out=current_urls.csv --ext=1234 --name="Collection Name" --sort
```
Arguments:
* csv - The CSV file with the seed URLs. 
* db - The DB file to store the URLs. DEPRECATED
* out - The CSV file to write the URLs.
* ext - ID of the archive.
* name - Name of the archive.
* sort - (optional) Include to sort the output.

### create-archive_urls.py
This program takes the CSV from read_seed.py and gets the Archive-It archive URL.  
> The output CSV file will have three columns, archive ID, URL ID, and URL.

Command syntax: 
```
python3 create_archive_urls.py --csv=current_urls.csv --out=archive_urls.csv --banner
```
Or
```
python3 create_archive_urls.py --db=urls.db --out=archive_urls.csv --banner
```
Arguments:
* csv - Input CSV file with current URLs. 
* db - Input DB file with URLs, output is automatically inserted in db. DEPRECATED
* out - The CSV file to write the URLs.
* banner - (optional) Include to generate URLs that has the banner, default removes banner.

### current_screenshot.py
This program takes the CSV with the current website URLS and takes screenshots. The output CSV will have six columns: archive ID, URL ID, URL, site status, site message, and screenshot message: 
* site_status - Contains 'LIVE' if the URL can be reached or redirects, and 'FAIL' if the URL could not be reached (ex. 404).
* site_message - A reason on why site_status was 'LIVE' or 'FAIL'. Such as 'Redirected to http://......' or 'HTTPError: 404'.
* screenshot_message - a message on whether the screenshot was successful. If site_status is 'FAIL' then screenshot_message is automatically 'Screenshot unsuccessful'. Another common message is 'Navigation Timeout Exceeded'.
> As of right now, method=0 and 2 are deprecated

Command syntax: 
```
python3 current_screenshot.py --csv=current_urls.csv --picsout=current_pics/ --indexcsv=current_index.csv --method=1 --timeout=30 --range=0,1000 --chrome-args="--no-sandbox" --screen-size=768,1024 --keep-cookies
```
Arguments:
* csv - Input CSV file with current URLs. 
* picsout - Directory to output the screenshots.
* indexcsv - The CSV file to write the index.
* method - Which method to take the screenshots, 0 for chrome, 1 for puppeteer, 2 for cutycapt.
* timeout - (optional) Specify duration before timeout for each site, in seconds, default 30 seconds.
* range - (optional) Specify to take screenshots between these lines, inclusive. Syntax: low,high. ex. 0,1000. default takes screenshots of everything.
* chrome-args - (optional) Additional arguments for pyppeteer chrome. ex. --args="--disable-gpu --no-sandbox".
* screen-size - (optional) Specify to take screenshots of size, affects browser viewport too. Syntax: height,width. ex 600,800. default size is 768,1024.
* keep-cookies  - (optional) Specify to NOT remove cookies banners. Dafault removes cookies banners.

### archive_screenshot.py
This program takes the CSV with the archive website URLS and takes screenshots. The output CSV will have seven columns, archive ID, URL ID, capture date, URL, site status, site message, and screenshot message.
* site_status - Contains 'LIVE' if the URL can be reached or redirects, and 'FAIL' if the URL could not be reached (ex. 404).
* site_message - A reason on why site_status was 'LIVE' or 'FAIL'. Such as 'Redirected to http://......' or 'HTTPError: 404'.
* screenshot_message - a message on whether the screenshot was successful. If site_status is 'FAIL' then screenshot_message is automatically 'Screenshot unsuccessful'. Another common message is 'Navigation Timeout Exceeded'.
> As of right now, method=0 and 2 are deprecated

Command syntax:
```
python3 archive_screenshot.py --csv=archive_urls.csv  --picsout=archive_pics/ --indexcsv=archive_index.csv --method=1 --timeout=30 --range=0,1000 --chrome-args="--no-sandbox" --screen-size=768,1024 --keep-cookies
```
Arguments:
* csv - Input CSV file with archive URLs. 
* picsout - Directory to output the screenshots.
* indexcsv - The CSV file to write the index.
* method - Which method to take the screenshots, 0 for chrome, 1 for puppeteer, 2 for cutycapt.
* timeout - (optional) Specify duration before timeout for each site, in seconds, default 30 seconds.
* range - (optional) Specify to take screenshots between these lines, inclusive. Syntax: low,high. ex. 0,1000. default takes screenshots of everything.
* chrome-args - (optional) Additional arguments for pyppeteer chrome. ex. --args="--disable-gpu --no-sandbox".
* screen-size - (optional) Specify to take screenshots of size, affects browser viewport too. Syntax: height,width. ex 600,800. default size is 768,1024.
* keep-cookies  - (optional) Specify to NOT remove cookies banners. Dafault removes cookies banners.

### get_file_names.py
This program outputs a CSV file which maps the current and archive URLs with their respective screenshots.
> The output CSV will have four columns, current URl, archive URL, current screenshot file name, archive screenshot file name.

Command syntax:
```
python3 get_file_names.py --currcsv=current_index.csv --archcsv=archive_index.csv --out=file_names.csv --print
```
Or
```
python3 get_file_names.py --db=urls.db --out=file_names.csv --print
```
Arguments:
* currcsv - The CSV file with the current screenshots index.
* archcsv - The CSV file with the archive screenshots index.
* db - Input DB file with urls. DEPRECATED
* out - The CSV file to write the urls and file names. 
* print - (optional) Include to print urls and file names to stdout, default doesn't print.

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
python3 crop_banners_from_images.py --input_dir=pics_archived_banners/ --output_dir=pics_archived_no_banners/ --new_dimensions=0,43,1024,768
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
