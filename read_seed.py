import argparse
import csv


def parse_csv(csv_in_name, csv_out_name, archive_name, do_sort):
    """Reads the input seed file and writes the urls to the output files

    Parameters
    ----------
    csv_in_name : str
        Input CSV file with the seed urls.
    csv_out_name : str
        The DB file to store the urls.
    do_sort : bool
        Whether or not the output is sorted.
    archive_name : str
        Name of the archive
    """


    with open(csv_in_name, "r") as csv_file_in:
        csv_reader = csv.reader(csv_file_in)
        with open(csv_out_name, "w+", newline='') as csv_file_out:
            csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
            csv_writer.writerow(["archive_name", "url_id", "current_url"])

            if do_sort:
                row_list = []
                for element in csv_file_in.read().split('\n'):
                    if element[0] != 'T':
                        row_list.append(element.split(','))

                row_list.sort(key=lambda x: int(x[0]))
                for line in row_list:
                    csv_writer.writerow([archive_name, line[0], line[-2]])
            else:
                next(csv_reader)  # skip header

                while True:
                    try:
                        line = next(csv_reader)
                    except StopIteration:
                        break
                    csv_writer.writerow([archive_name, line[0], line[-2]])


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
    archive_name : str
        Name of the archive

    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, help="The CSV file with the seed urls")
    parser.add_argument("--out", type=str, help="The CSV file to write the urls")
    parser.add_argument("--name", type=str, help="Name of the archive")
    parser.add_argument('--sort', action='store_true', help="(optional) Include to sort URLS by ID")
    args = parser.parse_args()

    # some error checks
    if args.csv is None:
        print("Must include an input CSV file\n")
        exit()
    if args.name is None:
        print("Must specify archive Name\n")
        exit()
    if args.out is None:
        print("Must specify the output CSV file")
        exit()

    return args.csv, args.out, args.name, args.sort


def main():
    csv_in_name, csv_out_name, archive_name, do_sort = parse_args()
    print("Parsing csv...\n")
    parse_csv(csv_in_name, csv_out_name, archive_name, do_sort)


main()
