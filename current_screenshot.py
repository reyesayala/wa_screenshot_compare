import argparse
import asyncio
import os
import sqlite3
import csv
import time
import urllib.request
import urllib.error
from pyppeteer import launch
from pyppeteer import errors
import logging
import signal
import re


def screenshot_csv(csv_in_name, csv_out_name, pics_out_path, screenshot_method, timeout_duration, read_range, chrome_args, screensize):
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
    read_range : list
        Contains two int which tell the programs to only take screenshots between these lines in the csv_in.
    chrome_args : list
        Contains extra arguments for chrome that can be passed into pyppeteer. None if no additional arguments.
    screensize : list
        Contains two int which are height and width of the browser viewport.
    """

    with open(csv_in_name, 'r') as csv_file_in:
        csv_reader = csv.reader(csv_file_in)
        with open(csv_out_name, 'w+') as csv_file_out:
            csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
            csv_writer.writerow(["archive_id", "url_id", "url", "site_status", "site_message", "screenshot_message"])

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

                archive_id = line[0]
                url_id = line[1]
                url = line[2]

                print("\nurl #{0} {1}".format(url_id, url))
                logging.info("url #{0} {1}".format(url_id, url))

                site_status, site_message, screenshot_message = take_screenshot(archive_id, url_id, url, pics_out_path,
                    screenshot_method, timeout_duration, chrome_args, screensize)

                csv_writer.writerow([archive_id, url_id, url, site_status, site_message, screenshot_message])


def screenshot_db(csv_out_name, make_csv, pics_out_path, screenshot_method, timeout_duration):
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

    """

    print("db not fully implemented")
    return

    cursor.execute("create table if not exists current_index (archiveID int, urlID int, succeed int, "
                   "foreign key(archiveID) references collection_name(archiveID));")
    cursor.execute("delete from current_index;")
    cursor.execute("select * from current_url;")
    connection.commit()
    results = cursor.fetchall()

    if make_csv:
        csv_file_out = open(csv_out_name, "w+")
        csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
        csv_writer.writerow(["archive_id", "url_id", "succeed_code", "current_url"])

    count = 0
    for row in results:
        count += 1
        archive_id = row[0]
        url_id = row[1]
        url = row[2]

        print("\nurl #{0} {1}".format(url_id, url))
        logging.info("url #{0} {1}".format(url_id, url))

        succeed = take_screenshot(str(archive_id), str(url_id), url, pics_out_path, screenshot_method, timeout_duration)

        cursor.execute("insert into current_index values ({0}, {1}, {2});".format(archive_id, url_id, succeed))
        if make_csv:
            csv_writer.writerow([archive_id, url_id, succeed, url])

        connection.commit()
    connection.close()
    if make_csv:
        csv_file_out.close()


def take_screenshot(archive_id, url_id, url, pics_out_path, screenshot_method, timeout_duration, chrome_args, screensize):
    """Calls the function or command to take a screenshot

    Parameters
    ----------
    archive_id : str
        The archive ID.
    url_id : str
        The url ID.
    url : str
        The url to take a screenshot of.
    pics_out_path : str
        Directory to output the screenshots.
    timeout_duration : str
        Duration before timeout when going to each website.
    screenshot_method : int
        Which method to take the screenshots, 0 for chrome, 1 for puppeteer, 2 for cutycapt.
    chrome_args : list
        Contains extra arguments for chrome that can be passed into pyppeteer. None if no additional arguments.
    screensize : list
        Contains two int which are height and width of the browser viewport.

    Returns
    -------
    site_status : str
        LIVE if website can still be reached or is redirected.
        FAIL if not.
    site_message : str
        An error describing why the site can't be reached or a message saying the site was redirected.
    screenshot_message : str
        Message indicating whether the screenshot was successful.

    """

    site_status, site_message = check_site_availability(url)
    if site_status == "FAIL":
        return site_status, site_message, "Screenshot unsuccessful"

    if screenshot_method == 0:
        return site_status, site_message, chrome_screenshot(pics_out_path, archive_id, url_id, url, timeout_duration)
    elif screenshot_method == 2:
        return site_status, site_message, cutycapt_screenshot(pics_out_path, archive_id, url_id, url, timeout_duration)
    elif screenshot_method == 1:
        try:
            loop = asyncio.get_event_loop()
            task = asyncio.gather(puppeteer_screenshot(archive_id, url_id, url, pics_out_path, timeout_duration, chrome_args, screensize))
            result = loop.run_until_complete(task)
            #logging.info(result)
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
        except:
            print("Unknown error")
            logging.info("Unknown error")
            return site_status, site_message, "Unknown error"


def chrome_screenshot(pics_out_path, archive_id, url_id, url, timeout_duration):
    # not fully implemented
    command = "timeout {4}s google-chrome --headless --hide-scrollbars --disable-gpu --noerrdialogs " \
              "--enable-fast-unload --screenshot={0}{1}.{2}.png --window-size=1024x768 '{3}'" \
        .format(pics_out_path, archive_id, url_id, url, timeout_duration)
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
        print("Screenshot unsuccessful")
        return "Screenshot unsuccessful"


def cutycapt_screenshot(pics_out_path, archive_id, url_id, url, timeout_duration):
    # not fully implemented
    command = "timeout {4}s xvfb-run --server-args=\"-screen 0, 1024x768x24\" cutycapt --url='{0}' " \
              "--out={1}{2}.{3}.png --delay=2000".format(url, pics_out_path, archive_id, url_id, timeout_duration)
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


async def puppeteer_screenshot(archive_id, url_id, url, pics_out_path, timeout_duration, chrome_args, screensize):
    """Take screenshot using the pyppeteer package.

    Parameters
    ----------
    archive_id : str
        The archive ID.
    url_id : str
        The url ID.
    url : str
        The url to take a screenshot of.
    pics_out_path : str
        Directory to output the screenshots.
    timeout_duration : str
        Duration before timeout when going to each website.
    chrome_args : list
        Contains extra arguments for chrome that can be passed into pyppeteer. None if no additional arguments.
    screensize : list
        Contains two int which are height and width of the browser viewport.

    References
    ----------
    .. [1] https://pypi.org/project/pyppeteer/

    .. [2] https://github.com/ukwa/webrender-puppeteer/blob/6fcc719d64dc19a4929c02d3a445a8283bee5195/renderer.js

    """

    browser = await launch(headless=True, dumpio=True, args=chrome_args)
    page = await browser.newPage()
    try:
        await page.setViewport({'height': screensize[0], 'width': screensize[1]})
        await page.goto(url, timeout=(timeout_duration * 1000))
        await page.waitFor(1000)
        await page.reload(timeout=(timeout_duration * 1000))    # reloading a site can get rid of certain popups

        await click_button(page, "I Accept")        # click through popups and banners, there could be a lot more
        await click_button(page, "I Understand")
        await click_button(page, "I Agree")
        await click_button(page, "Accept Recommended Settings")
        await click_button(page, "Close")
        await click_button(page, "Close and Accept")
        await click_button(page, "OK")
        await click_button(page, "OK, I Understand.")
        await click_button(page, "Accept")
        await click_button(page, "Accept Cookies")
        await click_button(page, "No Thanks")
        await page.keyboard.press("Escape")

        await page.screenshot(path='{0}{1}.{2}.png'.format(pics_out_path, archive_id, url_id))

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


async def click_button(page, button_text):
    """Execute js script on page to click button

    Parameters
    ----------
    page : pyppeteer.page.Page
        The page to go through
    button_text: str
        Name of the button to click

    References
    ----------
    .. [1] https://github.com/ukwa/webrender-puppeteer/blob/6fcc719d64dc19a4929c02d3a445a8283bee5195/renderer.js

    Notes
    -----
    Right now only clicks popups and banners that are buttons, but some sites have banners with using a or wb_divs


    """
    await page.evaluate('''query => {
      const elements = [...document.querySelectorAll('button')];
      const targetElement = elements.find(e => e.innerText.toLowerCase().includes(query));
      targetElement && targetElement.click();
      }''', button_text.lower())


def check_site_availability(url):
    """Run a request to see if the given url is available.

    Parameters
    ----------
    url : str
        The url to check.

    Returns
    -------
    site_status : str
        LIVE if website can still be reached or is redirected.
        FAIL if not.
    site_message : str
        An error describing why the site can't be reached or a message saying the site was redirected.


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
    except:
        # broad exception for anything else
        print("Unknown error")
        logging.info("Unknown error")
        return "FAIL", "Unknown error"

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
    make_csv : bool
        Whether or not to output a CSV when use_db is True.
    timeout_duration : str
        Duration before timeout when going to each website.
    read_range : list
        Contains two int which tell the programs to only take screenshots between these lines in the csv_in.
    chrome_args : list
        Contains extra arguments for chrome that can be passed into pyppeteer. None if no additional arguments.
    screensize : list
        Contains two int which are height and width of the browser viewport.

    """

    parser = argparse.ArgumentParser()

    #parser.add_argument("--db", type=str, help="Input DB file with urls")

    parser.add_argument("--csv", type=str, help="Input CSV file with current urls")
    parser.add_argument("--picsout", type=str, help="Directory to output the screenshots")
    parser.add_argument("--indexcsv", type=str, help="The CSV file to write the index")
    parser.add_argument("--method", type=int,
                        help="Which method to take the screenshots, 0 for chrome, 1 for puppeteer, 2 for cutycapt")
    parser.add_argument("--timeout", type=str,
                        help="(optional) Specify duration before timeout for each site, in seconds, default 30 seconds")
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

    # some command line argument error checking
    if args.indexcsv is None:
        print("invalid output index file\n")
        exit()
    if args.csv is None:
        print("Must provide input file\n")
        exit()
    if args.picsout is None:
        print("Must specify output path for pictures\n")
        exit()
    if args.method is None:
        print("Must specify screenshot method\n")
        exit()

    pics_out_path = args.picsout + '/'
    screenshot_method = int(args.method)
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

    return csv_in_name, csv_out_name, pics_out_path, screenshot_method, timeout_duration, read_range, chrome_args, screensize

def connect_sql(path):
    """Connects the DB file specified by path."""

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
        datefmt:  format of the date in the message, month-day-year hour:minute:second AM/PM
        level:    minimum message level accepted

    """

    logging.basicConfig(filename=(pics_out_path + "current_screenshot_log.txt"), filemode='a',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S %p', level=logging.INFO)


def signal_handler(sig, frame):
    raise Exception("User interrupted")


def main():
    csv_in_name, csv_out_name, pics_out_path, screenshot_method, timeout_duration, read_range, chrome_args, screensize \
        = parse_args()
    set_up_logging(pics_out_path)
    signal.signal(signal.SIGINT, signal_handler)

    print("Taking screenshots")
    screenshot_csv(csv_in_name, csv_out_name, pics_out_path, screenshot_method, timeout_duration, read_range, chrome_args, screensize)
    # if use_db:
    #     screenshot_db(csv_out_name, make_csv, pics_out_path, screenshot_method, timeout_duration)


main()
