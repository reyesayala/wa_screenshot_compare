import argparse
import csv
import sqlite3
import sys


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



def main():
    import read_config_file
    import config
    print("Parsing csv...\n")
    parse_csv(config.seed_list, config.current_urls_csv, config.sort, config.collection_id, False, True)
    print("File ", config.current_urls_csv, "with the current urls has been created")


main()

