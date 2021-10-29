import argparse
import asyncio
import os
import sqlite3
import csv
import time
import urllib.request
import urllib.error
from pyppeteer import launch
from pyppeteer import errors
import logging
import signal
import re
from PIL import Image
import sys
sys.path.insert(0, './utils/')
from website_exists_mod import *

def screenshot_csv(csv_in_name, csv_out_name, pics_out_path, screenshot_method, timeout_duration, read_range,
                   chrome_args, screensize, keep_cookies):
    """Fetches urls from the input CSV and takes a screenshot

    Parameters
    ----------
    csv_in_name : str
        The CSV file with the current urls.
    csv_out_name : str
        The CSV file to write the index.
    pics_out_path : str
        Directory to output the screenshots.
    screenshot_method : int
        Which method to take the screenshots, 0 for chrome, 1 for puppeteer, 2 for cutycapt, 3 for selenium.
    timeout_duration : str
        Duration before timeout when going to each website.
    read_range : list
        Contains two int which tell the programs to only take screenshots between these lines in the csv_in.
    chrome_args : list
        Contains extra arguments for chrome that can be passed into pyppeteer. None if no additional arguments.
    screensize : list
        Contains two int which are height and width of the browser viewport.
    keep_cookies : bool
        Whether or not to run click_button() to attempt to remove cookies banners. False to remove.
    """

    with open(csv_in_name, 'r') as csv_file_in:
        csv_reader = csv.reader(csv_file_in)
        with open(csv_out_name, 'w+') as csv_file_out:
            csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
            csv_writer.writerow(["archive_id", "url_id", "url", "site_status", "site_message", "screenshot_message"])

            line_count = 0
            next(csv_reader)  # skip header
            while True:
                try:
                    line = next(csv_reader)
                except StopIteration:
                    break
                line_count += 1

                if (read_range[0] != None) and (read_range[1] != None):  # skip if not within range
                    if line_count < read_range[0] or line_count > read_range[1]:
                        continue

                archive_id = line[0]
                url_id = line[1]
                url = line[2]

                print("\nurl #{0} {1}".format(url_id, url))
                logging.info("url #{0} {1}".format(url_id, url))

                site_status, site_message, screenshot_message = take_screenshot(archive_id, url_id, url, pics_out_path,
                    screenshot_method, timeout_duration, chrome_args, screensize, keep_cookies)

                csv_writer.writerow([archive_id, url_id, url, site_status, site_message, screenshot_message])


def take_screenshot(archive_id, url_id, url, pics_out_path, screenshot_method, timeout_duration, chrome_args, screensize, keep_cookies):
    """Calls the function or command to take a screenshot

    Parameters
    ----------
    archive_id : str
        The archive ID.
    url_id : str
        The url ID.
    url : str
        The url to take a screenshot of.
    pics_out_path : str
        Directory to output the screenshots.
    timeout_duration : str
        Duration before timeout when going to each website.
    screenshot_method : int
        Which method to take the screenshots, 0 for chrome, 1 for puppeteer, 2 for cutycapt.
    chrome_args : list
        Contains extra arguments for chrome that can be passed into pyppeteer. None if no additional arguments.
    screensize : list
        Contains two int which are height and width of the browser viewport.
    keep_cookies : bool
        Whether or not to run click_button() to attempt to remove cookies banners. False to remove.

    Returns
    -------
    site_status : str
        LIVE if website can still be reached or is redirected.
        FAIL if not.
    site_message : str
        An error describing why the site can't be reached or a message saying the site was redirected.
    screenshot_message : str
        Message indicating whether the screenshot was successful.

    """

    site_status, site_message, availability = is_website_exist(url, 10)
    if site_status == "FAIL":
        logging.info("Website does not exist")
        print("*"*20)
        print("wesite not exist")
        return site_status, site_message, "Screenshot unsuccessful"

    if screenshot_method == 0:
        return site_status, site_message, chrome_screenshot(pics_out_path, archive_id, url_id, url, timeout_duration)
    elif screenshot_method == 2:
        return site_status, site_message, cutycapt_screenshot(pics_out_path, archive_id, url_id, url, timeout_duration)
    elif screenshot_method == 3:
        return site_status, site_message, selenium_screenshot(pics_out_path, archive_id, url_id, url, timeout_duration)
    elif screenshot_method == 1:
        try:
            signal.alarm(timeout_duration * 2 + 60)  # timer for when asyncio stalls on a invalid state error
            loop = asyncio.get_event_loop()
            task = asyncio.gather(puppeteer_screenshot(archive_id, url_id, url, pics_out_path, timeout_duration,
                                                       chrome_args, screensize, keep_cookies))
            result = loop.run_until_complete(task)
            #logging.info(result)
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
        except TimeoutError as e:
            print(e)
            logging.info(e)
            return site_status, site_message, e
        except:
            print("Unknown error")
            logging.info("Unknown error")
            return site_status, site_message, "Unknown error"


def chrome_screenshot(pics_out_path, archive_id, url_id, url, timeout_duration):
    # not fully implemented
    command = "google-chrome --headless --hide-scrollbars --no-sandbox --aggressive-cache-discard --aggressive-tab-discard --timeout=600000" \
              "--screenshot={0}{1}.{2}.jpg --window-size=1024x768 '{3}'" \
        .format(pics_out_path, archive_id, url_id, url)
    try:
        if os.system(command) == 0:
            logging.info("Screenshot successful")
            print("Screenshot successful")
            return "Screenshot successful"
        else:
            logging.info("Screenshot unsuccessful")
            print("Screenshot unsuccessful")
            return "Screenshot unsuccessful"
    except:  # unknown error
        logging.info("Screenshot unsuccessful")
        print("Screenshot unsuccessful")
        return "Screenshot unsuccessful"


def selenium_screenshot(pics_out_path, archive_id, url_id, url, timeout_duration):
    
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import os

    print("Loading Selenium")
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    
    try:
       driver.get(url)
       print("Loading Selenium 2")	
       S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
       print("Loading Selenium 3")
       driver.set_window_size(S('Width'),S('Height')) # May need manual adjustment 
       print("Loading Selenium 4")
       output_file_name = pics_out_path+archive_id+"."+url_id+".png"
       print("Loading Selenium 5")	
       print("Output file name: ", output_file_name)
       driver.find_element_by_tag_name('body').screenshot(output_file_name)
       print("Screenshot successful")
       driver.quit()
       return "Screenshot successful"

    except:  # unknown error
        logging.info("Screenshot unsuccessful")
        print("Screenshot unsuccessful")
        return "Screenshot unsuccessful"
    
    
def cutycapt_screenshot(pics_out_path, archive_id, url_id, url, timeout_duration):
    command = "timeout {5}s xvfb-run -e /dev/stdout --server-args=\"-screen 0, 1024x768x24\" " \
              "/usr/bin/cutycapt --url='{0}' --out={1}{2}.{3}.png --delay=2000  --max-wait={4} --private-browsing=on --plugins=off" \
        .format(url, pics_out_path, archive_id, url_id, timeout_duration*1000, timeout_duration+10)
    print(command)
    try:
        time.sleep(1)  # cutycapt needs to rest
        c_out = os.system(command)
        if (c_out == 0 or c_out == 31744):
            logging.info("Screenshot successful")
            print("Screenshot successful")
            filename = archive_id+"."+url_id+".png"
            print(filename)
            return "Screenshot successful"
        else:
            logging.info("Screenshot unsuccessful")
            logging.info("process exit value: %d" % c_out)
            print("Screenshot unsuccessful")
            return "Screenshot unsuccessful"
    except Exception as e:  # unknown error
        print(e)
        logging.info("Screenshot unsuccessful")
        print("Screenshot unsuccessful")
        logging.info("process exit value: %d" % c_out)
        print("process exit value: %d" % c_out)
        return "Screenshot unsuccessful"

        


async def puppeteer_screenshot(archive_id, url_id, url, pics_out_path, timeout_duration, chrome_args, screensize, keep_cookies):
    """Take screenshot using the pyppeteer package.

    Parameters
    ----------
    archive_id : str
        The archive ID.
    url_id : str
        The url ID.
    url : str
        The url to take a screenshot of.
    pics_out_path : str
        Directory to output the screenshots.
    timeout_duration : str
        Duration before timeout when going to each website.
    chrome_args : list
        Contains extra arguments for chrome that can be passed into pyppeteer. None if no additional arguments.
    screensize : list
        Contains two int which are height and width of the browser viewport.
    keep_cookies : bool
        Whether or not to run click_button() to attempt to remove cookies banners. False to remove.

    References
    ----------
    .. [1] https://pypi.org/project/pyppeteer/

    .. [2] https://github.com/ukwa/webrender-puppeteer/blob/6fcc719d64dc19a4929c02d3a445a8283bee5195/renderer.js

    """

    browser = await launch(headless=True, dumpio=True, args=chrome_args)
    page = await browser.newPage()
    try:
        await page.setViewport({'height': screensize[0], 'width': screensize[1]})
        await page.goto(url, timeout=(timeout_duration * 1000))
        await page.waitFor(1000)
        await page.reload(timeout=(timeout_duration * 1000))    # reloading a site can get rid of certain popups

        if not keep_cookies:
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

        await page.screenshot(path='{0}{1}.{2}.jpg'.format(pics_out_path, archive_id, url_id))

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
    """Execute js script on page to click button

    Parameters
    ----------
    page : pyppeteer.page.Page
        The page to go through
    button_text: str
        Name of the button to click

    References
    ----------
    .. [1] https://github.com/ukwa/webrender-puppeteer/blob/6fcc719d64dc19a4929c02d3a445a8283bee5195/renderer.js

    Notes
    -----
    Right now only clicks popups and banners that are buttons, but some sites have banners with using a or wb_divs


    """
    await page.evaluate('''query => {
      const elements = [...document.querySelectorAll('button')];
      const targetElement = elements.find(e => e.innerText.toLowerCase().includes(query));
      targetElement && targetElement.click();
      }''', button_text.lower())


def check_site_availability(url):
    """Run a request to see if the given url is available.

    Parameters
    ----------
    url : str
        The url to check.

    Returns
    -------
    site_status : str
        LIVE if website can still be reached or is redirected.
        FAIL if not.
    site_message : str
        An error describing why the site can't be reached or a message saying the site was redirected.


    References
    ----------
    .. [1] https://stackoverflow.com/questions/1726402/in-python-how-do-i-use-urllib-to-see-if-a-website-is-404-or-200

    """

    try:
        conn = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        # Return code error (e.g. 404, 501, ...)
        try:
            conn.close()
        except:
            print("Process close error")
        finally:
            error_message = 'HTTPError: {}'.format(e.code)
            print(error_message)
            logging.info(error_message)
            return "FAIL", error_message
    except urllib.error.URLError as e:
        # Not an HTTP-specific error (e.g. connection refused)
        try:
            conn.close()
        except:
            print("Process close error")
        finally:
            error_message = 'URLError: {}'.format(e.reason)
            print(error_message)
            logging.info(error_message)
            return "FAIL", error_message
    except Exception as e:
        # other reasons such as "your connection is not secure"
        try:
            conn.close()
        except:
            print("Process close error")
        finally:
            print(e)
            logging.info(e)
            return "FAIL", e
    except:
        # broad exception for anything else
        try:
            conn.close()
        except:
            print("Process close error")
        finally:
            print("Unknown error")
            logging.info("Unknown error")
            return "FAIL", "Unknown error"

    # check if redirected
    if conn.geturl() != url:
        print("Redirected to {}".format(conn.geturl()))
        logging.info("Redirected to {}".format(conn.geturl()))
        conn.close()
        return "LIVE", "Redirected to {}".format(conn.geturl())

    # reaching this point means it received code 200
    print("Return code 200")
    logging.info("Return code 200")
    conn.close()
    return "LIVE", "Return code 200"


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
        datefmt:  format of the date in the message, month-day-year hour:minute:second AM/PM
        level:    minimum message level accepted

    """

    logging.basicConfig(filename=(pics_out_path + "current_screenshot_log.txt"), filemode='a',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S %p', level=logging.INFO)


def signal_handler_sigint(sig, frame):
    # sigint handler for debugging
    raise Exception("User interrupted")


def signal_handler_sigalrm(sig, frame):
    # sigalrm handler for a rare asyncio invalid state error
    raise TimeoutError("Timeout Error")


def main():


    signal.signal(signal.SIGINT, signal_handler_sigint)
    signal.signal(signal.SIGALRM, signal_handler_sigalrm)

    import read_config_file
    import config

    print("Taking screenshots")
    #create_with_csv(config.archive_urls_csv, config.current_urls_csv, config.banner)
    if not os.path.exists(config.current_pics_dir):
        os.makedirs(config.current_pics_dir)

    set_up_logging(config.current_pics_dir)
    print(config.c_screen_width)
    screenshot_csv(config.current_urls_csv, config.current_index_csv, config.current_pics_dir, config.c_method, config.c_timeout, [config.c_range_min, config.c_range_max], config.c_chrome_args, [config.c_screen_height, config.c_screen_width], config.c_keep_cookies)

    print("The current screenshots have been created in this directory: ", config.current_pics_dir)


main()
