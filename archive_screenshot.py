import argparse
import os
import sqlite3
import time
import asyncio
import urllib.request
import urllib.error
from pyppeteer import launch
from pyppeteer import errors
import logging


def screenshot_txt():
    count = 0
    compare = '0'
    for line in inputURLFile:
        line = line.split('|')
        url_id = line[1]

        if beLazy is True:  # makes running faster by not doing hundreds of archive sites
            if url_id != compare:
                count = 0
                compare = url_id
            else:
                count += 1
                if count > lazy:
                    continue

        archive_id = line[0]
        date = line[2]
        url = line[3]

        # remove/replace characters in url that may cause problems
        clean_url = url.strip('\n')

        print("\nurl #{0} {1}".format(url_id, clean_url))
        logging.info("url #{0} {1}".format(url_id, clean_url))

        succeed = take_screenshot(archive_id, url_id, date, clean_url)

        # print to index
        indexFile.write("{0}|{1}|{2}|{3}|{4}".format(archive_id, url_id, date, succeed, url))

    inputURLFile.close()
    indexFile.close()


def screenshot_db():
    cursor.execute("create table if not exists archive_index (archiveID int, urlID int, date text, succeed int, "
                   "foreign key(archiveID) references collection_name(archiveID));")
    cursor.execute("delete from archive_index;")
    cursor.execute("select * from archive_urls where url is not null;")
    connection.commit()

    results = cursor.fetchall()
    count = 0
    compare = '0'
    for row in results:
        url_id = row[1]

        if beLazy is True:  # makes running faster by not doing hundreds of archive site
            if url_id != compare:
                count = 0
                compare = url_id
            else:
                count += 1
                if count > lazy:
                    continue

        archive_id = row[0]
        date = row[2]
        url = row[3]

        clean_url = url  # may need more to clean url

        print("\nurl #{0} {1}".format(url_id, clean_url))
        logging.info("url #{0} {1}".format(url_id, clean_url))

        succeed = take_screenshot(archive_id, url_id, date, clean_url)

        # insert into db
        cursor.execute("insert into archive_index values ({0}, {1}, '{2}', {3});"
                       .format(archive_id, url_id, date, succeed))
        if maketxt:
            indexFile.write("{0}|{1}|{2}|{3}|{4}".format(archive_id, url_id, date, succeed, url))

        connection.commit()
    connection.close()

    if maketxt:
        indexFile.close()


def take_screenshot(archive_id, url_id, date, url):
    return_code = check_site_availability(url)
    if return_code != 200 and return_code != 302:
        return return_code

    # command which takes the screenshots
    command = ""
    if screenshot_method == 0:
        command = "timeout {5}s google-chrome --headless --hide-scrollbars --disable-gpu --noerrdialogs " \
                  "--enable-fast-unload --screenshot={0}{1}.{2}.{3}.png --window-size=1024x768 '{4}'"\
            .format(pics_out_path, archive_id, url_id, date, url, timeoutDuration)

    elif screenshot_method == 2:
        command = "timeout {5}s xvfb-run --server-args=\"-screen 0, 1024x768x24\" " \
                  "cutycapt --url='{0}' --out={1}{2}.{3}.{4}.png --delay=2000"\
            .format(url, pics_out_path, archive_id, url_id, date, timeoutDuration)

    elif screenshot_method == 1:
        try:
            asyncio.get_event_loop().run_until_complete(puppeteer_screenshot(archive_id, url_id, url))
            logging.info("Screenshot successful")
            print("Screenshot successful")
            return 200
        except errors.TimeoutError as e:
            print(e)
            logging.info(e)
            return 0
        except errors.NetworkError as e:
            print(e)
            logging.info(e)
            return 0
        except errors.PageError as e:
            print(e)
            logging.info(e)
            return 0
        except Exception as e:
            print(e)
            return 0
    else:
        # atm assumes the user only enters 0 or 1 or 2
        # better do more error checks
        pass

    try:
        if os.system(command) == 0:
            succeed = 200
            logging.info("Screenshot successful")
        else:
            logging.info("Screenshot unsuccessful")
            succeed = 0
    except:
        logging.info("Screenshot unsuccessful")
        succeed = 0
    time.sleep(1)  # xvfb needs time to rest

    return str(succeed)


async def puppeteer_screenshot(archive_id, url_id, url):
    browser = await launch()
    page = await browser.newPage()
    await page.setViewport({'height': 768, 'width': 1024})
    await page.goto(url, timeout=(int(timeoutDuration) * 1000))
    await page.screenshot(path='{0}{1}.{2}.png'.format(pics_out_path, archive_id, url_id))
    await browser.close()


def check_site_availability(url):
    try:
        conn = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        # Return code error (e.g. 404, 501, ...)
        print('HTTPError: {}'.format(e.code))
        logging.info('HTTPError: {}'.format(e.code))
        return int(e.code)
    except urllib.error.URLError as e:
        # Not an HTTP-specific error (e.g. connection refused)
        print('URLError: {}'.format(e.reason))
        logging.info('URLError: {}'.format(e.reason))
        return 0
    except Exception as e:
        # other reasons such as "your connection is not secure"
        print(e)
        logging.info(e)
        return 0

    # check if redirected
    if conn.geturl() != url:
        print("Redirected to {}".format(conn.geturl()))
        logging.info("Redirected to {}".format(conn.geturl()))
        return 302

    # reaching this point means it received code 200
    print("Return code 200")
    logging.info("Return code 200")
    return 200


# takes the command line arguments and parses it
def parse_args():
    global inputURLFile, pics_out_path, indexFile, screenshot_method, usetxt, maketxt, timeoutDuration, lazy, beLazy
    parser = argparse.ArgumentParser()

    # initializing every line switch
    parser.add_argument("--txt", type=str, help="input txt file with urls")
    parser.add_argument("--db", type=str, help="input db file with urls")
    parser.add_argument("--picsout", type=str, help="path to put the screenshots")
    parser.add_argument("--indexout", type=str, help="file to output the index txt")
    parser.add_argument("--method", type=int, help="0 for chrome, 1 for puppeteer, 2 for cutycapt")
    parser.add_argument("--timeout", type=str,
                        help="specify duration before timeout, in seconds, default 30s")
    parser.add_argument("--lazy", type=int, help="it will go to the next archive after taking n pictures")

    args = parser.parse_args()

    # some error checking
    if args.txt is not None and args.indexout is None:
        print("invalid output index file\n")
        exit()
    if args.txt is None and args.db is None:
        print("Must provide input file\n")
        exit()
    if args.txt is not None and args.db is not None:
        print("must only use only one type of input file\n")
        exit()
    if args.picsout is None:
        print("Must specify output path for pictures")
        exit()

    pics_out_path = args.picsout + '/'
    screenshot_method = int(args.method)

    if args.txt is not None:
        usetxt = True
        inputURLFile = open(args.txt, "r")

    if args.db is not None:
        usetxt = False
        connect_sql(args.db)

    if args.indexout is not None:
        indexFile = open(args.indexout, 'w+')
        maketxt = True
    else:
        maketxt = False

    if args.timeout is None:
        timeoutDuration = "30"
    else:
        timeoutDuration = args.timeout

    if args.lazy is not None:
        beLazy = True
        lazy = args.lazy
    else:
        beLazy = False


# basically connect the db at path
def connect_sql(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    connection.commit()


def set_up_logging():
    # setting up logging format
    # filename: the file to output the logs
    # filemode: a as in append
    # format: format of the message
    # datefmt: format of the date in the message
    # level: minimum message level accepted
    logging.basicConfig(filename=(pics_out_path + "archive_screenshot_log.txt"), filemode='a',
                        format='%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S',
                        level=logging.INFO)


def main():
    parse_args()
    set_up_logging()
    print("Taking screenshots")
    if usetxt:
        screenshot_txt()
    else:
        screenshot_db()


main()
