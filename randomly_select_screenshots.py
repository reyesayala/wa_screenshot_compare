import random
import csv
import argparse


def make_selection(input_csv, out_csv, num):
    """Randomly select a number of archive screenshot for each current screenshot.

    Parameters
    ----------
    input_csv : str
        Path of the input CSV file which contains the urls and file names.
    out_csv : str
        Path of the output CSV file which can be written to.
    num : int
        The number of screenshots to choose for each ID
    """

    print("File name: ", input_csv)
    with open(out_csv, 'w+') as out_file:
        csv_writer = csv.writer(out_file, delimiter=',', quoting=csv.QUOTE_ALL)
        csv_writer.writerow(["current_url", "archive_url", "current_file_name", "archive_file_name"])

        with open(input_csv, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            line_count = 0
            compare_name = ''
            holder = []

            for row in csv_reader:
                if line_count == 0:  # skip the first row in csv because it's the header
                    line_count += 1
                    continue

                current_image_name = row[2]

                if compare_name != current_image_name:
                    compare_name = current_image_name
                    if len(holder) != 0:
                        chosen_rows = random.sample(holder, min(num, len(holder)))
                        for chosen_row in chosen_rows:
                            csv_writer.writerow(chosen_row)
                        holder.clear()
                holder.append(row)


def parse_args():
    """Parses the arguments passed in from the command line.

    Returns
    -------
    args.csv : str
        Path of the input CSV file which contains the urls and file names.

    args.out : str
        Path of the output CSV file which can be written to.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, help="The CSV file with screenshot file names")
    parser.add_argument("--out", type=str, help="The CSV file to write the newly selected file names")
    parser.add_argument("--num", type=int, help="Specify to choose a random number of screenshot per ID")

    args = parser.parse_args()

    # some error checking
    if args.csv is None:
        print("Must provide input file")
        exit()
    if args.out is None:
        print("Must provide output file")
        exit()
    if args.num is None:
        print("Must provide number of random files")
        exit()
    if args.num < 1:
        print("Invalid value for number of random files")
        exit()

    return args.csv, args.out, args.num


def main():
    input_csv, out_file, num = parse_args()
    make_selection(input_csv, out_file, num)


main()
