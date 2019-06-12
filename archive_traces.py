import argparse
import csv
import asyncio
import sqlite3
import urllib.request
import urllib.error
import logging
import time
import os
from pyppeteer import launch
from pyppeteer import errors

def create_with_csv(csv_in_name, csv_out_name, trace_out_path, timeout_duration):
    """Extracts a trace file using the input csv file with current urls.
    
    Parameters
    ----------
    csv_in_name : str
        The CSV file with the archive urls.
    csv_out_name : str
        The CSV file to write the extraction status of the urls.
    trace_out_path : str
        The directory to store the trace files.
    timeout_duration : str
        Duration before timeout when going to each website.

    """

    with open(csv_in_name, 'r') as csv_file_in:
        csv_reader = csv.reader(csv_file_in)
        with open(csv_out_name, 'w+') as csv_file_out:
            csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
            csv_writer.writerow(["archive_id", "url_id", "archive_url", "site_status", "site_message", "extraction_message"])

            # Skip the header of the CSV
            next(csv_reader)

            for line in csv_reader:
                archive_id = line[0]
                url_id = line[1]
                date = line[2]
                url = line[3]

                print("url #{0} {1}".format(url_id, url))
                logging.info("url #{0} {1}".format(url_id, url))

                site_status, site_message, extraction_message = extract_traces(url, archive_id, url_id, trace_out_path, timeout_duration)

                csv_writer.writerow([archive_id, url_id, url, site_status, site_message, extraction_message])

def create_with_db(csv_out_name, trace_out_path, timeout_duration, make_csv):
    """Extracts trace files using the input database file with archive urls.

    Parameters
    ----------
    csv_out_name : str
        The CSV file to write the extracton status of the urls.
    trace_out_path : str
        The directory to store the trace files.
    timeout_duration : str
        Duration before timeout when going to each website.
    make_csv : bool
        Whether or not to also output a CSV file.

    """

    cursor.execute("SELECT * FROM archive_urls;")
    connection.commit()
    results = cursor.fetchall()

    if make_csv:
        csv_file_out = open(csv_out_name, "w+")
        csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
        csv_writer.writerow(["archive_id", "url_id", "archive_url", "site_status", "site_message", "extraction_message"])
    
    for row in results:
        archive_id = str(row[0])
        url_id = str(row[1])
        date = row[2]
        url = row[3]

        print("url #{0} {1}".format(url_id, url))
        logging.info("url #{0} {1}".format(url_id, url))

        site_status, site_message, extraction_message = extract_traces(url, archive_id, url_id, date, trace_out_path, timeout_duration)

        if make_csv:
            csv_writer.writerow([archive_id, url_id, url, site_status, site_message, extraction_message])

        cursor.execute('INSERT INTO archive_trace_status VALUES ({0}, {1}, "{2}", "{3}", "{4}", "{5}")'\
                      .format(archive_id, url_id, url, site_status, site_message, extraction_message))

    connection.commit()
    connection.close()

def extract_traces(url, archive_id, url_id, date, trace_out_path, timeout_duration):
    """Fetches url from input CSV and extract trace file
    
    Parameters
    ----------
    url : str
        The archive url to create a trace file.
    archive_id : str
        The archive ID.
    url_id : str
        The url ID.
    date : str
        The date of the archive capture.
    trace_out_path : str
        The directory to store the trace files.
    timeout_duration : str
        Duration before timeout when going to each website.

    """

    site_status, site_message = check_site_availability(url)

    if site_status == "FAIL":
        return site_status, site_message, "Extraction unsuccessful"
    elif site_status == "REDIRECT":
        return site_status, site_message, "Extraction unsuccessful"

    try:
        #loop = asyncio.new_event_loop()
        #asyncio.set_event_loop(loop)
        #asyncio.ensure_future(puppeteer_extract_trace(url, archive_id, url_id, trace_out_path, timeout_duration, loop))
        #loop.run_forever()

        asyncio.get_event_loop().run_until_complete(
                puppeteer_extract_trace(url, archive_id, url_id, date, trace_out_path, timeout_duration))

        print("Extraction successful")
        return site_status, site_message, "Extraction successful"
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

async def puppeteer_extract_trace(url, archive_id, url_id, date, trace_out_path, timeout_duration):
    """Create trace file using the pyppeteer package.
    
    Parameters
    ----------
    url : str
        The url to create a trace file.
    archive_id : str
        The archive ID.
    url_id : str
        The url ID.
    date : str
        The date of the archive capture.
    trace_out_path : str
        The directory to store the trace files.
    timeout_duration : str
        Duration before timeout when going to each website.

    References
    ----------
    .. [1] https://pypi.org/project/pyppeteer/

    .. [2] https://michaljanaszek.com/blog/test-website-performance-with-puppeteer

    """

    browser = await launch(headless=True)#, loop=loop)
    page = await browser.newPage()
    
    trace_path = '{}trace.json'.format(trace_out_path)

    # Begins tracing and waits until all content loaded before stopping trace
    try:
        await page.setViewport({'height': 768, 'width': 1024})
        await page.tracing.start({'path': trace_path})
        await page.goto(url, {'waitUntil': ['domcontentloaded'], \
                              'timeout': int(timeout_duration) * 1000})
        await page.tracing.stop()
        
        os.rename(trace_path, '{0}{1}_{2}_{3}.json'.format(trace_out_path, archive_id, url_id, date))

    except Exception as e:
        try:
            await page.close()
            await browser.close()
            #await loop.stop()
        except:
            await browser.close()
            #await loop.stop()
        raise e

    try:
        await page.close()
        await browser.close()
        #await loop.stop()
    except:
        await browser.close()
        #await loop.stop()

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

    """

    try:
        conn = urllib.request.urlopen(url)
    except urllib.error.URLError as e:
        error_message = 'URLError: {}'.format(e.reason)
        print(error_message)
        logging.info(error_message)
        return "FAIL", error_message
    except urllib.error.HTTPError as e:
        error_message = 'HTTPError: {}'.format(e.code)
        print(error_message)
        logging.info(error_message)
        return "FAIL", error_message
    except Exception as e:
        error_message = 'Other: {}'.format(e)
        print(error_message)
        logging.info(error_message)
        return "FAIL", error_message

    # Check if request was a redirect
    if conn.geturl() != url:
        print("Redirected to {}".format(conn.geturl()))
        logging.info("Redirected to {}".format(conn.geturl()))
        return "REDIRECT", "Redirected to {}".format(conn.geturl())

    # Successful connection: code 200
    print("Successfully connected to {}".format(url))
    logging.info("Successful connection to {}".format(url))
    return "LIVE", "Successful connection to {}".format(url)                

def parse_args():
    """Parse the arguments passed to in from the commandline

    Returns
    -------
    csv_in_name : str
        The CSV file containing archive urls.
    csv_out_name : str
        The CSV file to store the extraction status of archive urls.
    trace_out_path : str
        The directory to store the trace files.
    use_csv : bool
        Whether or not to output as csv.
    use_db : bool
        Whether or not to output as db.
    timeout_duration: : str
        Duration before timeout when attempting to connect to a website.
    make_csv : nool
        Whether or not to output a CSV when use_db is True.

    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--out", type=str, help="The CSV file to write the urls")
    parser.add_argument("--db", type=str, help="The DB file to store the urls")
    parser.add_argument("--csv", type=str, help="Input CSV file with archive urls")
    parser.add_argument("--tracesout", type=str, help="(Optional)Specify directory to output the trace files, default creates new folder named 'atraces' in current directory")
    parser.add_argument("--timeout", type=str, help="(Optional) Specify duration before timeout for each site, in seconds, default 30 seconds")

    args = parser.parse_args()

    # Error checking
    if args.csv is None and args.db is None:
        print("Must include input file\n")
        exit()

    if args.csv is not None and args.db is not None:
        print("Must only specify one type of input file\n")
        exit()

    if args.csv is not None and args.out is None:
        print("Must specify output file\n")
        exit()

    if args.tracesout is None:
        try :
            os.mkdir("atraces")
            path = "atraces/"
        except FileExistsError:
            print("'atraces' directory already exists, aborting...")
            exit()
    else:
        path = args.tracesout

    if args.db is not None:
        connect_sql(args.db)
        use_db = True
    else:
        use_db = False

    if args.csv is not None:
        use_csv = True
    else:
        use_csv = False

    if args.out is not None:
        make_csv = True
    else:
        make_csv = False

    if args.timeout is None:
        timeout_duration = "30"
    else:
        timeout_duration = args.timeout

    return args.csv, args.out, path, timeout_duration, use_csv, use_db, make_csv

def connect_sql(path):
    """Connect the database file, and creates the necessary tables.

    Parameters
    ----------
    path : str
        The path to the database file.

    """

    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    
    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='archive_urls'")

    if cursor.fetchone()[0] == 1:
        cursor.execute("CREATE TABLE IF NOT EXISTS archive_trace_status (archiveID INT, urlID INT, "
                       "url TEXT, siteStatus TEXT, siteMessage TEXT, extractionMessage TEXT, "
                       "FOREIGN KEY (archiveID) REFERENCES collection_name(archiveID));")
        connection.commit()

        cursor.execute("SELECT DISTINCT archiveID from archive_trace_status;")
        connection.commit()
        results = cursor.fetchall()

        for row in results:
            cursor.execute("DELETE FROM archive_trace_status WHERE archiveID = {};".format(row[0]))
        connection.commit()

    else:
        print("Missing table aborting...")
        connection.close()
        exit()

def set_up_logging():
    """Setting up logging format.

    Notes
    -----
    logging parameters:
        filename: The file to output the logs
        filemode: a as in append
        format:   Format of the message
        datefmt:  Format of the date in the message, month-day-year hour:minute:second AM/PM
        level:    Minimum message level accepted

    """

    logging.basicConfig(filename="archive_traces_log.txt", filemode='a',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S %p', level=logging.INFO)

def main():
    csv_in_name, csv_out_name, trace_out_path, timeout_duration, use_csv, use_db, make_csv = parse_args()
    set_up_logging()

    print("Extracting trace files...")
    if use_csv:
        create_with_csv(csv_in_name, csv_out_name, trace_out_path, timeout_duration)
    if use_db:
        create_with_db(csv_out_name, trace_out_path, timeout_duration, make_csv)

main()

