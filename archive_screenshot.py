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


def screenshot_csv(csv_in_name, csv_out_name, pics_out_path, screenshot_method, timeout_duration, lazy, be_lazy):
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

    """

    with open(csv_in_name, 'r') as csv_file_in:
        csv_reader = csv.reader(csv_file_in)
        with open(csv_out_name, 'w+') as csv_file_out:
            csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
            csv_writer.writerow(["archive_id", "url_id", "date", "succeed_code", "archive_url"])

            count = 0
            compare = '0'
            for line in csv_reader:
                if count == 0:      # skip the header
                    count += 1
                    continue

                archive_id = str(line[0])
                url_id = line[1]
                date = line[2]
                url = line[3]

                if url == "":
                    continue

                if be_lazy is True:  # makes running faster by not doing hundreds of archive sites
                    if url_id != compare:
                        count = 0
                        compare = url_id
                    else:
                        count += 1
                        if count > lazy:
                            continue

                print("\nurl #{0} {1}".format(url_id, url))
                logging.info("url #{0} {1}".format(url_id, url))

                succeed = take_screenshot(archive_id, url_id, date, url, pics_out_path, screenshot_method,
                                          timeout_duration)

                csv_writer.writerow([archive_id, url_id, date, succeed, url])


def screenshot_db(csv_out_name, pics_out_path, screenshot_method, make_csv, timeout_duration, lazy, be_lazy):
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

   """

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

        succeed = take_screenshot(archive_id, url_id, date, url, pics_out_path, screenshot_method, timeout_duration)

        cursor.execute("insert into archive_index values ({0}, {1}, '{2}', {3});"
                       .format(archive_id, url_id, date, succeed))
        if make_csv:
            csv_writer.writerow([archive_id, url_id, date, succeed, url])

        connection.commit()

    connection.close()

    if make_csv:
        csv_file_out.close()


def take_screenshot(archive_id, url_id, date, url, pics_out_path, screenshot_method, timeout_duration):
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

    Returns
    -------
    str(succeed) : str
        A code indicating whether how successful the screenshot was

    """

    return_code = check_site_availability(url)
    if return_code != 200 and return_code != 302:
        return return_code

    # command which takes the screenshots
    command = ""
    if screenshot_method == 0:
        command = "timeout {5}s google-chrome --headless --hide-scrollbars --disable-gpu --noerrdialogs " \
                  "--enable-fast-unload --screenshot={0}{1}.{2}.{3}.png --window-size=1024x768 '{4}'"\
            .format(pics_out_path, archive_id, url_id, date, url, timeout_duration)

    elif screenshot_method == 2:
        command = "timeout {5}s xvfb-run --server-args=\"-screen 0, 1024x768x24\" " \
                  "cutycapt --url='{0}' --out={1}{2}.{3}.{4}.png --delay=2000"\
            .format(url, pics_out_path, archive_id, url_id, date, timeout_duration)

    elif screenshot_method == 1:
        try:
            asyncio.get_event_loop().run_until_complete(
                puppeteer_screenshot(archive_id, url_id, date, url, pics_out_path, timeout_duration))
            logging.info("Screenshot successful")
            print("Screenshot successful")
            return 200
        except errors.TimeoutError as e:
            print(e)
            logging.info(e)
            return -1
        except errors.NetworkError as e:
            print(e)
            logging.info(e)
            return -2
        except errors.PageError as e:
            print(e)
            logging.info(e)
            return -3
        except Exception as e:
            print(e)
            return -4
    else:
        pass  # assumes the user entered 0,1,2 as method

    try:
        if os.system(command) == 0:
            succeed = 200
            logging.info("Screenshot successful")
        else:
            logging.info("Screenshot unsuccessful")
            succeed = -5
    except:
        logging.info("Screenshot unsuccessful")
        succeed = -6
    time.sleep(1)  # xvfb needs time to rest

    return str(succeed)


async def puppeteer_screenshot(archive_id, url_id, date, url, pics_out_path, timeout_duration):
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

    References
    ----------
    .. [1] https://pypi.org/project/pyppeteer/

    """

    browser = await launch()
    page = await browser.newPage()
    await page.setViewport({'height': 768, 'width': 1024})
    await page.goto(url, timeout=(int(timeout_duration) * 1000))
    await page.screenshot(path='{0}{1}.{2}.{3}.png'.format(pics_out_path, archive_id, url_id, date))
    await browser.close()


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
        print('HTTPError: {}'.format(e.code))
        logging.info('HTTPError: {}'.format(e.code))
        return int(e.code)
    except urllib.error.URLError as e:
        # Not an HTTP-specific error (e.g. connection refused)
        print('URLError: {}'.format(e.reason))
        logging.info('URLError: {}'.format(e.reason))
        return -7
    except Exception as e:
        # other reasons such as "your connection is not secure"
        print(e)
        logging.info(e)
        return -8

    # check if redirected
    if conn.geturl() != url:
        print("Redirected to {}".format(conn.geturl()))
        logging.info("Redirected to {}".format(conn.geturl()))
        return 302

    # reaching this point means it received code 200
    print("Return code 200")
    logging.info("Return code 200")
    return 200


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

    parser.add_argument("--csv", type=str, help="Input CSV file with Archive urls")
    parser.add_argument("--db", type=str, help="Input DB file with urls")
    parser.add_argument("--picsout", type=str, help="Path of directory to output the screenshots")
    parser.add_argument("--indexcsv", type=str, help="The CSV file to write the index")
    parser.add_argument("--method", type=int, help="Which method to take the screenshots, "
                                                   "0 for chrome, 1 for puppeteer, 2 for cutycapt")
    parser.add_argument("--timeout", type=str, help="(optional) Specify duration before timeout, "
                                                    "in seconds, default 30 seconds")
    parser.add_argument("--lazy", type=int, help="(optional) Continues to the next archive after taking n pictures")

    args = parser.parse_args()

    # some error checking
    if args.csv is not None and args.indexcsv is None:
        print("invalid output index file\n")
        exit()
    if args.csv is None and args.db is None:
        print("Must provide input file\n")
        exit()
    if args.csv is not None and args.db is not None:
        print("must only use only one type of input file\n")
        exit()
    if args.picsout is None:
        print("Must specify output path for pictures")
        exit()
    if args.method is None:
        print("Must specify screenshot method\n")
        exit()

    pics_out_path = args.picsout + '/'
    screenshot_method = int(args.method)

    if args.csv is not None:
        csv_in_name = args.csv
        use_csv = True
    else:
        use_csv = False

    if args.db is not None:
        connect_sql(args.db)
        use_db = True
    else:
        use_db = False

    if args.indexcsv is not None:
        csv_out_name = args.indexcsv
        make_csv = True
    else:
        make_csv = False

    if args.timeout is None:
        timeout_duration = "30"
    else:
        timeout_duration = args.timeout

    if args.lazy is not None:
        be_lazy = True
        lazy = int(args.lazy)
    else:
        be_lazy = False
        lazy = None

    return csv_in_name, csv_out_name, pics_out_path, screenshot_method, use_csv, use_db, make_csv, \
        timeout_duration, lazy, be_lazy


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
        datefmt:  format of the date in the message
        level:    minimum message level accepted

    """

    logging.basicConfig(filename=(pics_out_path + "archive_screenshot_log.txt"), filemode='a',
                        format='%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S',
                        level=logging.INFO)


def main():
    csv_in_name, csv_out_name, pics_out_path, screenshot_method, use_csv, use_db, make_csv, timeout_duration, lazy, \
        be_lazy = parse_args()
    set_up_logging(pics_out_path)
    print("Taking screenshots")
    if use_csv:
        screenshot_csv(csv_in_name, csv_out_name, pics_out_path, screenshot_method, timeout_duration, lazy, be_lazy)
    if use_db:
        screenshot_db(csv_out_name, pics_out_path, screenshot_method, make_csv, timeout_duration, lazy, be_lazy)


main()
