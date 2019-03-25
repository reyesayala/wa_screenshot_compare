import sqlite3
import argparse
import csv


def open_with_db():
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

    with open(csvOut, 'w+') as out_file:
        csv_writer = csv.writer(out_file, delimiter=',', quoting=csv.QUOTE_ALL)
        csv_writer.writerow(["current_url", "archive_url", "current_file_name", "archive_file_name"])
        
        for row in fetchall:
            [current_url, archive_url, archive_id, url_id, date] = row
            current_filename = "{0}.{1}.png".format(archive_id, url_id)
            archive_filename = "{0}.{1}.{2}.png".format(archive_id, url_id, date)
            csv_writer.writerow([current_url, archive_url, current_filename, archive_filename])

            if doPrint:
                print("{0}|{1}|{2}|{3}".format(current_url, archive_url, current_filename, archive_filename))

    connection.close()


def open_with_txt():
    out_file = open(csvOut, 'w+')
    csv_writer = csv.writer(out_file, delimiter=',', quoting=csv.QUOTE_ALL)
    csv_writer.writerow(["current_url", "archive_url", "current_file_name", "archive_file_name"])

    archive_index_file = open(atxt, 'r')
    current_index_file = open(ctxt, 'r')

    nline = current_index_file.readline().strip('\n')
    aline = archive_index_file.readline().strip('\n')

    # goes through both files and gets info line by line
    while aline != '' and nline != '':
        nline_split = nline.split('|')
        aline_split = aline.split('|')

        [narchive_id, nurl_id, nsucceed, nurl] = nline_split
        [aarchive_id, aurl_id, adate, asucceed, aurl] = aline_split
        nurl_id = int(nurl_id)
        aurl_id = int(aurl_id)

        if nurl_id > aurl_id or asucceed != '200':
            aline = archive_index_file.readline().rstrip()
        elif nurl_id < aurl_id or nsucceed != '200':
            nline = current_index_file.readline().rstrip()
        else:
            current_filename = "{0}.{1}.png".format(narchive_id, nurl_id)
            archive_filename = "{0}.{1}.{2}.png".format(aarchive_id, aurl_id, adate)
            csv_writer.writerow([nurl, aurl, current_filename, archive_filename])

            if doPrint:
                print("{0}|{1}|{2}|{3}".format(nurl, aurl, current_filename, archive_filename))

            aline = archive_index_file.readline().rstrip()

    current_index_file.close()
    archive_index_file.close()


# basically created the index db at path
def connect_sql(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    connection.commit()


# takes the command line arguments and parses it
def parse_args():
    global usetxt, ctxt, atxt, doPrint, csvOut
    parser = argparse.ArgumentParser()

    # initializing every line switch
    parser.add_argument("--ctxt", type=str, help="input txt file with the current index")
    parser.add_argument("--atxt", type=str, help="input txt file with the archive index")
    parser.add_argument("--db", type=str, help="input db file with urls")
    parser.add_argument("--out", type=str, help="output csv file to put the urls and filenames")
    parser.add_argument("--print", type=bool, default=False, const=True, nargs='?',
                        help="toggle to print urls and filenames to stdout, default doesnt print")

    args = parser.parse_args()

    # some parameters checking
    if args.ctxt is None and args.atxt is None and args.db is None:
        print("Must provide input file\n")
        exit()
    if args.db is not None and not (args.ctxt is None and args.atxt is None):
        print("Must only use only one type of input file\n")
        exit()
    if args.db is None and (args.ctxt is None or args.atxt is None):
        print("Must provide both current and archive index txt files\n")
        exit()
    if args.out is None:
        print("Must specify output file\n")
        exit()

    if args.ctxt is not None and args.atxt is not None:
        usetxt = True
        ctxt = args.ctxt
        atxt = args.atxt

    if args.db is not None:
        usetxt = False
        connect_sql(args.db)

    csvOut = args.out
    doPrint = args.print


def main():
    parse_args()
    if usetxt:
        open_with_txt()
    else:
        open_with_db()


main()
