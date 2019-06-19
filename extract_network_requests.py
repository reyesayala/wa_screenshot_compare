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

class Writer:
    """
    Base writer class which handles writing CSV files

    ...

    Attributes
    ----------
    file_name : str
        The CSV file name where info is output to.
    rows : list 
        Contains the elements to be inputted to the CSV file.
    use_archive : bool
        Whether or not the input is archive seeds. True is archive seeds, False is current seeds.

    Methods
    -------
    finalize()
        Writes the elements inside rows to the CSV file.

    References
    ----------
    .. [1] https://stackoverflow.com/questions/47026335/in-python-is-it-safe-to-pass-csv-file-writer-objects-between-classes

    """

    def __init__(self, file_name, use_archive):
        """
        Parameters
        ----------
        file_name : str
            The CSV file name where info is output to.
        rows : list
            Contains the elements to be inputted to the CSV file.
        use_archive : bool
            Whether or not the input is archive seeds. True is archive seeds, False is current seeds.

        """

        self.file_name = file_name
        self.rows = []
        self.use_archive = use_archive

    def finalize(self):
        """Writes the elements inside rows to the CSV file."""

        with open(self.file_name, 'w+') as csv_file_out:
            csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
            
            for row in self.rows:
                csv_writer.writerow(row)

class CSVWriter(Writer):
    """
    Inherits from Writer class, this class handles the creation of the CSV file containing
    the network requests.

    ...

    Methods
    -------
    initialize()
        Appends the header info to rows.
    writerow(archive_id, url_id, url, status_code)
        Appends CSV element to rows.

    """

    def initialize(self):
        """Appends the header info to rows."""

        if self.use_archive:
            self.rows.append(["archive_id", "url_id", "date", "url", "status_code"])
        else:
            self.rows.append(["archive_id", "url_id", "url", "status_code"])

    def writerow(self, archive_id, url_id, url, status_code, date=None):
        """Appends CSV element to rows.

        Parameters
        ----------
        archive_id : str
            The archive ID.
        url_id : str
            The url ID.
        url : str
            The network request url.
        status_code : str
            The status code of the network request url.
        date : str
            The date of the archive url. Default is None if current url.

        """
        
        if self.use_archive:
            self.rows.append([archive_id, url_id, date, url, status_code])
        else:
            self.rows.append([archive_id, url_id, url, status_code])

class IndexWriter(Writer):
    """
    Inherits from Writer class, this class handles the creation of the CSV file containing
    the extraction status of each url from the seed list.

    ...

    Methods
    -------
    initialize()
        Appends the header info to rows.
    writerow()
        Appends CSV element to rows.

    """

    def initialize(self):
        """Appends the header info to rows."""

        if self.use_archive:
            self.rows.append(["archive_id", "url_id", "date", "archive_url", \
                              "site_status", "site_message", "extraction_message"])
        else:
            self.rows.append(["archive_id", "url_id", "current_url", \
                              "site_status", "site_message", "extraction_message"])
    
    def writerow(self, archive_id, url_id, url, site_status, site_message, extraction_message, date=None):
        """Appends CSV element to rows.

        Parameters
        ----------
        archive_id : str
            The archive ID.
        url_id : str
            The url ID.
        url : str
            The current url from the input CSV file (or db).
        site_status : str
            The status of the current url (LIVE, FAIL, or REDIRECT).
        site_message : str
            The success/error message from the site.
        extraction_message : str
            The success/error message indicating whether or not extraction of network requests was a
            success or failure.
        date : str
            The date of the archive url. Default is None if current url.

        """
    
        if self.use_archive:
            self.rows.append([archive_id, url_id, date, url, site_status, \
                    site_message, extraction_message])
        else:
            self.rows.append([archive_id, url_id, url, site_status, site_message, extraction_message])

def create_with_csv(csv_in_name, csv_out_name, csv_index_name, timeout_duration, use_archive):
    """Extracts network requests using the input CSV with seed urls.
    
    Parameters
    ----------
    csv_in_name : str
        The CSV file with the seed urls.
    csv_out_name : str
        The CSV file to write the network request urls.
    csv_index_name : str
        The CSV file to write the extraction status.
    timeout_duration : str
        Duration before timeout when going to each website.
    use_archive : bool
        Whether or not the input is archive seeds. True is archive seeds, False is current seeds.

    """

    with open(csv_in_name, 'r') as csv_file_in:
        csv_reader = csv.reader(csv_file_in)
            
        index_writer = IndexWriter(csv_index_name, use_archive)
        csv_writer = CSVWriter(csv_out_name, use_archive)

        # Append header info to CSV files
        index_writer.initialize()
        csv_writer.initialize()

        # Skip the header of the CSV
        next(csv_reader)

        for row in csv_reader:
            archive_id = row[0]
            url_id = row[1]

            if use_archive:
                date = row[2]
                url = row[3]
            else:
                date = None
                url = row[2]

            print("url #{0} {1}".format(url_id, url))
            logging.info("url #{0} {1}".format(url_id, url))

            site_status, site_message, extraction_message = extract_requests(csv_writer, url, archive_id, url_id, timeout_duration, date)

            #if use_archive:
            index_writer.writerow(archive_id, url_id, url, site_status, \
                    site_message, extraction_message, date)
            #else:
             #   index_writer.writerow(archive_id, url_id, url, site_status, \
              #          site_message, extraction_message)
    
        # Write elements to CSV file
        index_writer.finalize()
        csv_writer.finalize()

def create_with_db(csv_out_name, csv_index_name, timeout_duration, make_csv, use_archive):
    """Extracts network requests using the input database file with seed urls.

    Parameters
    ----------
    csv_out_name : str
        The CSV file to write the network request urls.
    csv_index_name : str
        The CSV file to write the extraction status.
    timeout_duration : str
        Duration before timeout when going to each website.
    make_csv : bool
        Whether or not to also output a CSV file.
    use_archive : bool
        Whether or not the input is archive seeds. True is archive seeds, False is current seeds.

    """

    if use_archive:
        cursor.execute("SELECT * FROM archive_urls;")
    else:
        cursor.execute("SELECT * FROM current_urls;")

    connection.commit()
    results = cursor.fetchall()

    csv_writer = CSVWriter(csv_out_name, use_archive)
    index_writer = IndexWriter(csv_index_name, use_archive)

    if make_csv:
        # Append header info to CSV files
        csv_writer.initialize()
        index_writer.initialize()
    
    for row in results:
        archive_id = str(row[0])
        url_id = str(row[1])

        if use_archive:
            date = row[2]
            url = row[3]
        else:
            date = None
            url = row[2]

        print("url #{0} {1}".format(url_id, url))
        logging.info("url #{0} {1}".format(url_id, url))

        site_status, site_message, extraction_message = extract_requests(csv_writer, url, archive_id, url_id, timeout_duration, date)

        if make_csv:
            index_writer.writerow(archive_id, url_id, url, site_status, \
                    site_message, extraction_message, date)

        if use_archive:
            cursor.execute('INSERT INTO archive_extraction_status VALUES ({0}, {1}, "{2}", '
                           '"{3}", "{4}", "{5}", "{6}")'.format(archive_id, url_id, date, url, \
                                                         site_status, site_message, extraction_message))
        else:
            cursor.execute('INSERT INTO current_extraction_status VALUES ({0}, {1}, "{2}", '
                           '"{3}", "{4}", "{5}")'.format(archive_id, url_id, url, \
                                                  site_status, site_message, extraction_message))

    if make_csv:
        csv_writer.finalize()
        index_writer.finalize()

    # Skips header element in rows
    csv_elements_no_header = iter(csv_writer.rows)
    next(csv_elements_no_header, None)

    # Append elements to database
    for element in csv_elements_no_header:
        if use_archive:
            cursor.execute('INSERT INTO archive_network_requests VALUES ({0}, {1}, "{2}", "{3}", "{4}")'\
                           .format(element[0], element[1], element[2], element[3], element[4]))
        else:
            cursor.execute('INSERT INTO current_network_requests VALUES ({0}, {1}, "{2}", "{3}")'\
                           .format(element[0], element[1], element[2], element[3]))

    # Commit and close database
    connection.commit()
    connection.close()

def extract_requests(csv_writer, url, archive_id, url_id, timeout_duration, date):
    """Fetches url from input CSV and extract network requests 
    
    Parameters
    ----------
    csv_writer : CSVWriter
        CSVWriter object which handles the creation of the CSV file containing the network requests.
    url : str
        The url to extract network requests.
    archive_id : str
        The archive ID.
    url_id : str
        The url ID.
    timeout_duration : str
        Duration before timeout when going to each website.
    date : str
        The date of the archive url.

    """

    site_status, site_message, url = check_site_availability(url)

    if site_status == "FAIL":
        return site_status, site_message, "Extraction unsuccessful"

    try:
        asyncio.get_event_loop().run_until_complete(
                puppeteer_extract_requests(csv_writer, url, archive_id, url_id, timeout_duration, date))

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

async def puppeteer_extract_requests(csv_writer, url, archive_id, url_id, timeout_duration, date):
    """Create trace file using the pyppeteer package.
    
    Parameters
    ----------
    csv_writer : CSVWriter
        CSVWriter object which handles the creation of the CSV containing the network requests.
    url : str
        The url where network requests are extracted..
    archive_id : str
        The archive ID.
    url_id : str
        The url ID.
    timeout_duration : str
        Duration before timeout when going to each website.
    date : str
        The date of the archive url.

    References
    ----------
    .. [1] https://pypi.org/project/pyppeteer/

    .. [2] https://github.com/miyakogi/pyppeteer/issues/140

    """

    browser = await launch(headless=True)

    # Intercepts network requests
    async def handle_request(request):
        await request.continue_()

    # Intercepts network responses
    async def handle_response(response, csv_writer, archive_id, url_id, date):
        csv_writer.writerow(archive_id, url_id, response.url, response.status, date)
        # print("Response => url: {0}, status code: {1}".format(response.url, response.status))

    page = await browser.newPage()

    try:    
        await page.setRequestInterception(True)

        page.on('request', lambda req: asyncio.ensure_future(handle_request(req)))
        page.on('response', lambda res: asyncio.ensure_future(handle_response(res, csv_writer, \
                                                                              archive_id, url_id, date)))
        
        response = await page.goto(url, {'waitUntil': ['networkidle0'], \
                                         'timeout': int(timeout_duration) * 1000})
        #input()

    except Exception as e:
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
        return "FAIL", error_message, url
    except urllib.error.HTTPError as e:
        error_message = 'HTTPError: {}'.format(e.code)
        print(error_message)
        logging.info(error_message)
        return "FAIL", error_message, url
    except Exception as e:
        error_message = 'Other: {}'.format(e)
        print(error_message)
        logging.info(error_message)
        return "FAIL", error_message, url

    # Check if request was a redirect
    if conn.geturl() != url:
        print("Redirected to {}".format(conn.geturl()))
        logging.info("Redirected to {}".format(conn.geturl()))
        return "REDIRECT", "Redirected to {}".format(conn.geturl()), conn.geturl()

    # Successful connection: code 200
    print("Successfully connected to {}".format(url))
    logging.info("Successful connection to {}".format(url))
    return "LIVE", "Successful connection to {}".format(url), url                

def parse_args():
    """Parse the arguments passed to in from the commandline

    Returns
    -------
    csv_in_name : str
        The CSV file containing current urls.
    csv_out_name : str
        The CSV file to store the network requests of current urls.
    csv_index_name : str
        The CSV file to store the extraction status of current urls.
    use_csv : bool
        Whether or not to output as csv.
    use_db : bool
        Whether or not to output as db.
    timeout_duration: : str
        Duration before timeout when attempting to connect to a website.
    make_csv : bool
        Whether or not to output a CSV when use_db is True.
    use_archive : bool
        Whether or not the input is archive seeds. True is archive seeds, False is current seeds.

    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--out", type=str, help="The CSV file to write the urls")
    parser.add_argument("--index", type=str, help="The CSV file to write the extraction status of urls")
    parser.add_argument("--db", type=str, help="The DB file to store the urls")
    parser.add_argument("--csv", type=str, help="Input CSV file with current urls")
    parser.add_argument("--timeout", type=str, help="(Optional) Specify duration before timeout for each site, in seconds, default 30 seconds")
    parser.add_argument("--archive", action="store_true", help="Include to specify input as archive seeds. Do not include if collection is current seeds.")

    args = parser.parse_args()

    # Error checking
    if args.csv is None and args.db is None:
        print("Must include input file\n")
        exit()

    if args.csv is not None and args.db is not None:
        print("Must only specify one type of input file\n")
        exit()

    if args.csv is not None and args.out is None and args.index is None:
        print("Must specify output file\n")
        exit()

    if args.db is not None:
        connect_sql(args.db, args.archive)
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

    return args.csv, args.out, args.index, timeout_duration, use_csv, use_db, make_csv, args.archive

def connect_sql(path, use_archive):
    """Connect the database file, and creates the necessary tables.

    Parameters
    ----------
    path : str
        The path to the database file.
    use_archive : bool
        Whether or not the input is archive seeds. True is archive seeds, False is current seeds.

    """

    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()

    if use_archive:
        cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='archive_urls'")
        
        if cursor.fetchone()[0] == 1:
            # Create database tables
            cursor.execute("CREATE TABLE IF NOT EXISTS archive_extraction_status (archiveID INT, "
                           "urlID INT, date TEXT, url TEXT, siteStatus TEXT, siteMessage TEXT, "
                           "extractionMessage TEXT, FOREIGN KEY (archiveID) REFERENCES "
                           "collection_name(archiveID));")

            cursor.execute("CREATE TABLE IF NOT EXISTS archive_network_requests (archiveID INT, "
                           "urlID INT, date TEXT, url TEXT, statusCode TEXT, FOREIGN KEY (archiveID) "
                           "REFERENCES collection_name(archiveID));")
            connection.commit()

            # Fetch all archive IDs being worked on in archive urls
            cursor.execute("SELECT DISTINCT archiveID from archive_urls;")
            connection.commit()
            results = cursor.fetchall()

            # Remove old results from database corresponding to archive ID in archive urls
            for row in results:
                cursor.execute("DELETE FROM archive_extraction_status WHERE archiveID = {};"\
                        .format(row[0]))
                cursor.execute("DELETE FROM archive_network_requests WHERE archiveID = {};"\
                        .format(row[0]))
            connection.commit()

        else:
            print("Missing table aborting...")
            connection.close()
            exit()

    else:
        cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='current_urls'")

        if cursor.fetchone()[0] == 1:
            # Create database tables
            cursor.execute("CREATE TABLE IF NOT EXISTS current_extraction_status (archiveID INT, "
                           "urlID INT, url TEXT, siteStatus TEXT, siteMessage TEXT, extractionMessage "
                           "TEXT, FOREIGN KEY (archiveID) REFERENCES collection_name(archiveID));")

            cursor.execute("CREATE TABLE IF NOT EXISTS current_network_requests (archiveID INT, "
                           "urlID INT, url TEXT, statusCode TEXT, FOREIGN KEY (archiveID) REFERENCES "
                           "collection_name(archiveID));")
            connection.commit()

            # Fetch all archive IDs being worked on in current urls
            cursor.execute("SELECT DISTINCT archiveID from current_urls;")
            connection.commit()
            results = cursor.fetchall()

            # Remove old results from database corresponding to archive ID in current urls
            for row in results:
                cursor.execute("DELETE FROM current_extraction_status WHERE archiveID = {};"\
                        .format(row[0]))
                cursor.execute("DELETE FROM current_network_requests WHERE archiveID = {};"\
                        .format(row[0]))
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

    logging.basicConfig(filename="extraction_log.txt", filemode='a',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S %p', level=logging.INFO)

def main():
    csv_in_name, csv_out_name, csv_index_name, \
            timeout_duration, use_csv, use_db, make_csv, use_archive = parse_args()
    set_up_logging()

    print("Extracting network requests...")
    if use_csv:
        create_with_csv(csv_in_name, csv_out_name, csv_index_name, timeout_duration, use_archive)
    if use_db:
        create_with_db(csv_out_name, csv_index_name, timeout_duration, make_csv, use_archive)

main()

