
import argparse
import sqlite3
import csv
import requests
from bs4 import BeautifulSoup

def create_with_csv(csv_out_name, csv_in_name, remove_banner):
    """Finds the archive urls using the input csv file with current urls, and outputs it into a csv.

    Parameters
    ----------
    csv_in_name : str
        The CSV file with the current urls.
    csv_out_name : str
        The CSV file to write the archive urls.
    remove_banner : bool
        Whether or not to generate urls that include Archive-It banner.

    """

    with open(csv_in_name, 'r') as csv_file_in:
        csv_reader = csv.reader(csv_file_in)
        with open(csv_out_name, 'w+') as csv_file_out:
            csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
            csv_writer.writerow(["archive_id", "url_id", "archive_url"])

            count = 0
            for line in csv_reader:
                if count == 0:      # skip the header
                    count += 1
                    continue

                archive_id = line[0]
                url_id = line[1]
                url = line[2]
                archive_url = "https://wayback.archive-it.org/{0}/*/{1}".format(archive_id, url)

                print("url #" + url_id)
                print("url #" + archive_url)

                found = False  # next 15 lines just goes through the html to find the urls
                page = requests.get(archive_url)
                soup = BeautifulSoup(page.content, features='html.parser')
                for htmltd in soup.findAll('td'):
                    htmlclass = htmltd.get('class')
                    if htmlclass is not None:
                        if htmlclass[0] == "mainBody":
                            for htmla in htmltd.findAll('a'):
                                found_url = htmla.get('href')
                                if(found_url.startswith("https://")):
                                    pass
                                else:
                                    found_url="https:"+found_url
                                date = found_url.split('/')[4]

                                if remove_banner:       # add if_ into archive url if remove_banner is true
                                    index = found_url.find('/', 40)
                                    final_url = found_url[:index] + "if_" + found_url[index:]
                                else:
                                    final_url = found_url
                                csv_writer.writerow([archive_id, url_id, date, final_url])

                                found = True
                if not found:
                    csv_writer.writerow([archive_id, url_id, "", ""])

                page.close()

def main():

    import read_config_file
    import config

    print("Getting archive urls...")
    create_with_csv(config.archive_urls_csv, config.current_urls_csv, config.remove_banner)
    print("File ", config.archive_urls_csv, "with the archived urls has been created")

main()




