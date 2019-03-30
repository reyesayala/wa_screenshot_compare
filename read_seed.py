import argparse
import csv
import sqlite3


def parse_csv(csv_in_name, csv_out_name, do_sort, extension, use_db, use_csv):
    """Reads the input seed file and writes the urls to the output files

    Parameters
    ----------
    csv_in_name : str
        Input CSV file with the seed urls.
    csv_out_name : str
        The DB file to store the urls.
    do_sort : bool
        Whether or not the output is sorted.
    extension : str
        The archive ID.
    use_db : bool
        Whether or not to output as db.
    use_csv : bool
        Whether or not to output as csv.

    """

    url_list = []
    with open(csv_in_name, 'r') as csv_file_in:
        csv_reader = csv.reader(csv_file_in)
        count = 0
        for line in csv_reader:
            if count == 0:
                count = 1
                continue
            url_list.append(line[0])

    if do_sort:
        url_list = sorted(url_list)

    if use_csv:
        csv_file_out = open(csv_out_name, 'w+')
        csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
        csv_writer.writerow(["archive_id", "url_id", "current_url"])

    count = 0
    for url in url_list:
        count += 1
        if use_csv:
            csv_writer.writerow([extension, str(count), url])
        if use_db:
            cursor.execute(
                "INSERT OR REPLACE INTO current_urls VALUES ({0}, {1}, '{2}');".format(extension, count, url))

    if use_csv:
        csv_file_out.close()
    if use_db:
        connection.commit()
        connection.close()


def parse_args():
    """Parses the arguments passed in from the command line.

    Returns
    -------
    csv_in_name : str
        The CSV file with the seed urls.
    csv_out_name : str
        The CSV file to store the urls.
    do_sort : bool
        Whether or not the output is sorted.
    extension : str
        The archive ID.
    use_db : bool
        Whether or not to output as db.
    use_csv : bool
        Whether or not to output as csv.

    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, help="The CSV file with the seed urls")
    parser.add_argument("--db", type=str, help="The DB file to store the urls")
    parser.add_argument("--out", type=str, help="The CSV file to write the urls")
    parser.add_argument("--ext", type=str, help="ID of the archive")
    parser.add_argument("--name", type=str, help="Name of the archive")
    parser.add_argument("--sort", action='store_true', help="(optional) Include to sort the output")

    args = parser.parse_args()

    # some error checks
    if args.csv is None:
        print("Must include an input CSV file\n")
        exit() 
    if args.db is None and args.out is None:            # two outputs are allowed
        print("Must specify output file(s)\n")
        exit()
    if args.ext is None:
        print("Must specify archive extension\n")
        exit()
    if args.name is None:
        print("must specify archive name\n")
        exit()

    csv_in_name = args.csv
    do_sort = args.sort
    extension = args.ext
    archive_name = args.name

    if args.db is not None:
        connect_sql(args.db, extension, archive_name)
        use_db = True
    else:
        use_db = False

    if args.out is not None:
        csv_out_name = args.out
        use_csv = True
    else:
        use_csv = False

    return csv_in_name, csv_out_name, do_sort, extension, use_db, use_csv


def connect_sql(path, extension, archive_name):
    """Creates or connects the DB file and create the necessary tables.

    Parameters
    ----------
    path : str
        The DB file to store the urls.
    extension : str
        The archive ID.
    archive_name : str
        The archive name.

    """

    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS collection_name (archiveID INT PRIMARY KEY, name TEXT);")
    cursor.execute("INSERT OR REPLACE INTO collection_name VALUES ({0}, '{1}');".format(extension, archive_name))
    cursor.execute("CREATE TABLE IF NOT EXISTS current_urls (archiveID INT, urlID INT, url TEXT, "
                   "FOREIGN KEY (archiveID) REFERENCES collection_name(archiveID));")
    cursor.execute("DELETE FROM current_urls WHERE archiveID = {0};".format(extension))
    connection.commit()
    

def main():
    csv_in_name, csv_out_name, do_sort, extension, use_db, use_csv = parse_args()
    print("Parsing csv...\n")
    parse_csv(csv_in_name, csv_out_name, do_sort, extension, use_db, use_csv)


main()
