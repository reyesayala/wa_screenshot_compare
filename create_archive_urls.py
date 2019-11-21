import argparse
import csv
import urllib.request
import urllib.error
import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup


def create_with_csv(csv_out_name, csv_in_name):
    archive_header = "https://www.webarchive.org.uk/wayback/archive/*/"

    with open(csv_in_name, "r") as csv_file_in:
        csv_reader = csv.reader(csv_file_in)
        with open(csv_out_name, "w+", newline='') as csv_file_out:
            csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
            csv_writer.writerow(["archive_name", "url_id", "position", "archive_url"])

            next(csv_reader)  # skip header
            line_number = 0
            while True:
                line_number += 1
                try:
                    line = next(csv_reader)
                except StopIteration:
                    break

                archive_name = line[0]
                url_id = line[1]
                current_url = line[2]
                archive_directory_url = "{0}{1}".format(archive_header, current_url)

                print("URL #" + str(line_number))

                try:
                    html = asyncio.get_event_loop().run_until_complete(fetch_html(archive_directory_url))
                except:
                    continue

                soup = BeautifulSoup(html, features='html.parser')
                for htmldiv in soup.findAll('div'):
                    if htmldiv.get('id') == "captureYears":
                        for montha in htmldiv.findAll('a'):
                            found_url = montha.get('href')
                            if found_url is not None:
                                date = found_url.split('/')[5]
                                csv_writer.writerow([archive_name, url_id, date, found_url])


async def fetch_html(url):
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.setViewport({'height': 768, 'width': 1024})
    await page.goto(url, timeout=60000)
    await page.waitFor(1000)
    html = await page.evaluate('''() => document.body.innerHTML''')

    await page.close()
    await browser.close()
    return html


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, help="Input CSV file with current urls")
    parser.add_argument("--out", type=str, help="The CSV file to write the urls")
    args = parser.parse_args()

    # some error checking
    if args.csv is None:
        print("Must include input file\n")
        exit()
    if args.out is None:
        print("Must specify output location\n")
        exit()

    csv_in_name = args.csv
    csv_out_name = args.out

    return csv_out_name, csv_in_name


def main():
    csv_out_name, csv_in_name = parse_args()
    print("Getting archive urls...")
    create_with_csv(csv_out_name, csv_in_name)


main()
