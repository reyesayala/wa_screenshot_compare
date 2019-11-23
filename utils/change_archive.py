import csv
import sys
import requests
from tqdm import tqdm

def main():
    input_csv = sys.argv[1]

    output_csv = input_csv[:-4] + '_new.csv'
    output_rows = []

    new_archive = 'https://web.archive.org/web/'        # the prefix of new url

    with open(input_csv) as f:
        f_csv = csv.reader(f)
        headers = next(f_csv)                                  # get the header

        for row in tqdm(f_csv):
            input_url = row[3]                                # get the old url
            date = row[2]                                        # get the date
            date_index = input_url.index(date)              # get index of date
            archive_url = input_url[date_index:]        # extract url from date
            new_url = new_archive + archive_url # replaced url, request it next

            try:                                         # try request with url
                page = requests.get(new_url)
                url_with_closest_date = page.url
                date_index_start = url_with_closest_date.index('web/') + 4
                date_index_end = date_index_start + 14
                closest_date = url_with_closest_date[date_index_start:date_index_end]
            except:                                          # if request fails
                url_with_closest_date = input_url             # use the old url
                closest_date = date

            page.close()

            output_row = row
            output_row[2] = closest_date           # replace date with new date
            output_row[3] = url_with_closest_date        # replace with new url
            output_rows.append(output_row)
            
    with open(output_csv, 'w+') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)                    # write the header to output
        for row in output_rows:
            f_csv.writerow(row)                      # write the rows to output

    print('Program finished, the output file is {}\n'.format(output_csv))

main()
