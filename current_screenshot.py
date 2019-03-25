import argparse
import asyncio
import os
import sqlite3
import time
import urllib.request
import urllib.error
from pyppeteer import launch
from pyppeteer import errors
import logging


def screenshot_txt():
    count = 0
    for line in input_url_file:
        count += 1

        line = line.split('|')
        archive_id = line[0]
        url_id = line[1]
        url = line[2]

        # remove/replace characters in url that may cause problems, may need to do more
        clean_url = url.strip('\n')

        print("\nurl #{0} {1}".format(url_id, clean_url))
        logging.info("url #{0} {1}".format(url_id, clean_url))

        succeed = take_screenshot(archive_id, url_id, clean_url)

        # print to index
        index_file.write("{0}|{1}|{2}|{3}".format(archive_id, url_id, succeed, url))

    input_url_file.close()
    index_file.close()


def screenshot_db():
    cursor.execute("create table if not exists current_index (archiveID int, urlID int, succeed int, "
                   "foreign key(archiveID) references collection_name(archiveID));")
    cursor.execute("delete from current_index;")
    cursor.execute("select * from current_url;")
    connection.commit()

    results = cursor.fetchall()
    count = 0
    for row in results:
        count += 1
        archive_id = row[0]
        url_id = row[1]
        url = row[2]

        clean_url = url  # may need more to clean url

        print("\nurl #{0} {1}".format(url_id, clean_url))
        logging.info("url #{0} {1}".format(url_id, clean_url))

        succeed = take_screenshot(str(archive_id), str(url_id), clean_url)

        # insert into db
        cursor.execute("insert into current_index values ({0}, {1}, {2});".format(archive_id, url_id, succeed))
        if maketxt:
            index_file.write("{0}|{1}|{2}|{3}".format(archive_id, url_id, succeed, url))

        connection.commit()
    connection.close()
    if maketxt:
        index_file.close()


def take_screenshot(archive_id, url_id, url):
    return_code = check_site_availability(url)
    if return_code != 200 and return_code != 302:
        return return_code

    command = ''
    # command which takes the screenshots
    if screenshot_method == 0:
        command = "timeout {4}s google-chrome --headless --hide-scrollbars --disable-gpu --noerrdialogs " \
                  "--enable-fast-unload --screenshot={0}{1}.{2}.png --window-size=1024x768 '{3}'" \
            .format(pics_out_path, archive_id, url_id, url, timeout_duration)
    elif screenshot_method == 2:
        command = "timeout {4}s xvfb-run --server-args=\"-screen 0, 1024x768x24\" cutycapt --url='{0}' " \
                  "--out={1}{2}.{3}.png --delay=2000".format(url, pics_out_path, archive_id, url_id,
                                                             timeout_duration)
    elif screenshot_method == 1:
        try:
            asyncio.get_event_loop().run_until_complete(puppeteer_screenshot(archive_id, url_id, url))
            logging.info("Screenshot successful")
            return 200
        except errors.TimeoutError as e:
            print(e)
            logging.info(e)
            return -1
        except errors.NetworkError as e:
            print(e)
            logging.info(e)
            return -2
        except errors.PageError as e:
            print(e)
            logging.info(e)
            return -3
        except Exception as e:
            print(e)
            return -4
    else:
        # atm assumes the user only enters 0 or 1 or 2
        # better do more error checks todo
        pass

    try:
        if os.system(command) == 0:
            succeed = 200
            logging.info("Screenshot successful")
        else:
            logging.info("Screenshot unsuccessful")
            succeed = -5
    except:
        logging.info("Screenshot unsuccessful")
        succeed = -6
    time.sleep(1)  # xvfb needs time to rest

    return str(succeed)


async def puppeteer_screenshot(archive_id, url_id, url):
    browser = await launch()
    page = await browser.newPage()
    await page.setViewport({'height': 768, 'width': 1024})
    await page.goto(url, timeout=(int(timeout_duration) * 1000))
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
        return -7
    except Exception as e:
        # other reasons such as "your connection is not secure"
        print(e)
        logging.info(e)
        return -8

    # check if redirected
    if conn.geturl() != url:
        print("Redirected to {}".format(conn.geturl()))
        logging.info("Redirected to {}".format(conn.geturl()))
        return 302

    # reaching this point means it received code 200
    print("Return code 200")
    logging.info("Return code 200")
    return 200


# for handling the command line switches
def parse_args():
    global input_url_file, pics_out_path, index_file, screenshot_method, usetxt, maketxt, timeout_duration
    parser = argparse.ArgumentParser()

    parser.add_argument("--txt", type=str, help="input txt file with urls")
    parser.add_argument("--db", type=str, help="input db file with urls")
    parser.add_argument("--picsout", type=str, help="path to output the screenshots")
    parser.add_argument("--indexout", type=str, help="file to output the index txt")
    parser.add_argument("--method", type=int, help="0 for chrome, 1 for puppeteer, 2 for cutycapt")
    parser.add_argument("--timeout", type=str,
                        help="specify duration before timeout, in seconds, default 30 seconds")

    args = parser.parse_args()

    # some command line argument error checking
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
        input_url_file = open(args.txt, "r")

    if args.db is not None:
        usetxt = False
        connect_sql(args.db)

    if args.indexout is not None:
        index_file = open(args.indexout, 'w+')
        maketxt = True
    else:
        maketxt = False

    if args.timeout is None:
        timeout_duration = "30"
    else:
        timeout_duration = args.timeout


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
    logging.basicConfig(filename=(pics_out_path + "current_screenshot_log.txt"), filemode='a',
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
