import csv
import sys
import requests
import math

def main():
    input_csv = sys.argv[1]

    output_csv = input_csv[:-4] + '_dup_removed.csv'
    output_rows = []

    """
    The algorithm below assumes the input csv file has duplicated archive urls
    sorted by their date/position.
    i.e., two rows with the same id would be sorted in ascending order by the 
    date/position.
    """
    with open(input_csv) as f:
        f_csv = csv.reader(f)
        headers = next(f_csv)                                  # get the header
        first_row = next(f_csv)                             # get the first row

        prev_url = first_row[0]                       # get the first row's url
        prev_row = first_row                                # get the first row
        
        for row in (f_csv):

            cur_url = row[0]                             # get current row's id

            if cur_url != prev_url:
                output_rows.append(prev_row)# append the previous row to output

            prev_url = cur_url                                 # update prev_id
            prev_row = row                                    # update prev_row
        
        output_rows.append(prev_row)                       # write the last row
    
    with open(output_csv, 'w+') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)                    # write the header to output
        for row in output_rows:
            f_csv.writerow(row)                      # write the rows to output

main()