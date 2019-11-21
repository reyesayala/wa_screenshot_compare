import argparse
import asyncio
import csv
import urllib.request
import urllib.error
import logging
from pyppeteer import launch
from pyppeteer import errors


def screenshot_csv(csv_in_name, csv_out_name, pics_out_path, timeout_duration):
    with open(csv_in_name, 'r') as csv_file_in:
        csv_reader = csv.reader(csv_file_in)
        with open(csv_out_name, 'w+', newline='') as csv_file_out:
            csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
            csv_writer.writerow(["archive_id", "url_id", "url", "site_status", "site_message", "screenshot_message"])

            next(csv_reader)  # skip header
            while True:
                try:
                    line = next(csv_reader)
                except StopIteration:
                    break

                archive_id = line[0]
                url_id = line[1]
                url = line[2]

                print("\nurl #{0} {1}".format(url_id, url))

                site_status, site_message, screenshot_message = \
                    take_screenshot(archive_id, url_id, url, pics_out_path, timeout_duration)

                print("\nurl #{0} {1}".format(url_id, url))
                logging.info("url #{0} {1}".format(url_id, url))

                csv_writer.writerow([archive_id, url_id, url, site_status, site_message, screenshot_message])


def take_screenshot(archive_id, url_id, url, pics_out_path, timeout_duration):
    site_status, site_message = check_site_availability(url)
    if site_status == "FAIL":
        return site_status, site_message, "Screenshot unsuccessful"

    try:
        asyncio.get_event_loop().run_until_complete(
            puppeteer_screenshot(archive_id, url_id, url, pics_out_path, timeout_duration))
        logging.info("Screenshot successful")
        print("Screenshot successful")
        return site_status, site_message, "Screenshot successful"
    except errors.TimeoutError as e:
        print(e)
        logging.info(e)
        return site_status, site_message, e
    except errors.NetworkError as e:
        print(e)
        logging.info(e)
        return site_status, site_message, e
    except errors.PageError as e:
        print(e)
        logging.info(e)
        return site_status, site_message, e
    except Exception as e:
        print(e)
        logging.info(e)
        return site_status, site_message, e
    except asyncio.futures.InvalidStateError as e:
        print(e)
        logging.info(e)
        return site_status, site_message, e
    except asyncio.streams.IncompleteReadError as e:
        print(e)
        logging.info(e)
        return site_status, site_message, e


async def puppeteer_screenshot(archive_id, url_id, url, pics_out_path, timeout_duration):
    browser = await launch(headless=True, dumpio=True)
    page = await browser.newPage()
    try:
        await page.setViewport({'height': 768, 'width': 1024})
        await page.goto(url, timeout=(int(timeout_duration) * 1000))
        await page.waitFor(1000)
        await page.reload(timeout=(int(timeout_duration) * 1000))    # reloading a site can get rid of certain popups

        await click_button(page, "I Accept")        # click through popups and banners, there could be a lot more
        await click_button(page, "I Understand")
        await click_button(page, "I Agree")
        await click_button(page, "Accept Recommended Settings")
        await click_button(page, "Close")
        await click_button(page, "Close and Accept")
        await click_button(page, "OK")
        await click_button(page, "OK, I Understand.")
        await click_button(page, "Accept")
        await click_button(page, "Accept Cookies")
        await click_button(page, "No Thanks")
        await page.keyboard.press("Escape")

        await page.screenshot(path='{0}{1}.{2}.png'.format(pics_out_path, archive_id, url_id))
    except Exception as e:
        # https://github.com/GoogleChrome/puppeteer/issues/2269
        try:
            await page.close()
            await browser.close()
        except:
            await browser.close()
        raise e

    try:
        await page.close()
        await browser.close()
    except:
        await browser.close()


async def click_button(page, button_text):
    await page.evaluate('''query => {
      const elements = [...document.querySelectorAll('button')];
      const targetElement = elements.find(e => e.innerText.toLowerCase().includes(query));
      targetElement && targetElement.click();
      }''', button_text.lower())


def check_site_availability(url):
    try:
        conn = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        # Return code error (e.g. 404, 501, ...)
        error_message = 'HTTPError: {}'.format(e.code)
        print(error_message)
        logging.info(error_message)
        return "FAIL", error_message
    except urllib.error.URLError as e:
        # Not an HTTP-specific error (e.g. connection refused)
        error_message = 'URLError: {}'.format(e.reason)
        print(error_message)
        logging.info(error_message)
        return "FAIL", error_message
    except Exception as e:
        # other reasons such as "your connection is not secure"
        print(e)
        logging.info(e)
        return "FAIL", e

    # check if redirected
    if conn.geturl() != url:
        print("Redirected to {}".format(conn.geturl()))
        logging.info("Redirected to {}".format(conn.geturl()))
        return "LIVE", "Redirected to {}".format(conn.geturl())

    # reaching this point means it received code 200
    print("Return code 200")
    logging.info("Return code 200")
    return "LIVE", "Return code 200"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, help="Input CSV file with current urls")
    parser.add_argument("--picsout", type=str, help="Directory to output the screenshots")
    parser.add_argument("--indexcsv", type=str, help="The CSV file to write the index")
    parser.add_argument("--timeout", type=str, help="(optional) Specify duration before timeout for each site, "
                                                    "in seconds, default 30 seconds")
    args = parser.parse_args()

    # some command line argument error checking
    if args.indexcsv is None:
        print("invalid output index file\n")
        exit()
    if args.csv is None:
        print("Must provide input file\n")
        exit()
    if args.picsout is None:
        print("Must specify output path for pictures\n")
        exit()

    pics_out_path = args.picsout + '/'
    csv_in_name = args.csv
    csv_out_name = args.indexcsv

    if args.timeout is None:
        timeout_duration = "30"
    else:
        timeout_duration = args.timeout

    return csv_in_name, csv_out_name, pics_out_path, timeout_duration


def set_up_logging(pics_out_path):
    """Setting up logging format.

    Parameters
    ----------
    pics_out_path : str
        Directory to output the screenshots.

    Notes
    -----
    logging parameters:
        filename: the file to output the logs
        filemode: a as in append
        format:   format of the message
        datefmt:  format of the date in the message, date-month-year hour:minute:second AM/PM
        level:    minimum message level accepted

    """

    logging.basicConfig(filename=(pics_out_path + "archive_screenshot_log.txt"), filemode='a',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S %p', level=logging.INFO)


def main():
    csv_in_name, csv_out_name, pics_out_path, timeout_duration = parse_args()
    set_up_logging(pics_out_path)
    print("Taking screenshots")
    screenshot_csv(csv_in_name, csv_out_name, pics_out_path, timeout_duration)


main()
