# README FILE

# This is the documentation for the scripts that take
# screenshots from current and archived instances of
# websites and compares the two screenshots.


# This code operates within a test environment made for this task
# Activating the test environment
# anaconda:
    # activate python3 environment:
        # conda activate envname
    # deactivate environment:
        # conda deactivate
    # create environment:
        # conda create --name name python=... ...
    # list existing environments:
        # conda info --env


# INSTRUCTIONS FOR RUNNING PROGRAM IN THE BACKGROUND
# run program in background:
    # example: nohup python3 program.py -a=1 -b=2 .. > output.txt & nohup
    # > output.txt - outputs the console output to the specified file
	# &            - runs process in the background
    # nohup        - including this at the front of a command will cause the process to ignore SIGHUP,
		             so closing the connection to the server will not terminate the process


# STEP ONE: FETCH CURRENT SITE URLS FROM SEED FILES
# read_seed.py
    # command syntax: python3 read_seed.py --csv=your/directory/here/Collection\ seed-list.csv
	                   --out=current_urls.txt --db=urls.db --ext=1234 --sort --name="Collection Name"

	# Arguments:
		# --csv  - the input file with all of the seed urls
		# --db   - output db file to write the urls
		# --out  - output txt file to write the urls
		# --ext  - a number that is the id of the archive
		# --name - name of the archive, enclose with "" if name contains escapable characters
		# --sort - (optional) include this to sort the output alphabetically

    # This program parses the seed list csv from Ualberta archives and will
    # output the data into the specified db or file. The output with urls is then
    # used as the input for create_archive_urls.py and current_screenshot.py

    # A valid seed csv file should have the urls as the first column, other columns are ignored


# STEP TWO: CREATE ARCHIVE URLS FROM THE URLS OUTPUTTED BY read_seed.py
# create_archive_urls.py
	# command syntax: python3 create_archive_urls.py --db=urls.db --txt=current_urls.txt --out=archive_urls.txt --banner
	# Arguments:
		# --db     - input db file with current urls
		# --txt    - input txt file with urls
		# --out    - output txt file to write the urls
		# --banner - (optional) include this to keep the banner on archive sites

    # This program opens the output of read_seed.py,
    # uses the data in the db or txt file to create urls that
    # archive_screenshot.py will use to take screenshots,
    # and outputs it into the same database or a text file.
    # The output of this file will be used to take screenshots from the ARCHIVED SITES.


# STEP THREE: TAKE A SCREENSHOT OF CURRENT WEBPAGES
# current_screenshot.py
	# command syntax: python3 current_screenshot.py --txt=current_urls.txt --db=urls.db --picsout=pics_current/
	                      --indexout=current_index.txt --method=0 --timeout=30

	# Arguments:
		# --txt      - input txt file with the urls
		# --db       - input db file with the urls
		# --picsout  - directory where the pictures will be stored
		# --indexout - file to write the generated index into
		# --method   - method to take the screenshot, 0 for chrome, 1 for puppeteer, 2 for cutycapt
		# --timeout  - (optional) specify duration before timeout, in seconds, default 30 seconds

	# This program takes screenshots using the urls from the input file, 
	# index information is stored in the .db file or as a .txt file in the same directory as
	# the screenshots. The screenshots are saved as .png files.

	# Issues:
        # A common warning with chrome is the .service file cant be found,
        # (this doesnt cause many problems however I'm not sure how to fix it)
		# urllib is used to check the return code of a website before a screenshot is taken
		# and there have been cases where a site can load but still returns a 404
		# redirects, http errors, url errors are noted in the log file
		# in general, it's better to take screenshots of current webpages using pyppeteer
        

# STEP FOUR: TAKE A SCREENSHOT OF THE ARCHIVED WEBPAGES
# archive_screenshot.py
	# command syntax: python3 archive_screenshot.py --db=urls.db --txt=archive_urls.txt
	                      --picsout=pics_archive/ --indexout=archive_index.txt --chrome --timeout --lazy=50

	# Arguments:
		# --txt      - input txt file with the urls
		# --db       - input db file with the urls
		# --picsout  - directory where the pictures will be stored
		# --indexout - file to write the generated index into
		# --method   - method to take the screenshot, 0 for chrome, 1 for puppeteer, 2 for cutycapt
		# --timeout  - (optional) specify duration before timeout, in seconds, default 30 seconds
		# --lazy     - (optional) specify the max number of screenshots to take for one archive, default takes screenshot of all

	# issues:
        # some archive webpages dont ever load which means waiting the entire duration of the timeout
		# in general it's better to take screenshots of archive webpages using chrome


# STEP FIVE: GET THE FILE NAME OF ALL THE SCREENSHOTS
# get_file_names.py
    # command syntax: python3 get_file_names.py --db=urls.db --atxt=archive_urls.txt --ntxt=current_urls.txt
                      --out=filenames.csv --print

    # Arguments:
		# --db    - input db file with the screenshot index
        # --atxt  - input txt file with the archive screenshot index
        # --ntxt  - input txt file with the current screenshot index
        # --out   - csv file to write the output to
        # --print - (optional) include this to print result to stdout

    # The output csv file will contain: current website url, archive website url, current screenshot name, archive screenshot name
    # if the website is down or screenshot failed then their url will not be included in here


# STEP SIX: CALCULATE SIMILARITY SCORES
# calculate_similarity.py, similarity_measures.py
    # command syntax: python3 calculate_similarities.py --csv=filenames.csv --cpics=pics_current/ --apics=archive_pics/
                      --out=scores.txt --ssim --mse --print

    # Arguments:
        # --csv   - input csv file with the urls and image names
        # --cpics - directory with images of the current website screenshots
        # --apics - directory with images of the archive website screenshots
        # --out   - file to output the results and scores
        # --print - (optional) include this to print results and scores in stdout
        # --ssim  - (optional) include this to calculate the ssim scores
        # --mse   -


# To Do Items and General Issues:
	# There may be more cases where there are problems with the url which
	# causes the program to take a screenshot of a archive-it page-not-found.
		# This was only found recently when I looked through some of the pictures.
		# Possible Cause: The '&'' character needed escaping (could be more).

	# Some archives have hundreds of captures while most have only a handful.
	# It might be better to be selective when it comes to taking
	# screenshots of archives with many captures as
	# this will save a lot of time running archive_screenshot.py

	# youtube doesnt load well (except with puppeteer)

	# anaconda sometimes crashes, twice it has happened, dont know why, i just reran and it worked

	# puppeteer has trouble taking screenshots of archived sites
