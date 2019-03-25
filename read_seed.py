import argparse
import csv
import os
import sqlite3


def parse_csv():
    temp_txt = None
    if use_txt:
        temp_txt = open("temp", 'w+')

    with open(csv_file_name, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        count = 0
        for line in csv_reader:
            count += 1
            if count == 1:
                continue

            url = line[0]

            write_to_temp(temp_txt, url, count)

        if do_sort:
            if use_txt:
                temp_txt.close()
                sort_txt()
            if use_db:
                sort_db()
        else:
            if use_txt:
                temp_txt.close()
                os.system("cp temp {0}".format(output_file_name))
                os.system("rm temp")
            if use_db:
                connection.commit()
                connection.close()


def write_to_temp(temp_txt, url, count):
    if use_txt:
        temp_txt.write("{0}\n".format(url))
    if use_db:
        cursor.execute("INSERT OR REPLACE INTO current_urls VALUES ({0}, {1}, '{2}');".format(extension, count, url))


def sort_txt():
    os.system("sort temp -o temp")
    temp_txt = open("temp", 'r')
    output_file = open(output_file_name, 'w+')
    count = 0
    for line in temp_txt:
        count += 1
        output_file.write("{0}|{1}|{2}".format(extension, count, line))
    temp_txt.close()
    os.system("rm temp")
    output_file.close()


def sort_db():
    cursor.execute("create table temptable as select {0}, ROW_NUMBER() over (order by url asc) urlID, "
                   "url from current_urls where archiveID = {0};".format(extension))
    cursor.execute("delete from current_urls where archiveID = {0};".format(extension))
    cursor.execute("insert into current_urls select * from temptable;")
    cursor.execute("drop table temptable;")

    connection.commit()
    connection.close()


def parse_args():
    global csv_file_name, do_sort, extension, archive_name, output_file_name, use_db, use_txt

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, help="Input csv file with the seed urls")
    parser.add_argument("--db", type=str, help="The db file to store the urls")
    parser.add_argument("--out", type=str, help="The file to write the urls to")
    parser.add_argument("--sort", action='store_true', help="Include to sort the output")   # optional
    parser.add_argument("--ext", type=str, help="ID of the archive")
    parser.add_argument("--name", type=str, help="Name of the archive")
  
    args = parser.parse_args()

    # some error checks
    if args.csv is None:
        print("Must include an input file\n")
        exit() 
    if args.db is None and args.out is None:            # two outputs are allowed
        print("Must specify output file(s)\n")
        exit()
    if args.ext is None:
        print("Must specify archive extension\n")
        exit()
    if args.name is None:
        print("must specify archive name\n")
        exit()

    csv_file_name = args.csv
    do_sort = args.sort
    extension = args.ext
    archive_name = args.name

    if args.db is not None:
        connect_sql(args.db)
        use_db = True
    else:
        use_db = False

    if args.out is not None:
        output_file_name = args.out
        use_txt = True
    else:
        use_txt = False


# creates the db and table to store the URLs
def connect_sql(path):
    global connection, cursor    

    connection = sqlite3.connect(path)
    cursor = connection.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS collection_name (archiveID INT PRIMARY KEY, name TEXT);")
    cursor.execute("INSERT OR REPLACE INTO collection_name VALUES ({0}, '{1}');".format(extension, archive_name))
    cursor.execute("CREATE TABLE IF NOT EXISTS current_urls (archiveID INT, urlID INT, url TEXT, "
                   "FOREIGN KEY (archiveID) REFERENCES collection_name(archiveID));")
    cursor.execute("DELETE FROM current_urls WHERE archiveID = {0};".format(extension))
    connection.commit()
    

def main():
    parse_args()
    print("Parsing csv...\n")
    parse_csv()


main()
