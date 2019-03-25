import argparse
import sqlite3
import requests
from bs4 import BeautifulSoup


def create_with_db():
    cursor.execute("select * from current_urls;")
    connection.commit()
    results = cursor.fetchall()

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

                        if remove_banner:       # add id_ into url if remove_banner is true
                            index = found_url.find('/', 40)
                            final_url = found_url[:index] + "id_" + found_url[index:]
                        else:
                            final_url = found_url

                        cursor.execute("insert into archive_urls values ({0}, {1}, '{2}', '{3}');"
                                       .format(archive_id, url_id, date, final_url))        # insert into db

                        if maketxt:
                            outputFile.write("{0}|{1}|{2}|{3}\n".format(archive_id, url_id, date, final_url))
                        
                        found = True

        if not found:
            cursor.execute("insert into archive_urls values({0}, {1}, NULL, NULL);".format(archive_id, url_id))
            if maketxt:
                outputFile.write("{0}|{1}||\n".format(archive_id, url_id))

        page.close()

        connection.commit()

    connection.close()
    if maketxt:
        outputFile.close()


def create_with_txt():
    for line in inputtxt:
        line = line.split('|')
        archive_id = line[0]
        url_id = line[1]
        url = line[2].strip('\n')

        archive_url = "https://wayback.archive-it.org/{0}/*/{1}".format(archive_id, url)

        print("url #" + url_id)

        # get external link to each capture                                                                                                     
        found = False
        page = requests.get(archive_url)                    # next 7 lines just go through the html to find the urls
        soup = BeautifulSoup(page.content, features='html.parser')
        for htmltd in soup.findAll('td'):
            htmlclass = htmltd.get('class')
            if htmlclass is not None:
                if htmlclass[0] == "mainBody":
                    for htmla in htmltd.findAll('a'):
                        found_url = htmla.get('href')
                        date = found_url.split('/')[4]

                        if remove_banner:       # add id_ into url if remove_banner is true
                            index = found_url.find('/', 40)
                            final_url = found_url[:index] + "id_" + found_url[index:]
                        else:
                            final_url = found_url

                        outputFile.write("{0}|{1}|{2}|{3}\n".format(archive_id, url_id, date, final_url))

                        found = True
        if not found:
            outputFile.write("{0}|{1}||\n".format(archive_id, url_id))

        page.close()

    outputFile.close()

    
def parse_args():
    global usetxt, maketxt, outputFile, inputtxt, remove_banner

    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=str, help="input db file with urls, output is automatically inserted in db")
    parser.add_argument("--txt", type=str, help="input txt file with urls")
    parser.add_argument("--out", type=str, help="output file to generate the output into")
    parser.add_argument("--banner", action='store_true', help="include to generate urls that has the banner, "
                                                              "default removes banner")

    args = parser.parse_args()

    # some error checking
    if args.db is None and args.txt is None:
        print("Must include input file\n")
        exit()
    if args.db is not None and args.txt is not None:
        print("Must only specify one type in input file\n")
        exit()
    if args.txt is not None and args.out is None:
        print("Must specify output location\n")
        exit()
        
    if args.db is not None:
        usetxt = False
        connect_sql(args.db)
                
    if args.txt is not None:
        usetxt = True
        inputtxt = open(args.txt, 'r')
                        
    if args.out is not None:
        outputFile = open(args.out, "w+")
        maketxt = True
    else:
        maketxt = False

    remove_banner = not args.banner

        
# creates the db and table to store the URLs
def connect_sql(path):
    global connection, cursor    

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    connection.commit()
    cursor.execute("CREATE TABLE IF NOT EXISTS archive_urls (archiveID INT, urlID INT, date TEXT, url TEXT, "
                   "FOREIGN KEY (archiveID) REFERENCES collection_name(archiveID));")
    cursor.execute("DELETE FROM archive_urls;")
    connection.commit()
    

def main():
    parse_args()
    print("Getting archive urls...\n")
    if usetxt:
        create_with_txt()
    else:
        create_with_db()
    

main()
