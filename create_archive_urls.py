import argparse
import sqlite3
import csv
import requests
from bs4 import BeautifulSoup


def create_with_db(make_csv, csv_out_name, remove_banner):
    """Finds the archive urls using the DB file with current urls, and outputs it into a db.

    Parameters
    ----------
    make_csv: bool
        Whether or not to also output a CSV file.
    csv_out_name : str
        The CSV file to write the archive urls.
    remove_banner : bool
        Whether or not to generate urls that include Archive-It banner.

    """

    cursor.execute("select * from current_urls;")
    connection.commit()
    results = cursor.fetchall()

    if make_csv:
        csv_file_out = open(csv_out_name, "w+")
        csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
        csv_writer.writerow(["archive_id", "url_id", "archive_url"])

    for row in results:
        archive_id = str(row[0])
        url_id = str(row[1])
        url = row[2]

        archive_url = "https://wayback.archive-it.org/{0}/*/{1}".format(archive_id, url)

        print("url #" + url_id)

        # get external link to each capture                                                                                        
        found = False
        page = requests.get(archive_url)                # next 7 lines just go through the html to find the urls
        soup = BeautifulSoup(page.content, features='html.parser')
        for htmltd in soup.findAll('td'):
            htmlclass = htmltd.get('class')
            if htmlclass is not None:
                if htmlclass[0] == "mainBody":
                    for htmla in htmltd.findAll('a'):
                        found_url = htmla.get('href')
                        date = found_url.split('/')[4]

                        if remove_banner:       # add if_ into url if remove_banner is true
                            index = found_url.find('/', 40)
                            final_url = found_url[:index] + "if_" + found_url[index:]
                        else:
                            final_url = found_url

                        cursor.execute("insert into archive_urls values ({0}, {1}, '{2}', '{3}');"
                                       .format(archive_id, url_id, date, final_url))        # insert into db

                        if make_csv:
                            csv_writer.writerow([archive_id, url_id, date, final_url])
                        
                        found = True

        if not found:
            cursor.execute("insert into archive_urls values({0}, {1}, NULL, NULL);".format(archive_id, url_id))
            if make_csv:
                csv_writer.writerow([archive_id, url_id, "", ""])

        page.close()
        connection.commit()

    connection.close()
    if make_csv:
        csv_file_out.close()


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

                found = False  # next 15 lines just goes through the html to find the urls
                page = requests.get(archive_url)
                soup = BeautifulSoup(page.content, features='html.parser')
                for htmltd in soup.findAll('td'):
                    htmlclass = htmltd.get('class')
                    if htmlclass is not None:
                        if htmlclass[0] == "mainBody":
                            for htmla in htmltd.findAll('a'):
                                found_url = htmla.get('href')
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


def parse_args():
    """Parses the arguments passed in from the command line.

    Returns
    -------
    csv_in_name : str
        The CSV file with the current urls.
    csv_out_name : str
        The CSV file to write the archive urls.
    use_db : bool
        Whether or not the input is DB.
    use_csv : bool
        Whether or not the input is CSV.
    make_csv : bool
        Whether or not to output a CSV when use_db is True.
    remove_banner : bool
        Whether or not to generate urls that include Archive-It banner.

    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=str, help="Input DB file with urls, output is automatically inserted in db")
    parser.add_argument("--csv", type=str, help="Input CSV file with current urls")
    parser.add_argument("--out", type=str, help="The CSV file to write the urls")
    parser.add_argument("--banner", action='store_true',
                        help="(optional) Include to generate urls that has the banner, default removes banner")

    args = parser.parse_args()

    # some error checking
    if args.db is None and args.csv is None:
        print("Must include input file\n")
        exit()
    if args.db is not None and args.csv is not None:
        print("Must only specify one type in input file\n")
        exit()
    if args.csv is not None and args.out is None:
        print("Must specify output location\n")
        exit()
        
    if args.db is not None:
        use_db = True
        connect_sql(args.db)
    else:
        use_db = False
                
    if args.csv is not None:
        use_csv = True
        csv_in_name = args.csv
    else:
        use_csv = False

    if args.out is not None:
        csv_out_name = args.out
        make_csv = True
    else:
        make_csv = False

    remove_banner = not args.banner

    return use_db, use_csv, make_csv, csv_out_name, csv_in_name, remove_banner

        
# creates the db and table to store the URLs
def connect_sql(path):
    """Creates or connects the DB file and create the necessary tables. """
    global connection, cursor    

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    connection.commit()
    cursor.execute("CREATE TABLE IF NOT EXISTS archive_urls (archiveID INT, urlID INT, date TEXT, url TEXT, "
                   "FOREIGN KEY (archiveID) REFERENCES collection_name(archiveID));")
    cursor.execute("DELETE FROM archive_urls;")
    connection.commit()
    

def main():
    use_db, use_csv, make_csv, csv_out_name, csv_in_name, remove_banner = parse_args()
    print("Getting archive urls...")
    if use_csv:
        create_with_csv(csv_out_name, csv_in_name, remove_banner)
    if use_db:
        create_with_db(make_csv, csv_out_name, remove_banner)
    

main()
