import sqlite3
import argparse
import csv


def open_with_db(csv_out_name, do_print):
    """Gets the url and file names using a sql query and writing it to CSV

    Parameters
    ----------
    csv_out_name : str
        The CSV file to write the urls and file names.
    do_print : bool
        Whether or not to print the results to stdout.

    """

    cursor.execute("select urln.urln, urla.url, inda.archiveID, inda.urlID, inda.date, inda.succeed, indn.succeed" +
                   "from current_index indn, archive_index inda, current_urls urln, archive_urls urla " +
                   "where indn.archiveID = inda.archiveID " +
                   "and indn.archiveID = urln.archiveID " +
                   "and indn.archiveID = urla.archiveID " +
                   "and indn.urlID = inda.urlID " +
                   "and indn.urlID = urln.urlID " +
                   "and indn.urlID = urla.urlID "
                   "and (indn.succeed = 200 or inda.succeed = 200) "
                   "and (indn.succeed = 302 or inda.succeed = 302)"
                   ";")

    fetchall = cursor.fetchall()

    with open(csv_out_name, 'w+') as csv_file_out:
        csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
        csv_writer.writerow(["current_url", "archive_url", "current_file_name", "archive_file_name"])
        
        for row in fetchall:
            [current_url, archive_url, archive_id, url_id, date] = row
            current_filename = "{0}.{1}.png".format(archive_id, url_id)
            archive_filename = "{0}.{1}.{2}.png".format(archive_id, url_id, date)
            csv_writer.writerow([current_url, archive_url, current_filename, archive_filename])

            if do_print:
                print("{0}|{1}|{2}|{3}".format(current_url, archive_url, current_filename, archive_filename))

    connection.close()


def open_with_csv(curr_csv_name, arch_csv_name, csv_out_name, do_print):
    """Parses both index files line by line and writes the urls and file names to the output file.

    Parameters
    ----------
    curr_csv_name : str
        The CSV file with the current screenshot index.
    arch_csv_name : str
        The CSV file with the archive screenshots index.
    csv_out_name : str
        The CSV file to write the urls and file names.
    do_print : bool
        Whether or not to print the results to stdout.

    """

    with open(curr_csv_name, "r") as curr_csv_file:
        curr_csv_reader = csv.reader(curr_csv_file)
        with open(arch_csv_name, "r") as arch_csv_file:
            arch_csv_reader = csv.reader(arch_csv_file)

            with open(csv_out_name, "w+") as csv_file_out:
                csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
                csv_writer.writerow(["current_url", "archive_url", "current_file_name", "archive_file_name"])

                next(curr_csv_reader)       # skip header
                next(arch_csv_reader)
                crow = next(curr_csv_reader)       # a single row in the current index file
                arow = next(arch_csv_reader)

                # goes through both files and gets info row by row
                try:
                    while True:  # how to check EOF in csv?

                        [carchive_id, curl_id, curl] = crow[:3]
                        cscreenshot_status = crow[-1]
                        [aarchive_id, aurl_id, adate, aurl] = arow[:4]
                        ascreenshot_status = arow[-1]

                        curl_id = int(curl_id)
                        aurl_id = int(aurl_id)

                        if curl_id > aurl_id or ascreenshot_status != "Screenshot successful":
                            arow = next(arch_csv_reader)
                        elif curl_id < aurl_id or cscreenshot_status != "Screenshot successful":
                            crow = next(curr_csv_reader)
                        else:
                            current_filename = "{0}.{1}.png".format(carchive_id, curl_id)
                            archive_filename = "{0}.{1}.{2}.png".format(aarchive_id, aurl_id, adate)
                            csv_writer.writerow([curl, aurl, current_filename, archive_filename])

                            if do_print:
                                print("{0}, {1}, {2}, {3}".format(curl, aurl, current_filename, archive_filename))

                            arow = next(arch_csv_reader)

                except StopIteration:
                    pass


def connect_sql(path):
    """Connects the DB file. """

    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    connection.commit()


def parse_args():
    """Parses the command line arguments

    Returns
    -------
    use_csv : bool
        Whether or not the input is a CSV.
    use_db : bool
        Whether or not the input is a DB.
    curr_csv_name : str
        The CSV file with the current screenshot index.
    arch_csv_name : str
        The CSV file with the archive screenshots index.
    csv_out_name : str
        The CSV file to write the urls and file names.
    do_print : bool
        Whether or not to print the results to stdout.

    """

    parser = argparse.ArgumentParser()

    # initializing every line switch
    parser.add_argument("--currcsv", type=str, help="The CSV file with the current screenshots index")
    parser.add_argument("--archcsv", type=str, help="The CSV file with the archive screenshots index")
    parser.add_argument("--db", type=str, help="Input DB file with urls")
    parser.add_argument("--out", type=str, help="The CSV file to write the urls and file names")
    parser.add_argument("--print", action='store_true',
                        help="(optional) Include to print urls and file names to stdout, default doesn't print")

    args = parser.parse_args()

    # some parameters checking
    if args.currcsv is None and args.archcsv is None and args.db is None:
        print("Must provide input file\n")
        exit()
    if args.db is not None and not (args.currcsv is None and args.archcsv is None):
        print("Must only use only one type of input file\n")
        exit()
    if args.db is None and (args.currcsv is None or args.archcsv is None):
        print("Must provide both current and archive index CSV files\n")
        exit()
    if args.out is None:
        print("Must specify output file\n")
        exit()

    if args.currcsv is not None and args.archcsv is not None:
        use_csv = True
        curr_csv_name = args.currcsv
        arch_csv_name = args.archcsv
    else:
        use_csv = False

    if args.db is not None:
        use_db = True
        connect_sql(args.db)
    else:
        use_db = False

    csv_out_name = args.out
    do_print = args.print

    return use_csv, use_db, curr_csv_name, arch_csv_name, do_print, csv_out_name


def main():
    use_csv, use_db, curr_csv_name, arch_csv_name, do_print, csv_out_name = parse_args()
    if use_csv:
        open_with_csv(curr_csv_name, arch_csv_name, csv_out_name, do_print)
    if use_db:
        open_with_db(csv_out_name, do_print)


main()
