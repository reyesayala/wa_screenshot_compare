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
                        ascreenshot_site_message = arow[-2]

                        curl_id = int(curl_id)
                        aurl_id = int(aurl_id)

                        if curl_id > aurl_id or ascreenshot_status != "Screenshot successful":
                            arow = next(arch_csv_reader)
                        elif curl_id < aurl_id or cscreenshot_status != "Screenshot successful":
                            crow = next(curr_csv_reader)
                        else:
                            if (ascreenshot_site_message.find("Redirected") == 0):
                                aurl = ascreenshot_site_message.split()[2]
                                marker = aarchive_id+'/'
                                aurl_split = aurl.split(marker)[1]
                                adate = aurl_split[:aurl_split.find('/')]
                                if (adate.find("if_") != -1):
                                    adate = adate[:-3]
                            current_filename = "{0}.{1}.png".format(carchive_id, curl_id)
                            archive_filename = "{0}.{1}.{2}.png".format(aarchive_id, aurl_id, adate)
                            csv_writer.writerow([curl, aurl, current_filename, archive_filename])

                            if do_print:
                                print("{0}, {1}, {2}, {3}".format(curl, aurl, current_filename, archive_filename))

                            arow = next(arch_csv_reader)

                except StopIteration:
                    pass

def main():
    # curr_csv_name, arch_csv_name, do_print, csv_out_name = parse_args()
    import read_config_file
    import config

    open_with_csv(config.current_index_csv, config.archive_index_csv, config.file_names_csv, config.print)

main()
