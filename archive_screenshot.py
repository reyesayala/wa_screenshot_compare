import argparse
import os
import sqlite3
import time
import csv
import asyncio
import urllib.request
import urllib.error
from pyppeteer import launch
from pyppeteer import errors
import logging
import signal
import re


def screenshot_csv(csv_in_name, csv_out_name, pics_out_path, screenshot_method, timeout_duration, banner, read_range, chrome_args, screensize):
    """Fetches urls from the input CSV and takes a screenshot

    Parameters
    ----------
    csv_in_name : str
        The CSV file with the current urls.
    csv_out_name : str
        The CSV file to write the index.
    pics_out_path : str
        Directory to output the screenshots.
    screenshot_method : int
        Which method to take the screenshots, 0 for chrome, 1 for puppeteer, 2 for cutycapt.
    timeout_duration : str
        Duration before timeout when going to each website.
    lazy : int
        The max number of archive captures to take a screenshot of before moving on.
    be_lazy : bool
        Whether or not to take a maximum of screenshots per archive capture.
    banner : bool
        Whether or not to remove the Archive-It banner

    """

    with open(csv_in_name, 'r') as csv_file_in:
        csv_reader = csv.reader(csv_file_in)
        with open(csv_out_name, 'w+') as csv_file_out:
            csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
            csv_writer.writerow(
                ["archive_id", "url_id", "date", "url", "site_status", "site_message", "screenshot_message"])

            line_count = 0
            next(csv_reader)  # skip header
            while True:
                try:
                    line = next(csv_reader)
                except StopIteration:
                    break
                line_count += 1

                if read_range is not None:  # skip if not within range
                    if line_count < read_range[0] or line_count > read_range[1]:
                        continue

                archive_id = str(line[0])
                url_id = line[1]
                date = line[2]
                url = line[3]

                if url == "":
                    continue

                # if be_lazy is True:  # makes running faster by not doing hundreds of archive sites
                #     if url_id != compare:
                #         count = 0
                #         compare = url_id
                #     else:
                #         count += 1
                #         if count > lazy:
                #             continue

                print("\nurl #{0} {1}".format(url_id, url))
                logging.info("url #{0} {1}".format(url_id, url))

                site_status, site_message, screenshot_message = take_screenshot(archive_id, url_id, date, url,
                    pics_out_path, screenshot_method, timeout_duration, banner, chrome_args, screensize)

                csv_writer.writerow([archive_id, url_id, date, url, site_status, site_message, screenshot_message])


def screenshot_db(csv_out_name, pics_out_path, screenshot_method, make_csv, timeout_duration, lazy, be_lazy, banner):
    """Fetches urls from the input DB and takes a screenshot

    Parameters
    ----------
    csv_out_name : str
        The CSV file to write the index.
    make_csv : bool
        Whether or not to output a CSV when use_db is True.
    pics_out_path : str
        Directory to output the screenshots.
    screenshot_method : int
        Which method to take the screenshots, 0 for chrome, 1 for puppeteer, 2 for cutycapt.
    timeout_duration : str
        Duration before timeout when going to each website.
    lazy : int
        The max number of archive captures to take a screenshot of before moving on.
    be_lazy : bool
        Whether or not to take a maximum of screenshots per archive capture.
    banner : bool
        Whether or not to remove the Archive-It banner

   """

    print("db not fully implemented")
    return

    cursor.execute("create table if not exists archive_index (archiveID int, urlID int, date text, succeed int, "
                   "foreign key(archiveID) references collection_name(archiveID));")
    cursor.execute("delete from archive_index;")
    cursor.execute("select * from archive_urls where url is not null;")
    connection.commit()
    results = cursor.fetchall()

    if make_csv:
        csv_file_out = open(csv_out_name, "w+")
        csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
        csv_writer.writerow(["archive_id", "url_id", "date", "succeed_code", "archive_url"])

    count = 0
    compare = '0'
    for row in results:
        url_id = row[1]

        if be_lazy is True:  # makes running faster by not doing hundreds of archive site
            if url_id != compare:
                count = 0
                compare = url_id
            else:
                count += 1
                if count > lazy:
                    continue

        archive_id = row[0]
        date = row[2]
        url = row[3]

        print("\nurl #{0} {1}".format(url_id, url))
        logging.info("url #{0} {1}".format(url_id, url))

        succeed = take_screenshot(archive_id, url_id, date, url, pics_out_path, screenshot_method,
                                  timeout_duration, banner)

        cursor.execute("insert into archive_index values ({0}, {1}, '{2}', {3});"
                       .format(archive_id, url_id, date, succeed))
        if make_csv:
            csv_writer.writerow([archive_id, url_id, date, succeed, url])

        connection.commit()

    connection.close()

    if make_csv:
        csv_file_out.close()


def take_screenshot(archive_id, url_id, date, url, pics_out_path, screenshot_method, timeout_duration, banner, chrome_args, screensize):
    """Calls the function or command to take a screenshot

    Parameters
    ----------
    archive_id : str
        The archive ID.
    url_id : str
        The url ID.
    date : str
        The date of the archive capture.
    url : str
        The url to take a screenshot of.
    pics_out_path : str
        Directory to output the screenshots.
    timeout_duration : str
        Duration before timeout when going to each website.
    screenshot_method : int
        Which method to take the screenshots, 0 for chrome, 1 for puppeteer, 2 for cutycapt.
    banner : bool
        Whether or not to remove the Archive-It banner

    Returns
    -------
    str(succeed) : str
        A code indicating whether how successful the screenshot was

    """

    site_status, site_message = check_site_availability(url)
    if site_status == "FAIL":
        return site_status, site_message, "Screenshot unsuccessful"

    if screenshot_method == 0:
        return site_status, site_message, chrome_screenshot(pics_out_path, archive_id, url_id, date, url, timeout_duration)
    elif screenshot_method == 2:
        return site_status, site_message, cutycapt_screenshot(pics_out_path, archive_id, url_id, date, url, timeout_duration)

    elif screenshot_method == 1:
        try:
            asyncio.get_event_loop().run_until_complete(
                puppeteer_screenshot(archive_id, url_id, date, url, pics_out_path, timeout_duration, banner, chrome_args, screensize))
            logging.info("Screenshot successful")
            print("Screenshot successful")
            return site_status, site_message, "Screenshot successful"
        except errors.TimeoutError as e:
            print(e)
            logging.info(e)
            return site_status, site_message, e
        except errors.NetworkError as e:
            print(e)
            logging.info(e)
            return site_status, site_message, e
        except errors.PageError as e:
            print(e)
            logging.info(e)
            return site_status, site_message, e
        except Exception as e:
            print(e)
            logging.info(e)
            return site_status, site_message, e
        except asyncio.futures.InvalidStateError as e:
            print(e)
            logging.info(e)
            return site_status, site_message, e
        except asyncio.streams.IncompleteReadError as e:
            print(e)
            logging.info(e)
            return site_status, site_message, e

    return None, None, None  # assumes the user entered 0,1,2 as method


async def puppeteer_screenshot(archive_id, url_id, date, url, pics_out_path, timeout_duration, banner, chrome_args, screensize):
    """Take screenshot using the pyppeteer package.

    Parameters
    ----------
    archive_id : str
        The archive ID.
    url_id : str
        The url ID.
    date : str
        The date of the archive capture.
    url : str
        The url to take a screenshot of.
    pics_out_path : str
        Directory to output the screenshots.
    timeout_duration : str
        Duration before timeout when going to each website.
    banner : bool
        Whether or not to remove the Archive-It banner

    References
    ----------
    .. [1] https://pypi.org/project/pyppeteer/

    """

    browser = await launch(headless=True, dumpio=True, args=chrome_args)
    page = await browser.newPage()
    try:
        await page.setViewport({'height': screensize[0], 'width': screensize[1]})
        await page.goto(url, timeout=(timeout_duration * 1000))

        if not banner:
            await remove_banner(page)        # edit css of page to remove archive-it banner

        await page.screenshot(path='{0}{1}.{2}.{3}.png'.format(pics_out_path, archive_id, url_id, date))

    except Exception as e:
        # https://github.com/GoogleChrome/puppeteer/issues/2269
        try:
            await page.close()
            await browser.close()
        except:
            await browser.close()
        raise e

    try:
        await page.close()
        await browser.close()
    except:
        await browser.close()


def chrome_screenshot(pics_out_path, archive_id, url_id, date, url, timeout_duration):
    command = "timeout {5}s google-chrome --headless --hide-scrollbars --disable-gpu --noerrdialogs " \
              "--enable-fast-unload --screenshot={0}{1}.{2}.{3}.png --window-size=1024x768 '{4}'" \
        .format(pics_out_path, archive_id, url_id, date, url, timeout_duration)
    try:
        if os.system(command) == 0:
            logging.info("Screenshot successful")
            print("Screenshot successful")
            return "Screenshot successful"
        else:
            logging.info("Screenshot unsuccessful")
            print("Screenshot unsuccessful")
            return "Screenshot unsuccessful"
    except:  # unknown error
        logging.info("Screenshot unsuccessful")
        return "Screenshot unsuccessful"


def cutycapt_screenshot(pics_out_path, archive_id, url_id, date, url, timeout_duration):
    command = "timeout {5}s xvfb-run --server-args=\"-screen 0, 1024x768x24\" " \
              "cutycapt --url='{0}' --out={1}{2}.{3}.{4}.png --delay=2000" \
        .format(url, pics_out_path, archive_id, url_id, date, timeout_duration)
    try:
        time.sleep(1)  # cutycapt needs to rest
        if os.system(command) == 0:
            logging.info("Screenshot successful")
            print("Screenshot successful")
            return "Screenshot successful"
        else:
            logging.info("Screenshot unsuccessful")
            print("Screenshot unsuccessful")
            return "Screenshot unsuccessful"
    except:  # unknown error
        logging.info("Screenshot unsuccessful")
        print("Screenshot unsuccessful")
        return "Screenshot unsuccessful"


async def remove_banner(page):
    """Execute js script on page to click button

        Parameters
        ----------
        page : pyppeteer.page.Page
            The page to go through

        References
        ----------
        .. [1] https://github.com/ukwa/webrender-puppeteer/blob/6fcc719d64dc19a4929c02d3a445a8283bee5195/renderer.js

        """
    await page.evaluate('''query => {
      const elements = [...document.querySelectorAll('wb_div')];
      const targetElement = elements.find(e => e.style.display.includes(query));
      targetElement.style.display = "none";
      }''', "block")


def check_site_availability(url):
    """Run a request to see if the given url is available.

    Parameters
    ----------
    url : str
        The url to check.

    Returns
    -------
    200 if the site is up and running
    302 if it was a redirect
    -7  for URL errors
    ?   for HTTP errors
    -8  for other error

    References
    ----------
    .. [1] https://stackoverflow.com/questions/1726402/in-python-how-do-i-use-urllib-to-see-if-a-website-is-404-or-200


    """

    try:
        conn = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        # Return code error (e.g. 404, 501, ...)
        error_message = 'HTTPError: {}'.format(e.code)
        print(error_message)
        logging.info(error_message)
        return "FAIL", error_message
    except urllib.error.URLError as e:
        # Not an HTTP-specific error (e.g. connection refused)
        error_message = 'URLError: {}'.format(e.reason)
        print(error_message)
        logging.info(error_message)
        return "FAIL", error_message
    except Exception as e:
        # other reasons such as "your connection is not secure"
        print(e)
        logging.info(e)
        return "FAIL", e

    # check if redirected
    if conn.geturl() != url:
        print("Redirected to {}".format(conn.geturl()))
        logging.info("Redirected to {}".format(conn.geturl()))
        return "LIVE", "Redirected to {}".format(conn.geturl())

    # reaching this point means it received code 200
    print("Return code 200")
    logging.info("Return code 200")
    return "LIVE", "Return code 200"


def parse_args():
    """Parses the arguments passed in from the command line.

    Returns
    ----------
    csv_in_name : str
        The CSV file with the current urls.
    csv_out_name : str
        The CSV file to write the index.
    pics_out_path : str
        Directory to output the screenshots.
    screenshot_method : int
        Which method to take the screenshots, 0 for chrome, 1 for puppeteer, 2 for cutycapt.
    use_db : bool
        Whether or not the input is a DB.
    use_csv : bool
        Whether or not the input is a CSV.
    make_csv : bool
        Whether or not to output a CSV when use_db is True.
    timeout_duration : str
        Duration before timeout when going to each website.
    lazy : int
        The max number of archive captures to take a screenshot of before moving on.
    be_lazy : bool
        Whether or not to take a maximum of screenshots per archive capture.

    """

    parser = argparse.ArgumentParser()

    #parser.add_argument("--db", type=str, help="Input DB file with urls")
    #parser.add_argument("--lazy", type=int, help="(optional) Continues to the next archive after taking n pictures")

    parser.add_argument("--csv", type=str, help="Input CSV file with Archive urls")
    parser.add_argument("--picsout", type=str, help="Path of directory to output the screenshots")
    parser.add_argument("--indexcsv", type=str, help="The CSV file to write the index")
    parser.add_argument("--method", type=int,
                        help="Which method to take the screenshots, 0 for chrome, 1 for puppeteer, 2 for cutycapt")
    parser.add_argument("--timeout", type=str,
                        help="(optional) Specify duration before timeout, in seconds, default 30 seconds")
    parser.add_argument("--banner", action='store_true',
                        help="(optional) Include to keep banner, default removes banner")
    parser.add_argument("--range", type=str,
                        help="(optional) Specify to take screenshots between these lines, inclusive. "
                             "Syntax: low,high. ex. 0,1000. default takes screenshots of everything.")
    parser.add_argument("--chrome-args", type=str,
                        help="(optional) Additional arguments for pyppeteer chrome. "
                             "ex. --args=\"--disable-gpu --no-sandbox\"")
    parser.add_argument("--screen-size", type=str,
                        help="(optional) Specify to take screenshots of size, affects browser viewport too. "
                             "Syntax: height,width. ex 600,800. default size is 768,1024")
    args = parser.parse_args()

    # some error checking
    if args.indexcsv is None:
        print("invalid output index file\n")
        exit()
    if args.csv is None:
        print("Must provide input file\n")
        exit()
    if args.picsout is None:
        print("Must specify output path for pictures")
        exit()
    if args.method is None:
        print("Must specify screenshot method\n")
        exit()

    pics_out_path = args.picsout + '/'
    screenshot_method = int(args.method)
    banner = args.banner
    csv_in_name = args.csv
    csv_out_name = args.indexcsv

    # if args.db is not None:
    #     connect_sql(args.db)
    #     use_db = True
    # else:
    #     use_db = False

    timeout_duration = args.timeout
    if timeout_duration is None:
        timeout_duration = 30
    else:
        try:
            timeout_duration = int(args.timeout)
        except:
            print("Invalid format for timeout")
            exit()

    read_range = args.range
    if read_range is not None:
        try:
            temp = read_range.split(",")
            read_range = [int(temp[0]), int(temp[1])]
            assert read_range[0] <= read_range[1]
        except:
            print("Invalid format for range")
            exit()

    chrome_args = args.chrome_args
    if chrome_args is not None:
        try:
            chrome_args = re.sub(" +", " ", chrome_args)
            chrome_args = chrome_args.strip().split(" ")
            assert len(chrome_args) >= 1
        except:
            print("Invalid format for args")
            exit()

    screensize = args.screen_size
    if screensize is None:
        screensize = [768, 1024]
    else:
        try:
            temp = args.screen_size.split(",")
            screensize = [int(temp[0]), int(temp[1])]
        except:
            print("Invalid format for screensize")
            exit()

    # if args.lazy is not None:
    #     be_lazy = True
    #     lazy = int(args.lazy)
    # else:
    #     be_lazy = False
    #     lazy = None

    return csv_in_name, csv_out_name, pics_out_path, screenshot_method, timeout_duration, banner, read_range, chrome_args, screensize


def connect_sql(path):
    """Connects the DB file. """

    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    connection.commit()


def set_up_logging(pics_out_path):
    """Setting up logging format.

    Parameters
    ----------
    pics_out_path : str
        Directory to output the screenshots.

    Notes
    -----
    logging parameters:
        filename: the file to output the logs
        filemode: a as in append
        format:   format of the message
        datefmt:  format of the date in the message, date-month-year hour:minute:second AM/PM
        level:    minimum message level accepted

    """

    logging.basicConfig(filename=(pics_out_path + "archive_screenshot_log.txt"), filemode='a',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S %p', level=logging.INFO)


def signal_handler(sig, frame):
    raise Exception("User interrupted")


def main():
    csv_in_name, csv_out_name, pics_out_path, screenshot_method, timeout_duration, banner, read_range, \
        chrome_args, screensize = parse_args()
    set_up_logging(pics_out_path)
    signal.signal(signal.SIGINT, signal_handler)

    print("Taking screenshots")
    # if use_csv:
    screenshot_csv(csv_in_name, csv_out_name, pics_out_path, screenshot_method, timeout_duration, banner, read_range, chrome_args, screensize)
    # if use_db:
    # screenshot_db(csv_out_name, pics_out_path, screenshot_method, make_csv, timeout_duration, lazy, be_lazy, banner)


if __name__ == "__main__":
    main()
