import argparse
import json
import sqlite3
import csv
import os
import re

def create_with_csv(traces_in_path, csv_out_name):
    """Fetches trace files from directory and extracts network requests urls.
       Stores the results in a CSV file.

    Parameters
    ----------
    traces_in_path : str
        Path to directory containing trace files.
    csv_out_name : str
        The CSV file to write the network requests urls.

    References
    ----------
    .. [1] https://michaljanaszek.com/blog/test-website-performance-with-puppeteer

    """

    print("Creating with csv...")

    with open(csv_out_name, 'w+') as csv_file_out:
        csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
        csv_writer.writerow(["archive_id", "url_id", "date", "network_requests_urls", "priority"])

        for filename in os.listdir(traces_in_path):
            file_components = re.split(r'[.]', filename) # Filename is structured as: archiveid.urlid.date.json
            path = traces_in_path + filename

            archive_id = file_components[0]
            url_id = file_components[1]
            date = file_components[2]

            print("Extracting data from {}".format(filename))

            with open(path) as trace_file:
                data = json.load(trace_file)

                # count = 0

                for element in data['traceEvents']:
                    if element['cat'] == 'devtools.timeline' and\
                       element['name'] == 'ResourceSendRequest' and\
                       'url' in element['args']['data']:
                        # count += 1
                        url = element['args']['data']['url']
                        priority = element['args']['data']['priority']
                        csv_writer.writerow([archive_id, url_id, date, url, priority])

                # print(count)   
                # input()

def create_with_db(traces_in_path):
    """Fetches trace files from directory and extracts network requests urls. 
       Stores the results in a database table.

    Parameters
    ----------
    traces_in_path : str
        Path to directory containing trace files.

    """

    print("Creating with db...")
    
    for filename in os.listdir(traces_in_path):
        file_components = re.split(r'[.]', filename)

        path = traces_in_path + filename

        archive_id = file_components[0]
        url_id = file_components[1]
        date = file_components[2]

        print("extracting data from {}".format(filename))

        with open(path) as trace_file:
            data = json.load(trace_file)

            for element in data['traceEvents']:
                if element['cat'] == 'devtools.timeline' and\
                   element['name'] == 'ResourceSendRequest' and\
                   'url' in element['args']['data']:
                    
                    url = element['args']['data']['url']
                    priority = element['args']['data']['priority']

                    cursor.execute(
                        'INSERT INTO archive_network_requests VALUES ({0}, {1}, "{2}", "{3}", "{4}");'\
                                    .format(archive_id, url_id, date, url, priority))

    connection.commit()
    connection.close()

def parse_args():
    """Parses the arguments passed in from the command line.

    Returns
    -------
    traces_in_path : str
        The directory where the trace files are located.
    csv_out_name : str
        The CSV file to write the network requests urls.
    use_csv : bool
        Whether or not to output data as a csv file.
    use_db : bool
        Whether or not to output data to a db file.

    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--tracesin", type=str, help="Directory where traces files located")
    parser.add_argument("--out", type=str, help="The CSV file to write the network requests urls")
    parser.add_argument("--db", type=str, help="Output DB where network requests would be stored")

    args = parser.parse_args()

    # Some command line argument error checking
    if args.tracesin is None:
        print("Must specify input path to trace files\n")
        exit()

    if args.db is None and args.out is None:
        print("Must specify output location\n")
        exit()

    if args.out is not None:
        use_csv = True
    else:
        use_csv = False

    if args.db is not None:
        connect_sql(args.db)
        use_db = True
    else:
        use_db = False

    return args.tracesin, args.out, use_csv, use_db

def connect_sql(path):
    """Connects database and creates connection

    Parameter
    ---------
    path : str
        Path to database file.

    References
    ----------

    .. [1] https://pythonexamples.org/python-sqlite3-check-if-table-exists/


    """ 
    
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()

    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='collection_name'")

    if cursor.fetchone()[0] == 1:
        cursor.execute("CREATE TABLE IF NOT EXISTS archive_network_requests (archiveID INT, urlID INT, "
                       "date TEXT, networkURL TEXT, priority TEXT, FOREIGN KEY (archiveID) REFERENCES "
                       "collection_name(archiveID));")
        connection.commit()
    
        cursor.execute("SELECT DISTINCT archiveID FROM archive_network_requests;")
        connection.commit()
        results = cursor.fetchall()

        for row in results:
            cursor.execute("DELETE FROM archive_network_requests WHERE archiveID = {};".format(row[0]))
        connection.commit()

    else:
        print("Missing table aborting...")
        connection.close()
        exit()

def main():
    traces_in_path, csv_out_name, use_csv, use_db = parse_args()

    print("Extracting network requests...")
    if use_csv:
        create_with_csv(traces_in_path, csv_out_name)
    if use_db:
        create_with_db(traces_in_path)

main()
