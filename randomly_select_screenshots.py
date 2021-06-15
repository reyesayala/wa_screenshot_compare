import random
import csv
import argparse


def make_selection(input_csv, out_csv, num, total):
    """Randomly select a number of archive screenshot for each current screenshot.

    Parameters
    ----------
    input_csv : str
        Path of the input CSV file which contains the urls and file names.
    out_csv : str
        Path of the output CSV file which can be written to.
    num : int
        The number of screenshots to choose for each ID.
    total : int
        Total number of screenshots to choose.

    """

    print("File name: ", input_csv)
    with open(out_csv, 'w+') as out_file:
        csv_writer = csv.writer(out_file, delimiter=',', quoting=csv.QUOTE_ALL)
        csv_writer.writerow(["current_url", "archive_url", "current_file_name", "archive_file_name"])

        with open(input_csv, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            row_count = 0
            compare_name = ''
            holder = []

            next(csv_reader)  # skip header
            while True:
                try:
                    row = next(csv_reader)
                except StopIteration:
                    break

                current_image_name = row[2]

                if compare_name != current_image_name:
                    compare_name = current_image_name
                    if len(holder) != 0:
                        chosen_rows = random.sample(holder, min(num, len(holder)))
                        for chosen_row in chosen_rows:
                            csv_writer.writerow(chosen_row)
                            row_count += 1
                            if total is not None:
                                if row_count >= total:
                                    return

                        holder.clear()
                holder.append(row)


def main():
    # input_csv, out_file, num, total = parse_args()
    import read_config_file
    import config

    make_selection(config.file_names_csv, config.selected_file_names, config.num, config.total)


main()
