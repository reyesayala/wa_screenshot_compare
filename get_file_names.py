import sqlite3
import argparse
import csv

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
                            current_filename = "{0}.{1}.jpg".format(carchive_id, curl_id)
                            archive_filename = "{0}.{1}.{2}.jpg".format(aarchive_id, aurl_id, adate)
                            csv_writer.writerow([curl, aurl, current_filename, archive_filename])

                            if do_print:
                                print("{0}, {1}, {2}, {3}".format(curl, aurl, current_filename, archive_filename))

                            arow = next(arch_csv_reader)

                except StopIteration:
                    pass

def parse_args():
    """Parses the command line arguments

    Returns
    -------
    use_csv : bool
        Whether or not the input is a CSV.
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
    parser.add_argument("--out", type=str, help="The CSV file to write the urls and file names")
    parser.add_argument("--print", action='store_true',
                        help="(optional) Include to print urls and file names to stdout, default doesn't print")

    args = parser.parse_args()

    # some parameters checking
    if args.currcsv is None and args.archcsv is None:
        print("Must provide input file\n")
        exit()
    if args.currcsv is None:
        print("Must provide input CSV file with the current screenshot index.\n")
        exit()
    if args.archcsv is None:
        print("Must provide input CSV file with the archive screenshots index.\n")
        exit()
    if args.out is None:
        print("Must specify output file\n")
        exit()
    
    curr_csv_name = args.currcsv
    arch_csv_name = args.archcsv

    csv_out_name = args.out
    do_print = args.print

    return curr_csv_name, arch_csv_name, do_print, csv_out_name


def main():
    curr_csv_name, arch_csv_name, do_print, csv_out_name = parse_args()
    open_with_csv(curr_csv_name, arch_csv_name, csv_out_name, do_print)

main()
