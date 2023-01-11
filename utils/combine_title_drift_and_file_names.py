import argparse
import sqlite3
import csv
import requests
from bs4 import BeautifulSoup
import sys

def search(archive_url, scores_file):
    scores_dict = csv.DictReader(open(scores_file))
    print("Searching")
    
    result_lst = []
        
    for line in scores_dict:
        score_url = line["archive_url"]
        if(archive_url != score_url):
         continue
            
        else:
         print("Found it!")
         result_lst.extend([line["current_file_name"], line["archive_file_name"], line["ssim_score"], line["mse_score"], line["vector_score"], line["phash_score"]])
         



         break
    return(result_lst)


def create_output_file_with_scores(title_drift_file, scores_file, csv_out):
    """Finds the image files names and similarity scores for each current/archived image pair in scores file.
       Begins by opening title drift file and extracting archived URL, then it looks into scores file for a match. 
       If found, it extracts the image file names and similarity scores and writes all of the columns (old + new)
       to the output file. If not found, it will write only the old columns + blanks. 
    Parameters
    ----------
    title_drift_file : str
        The CSV file with the title_drift judgments
    scores_file : str
        The CSV file with the similarity scores calculated
    csv_out_name : str
        The CSV file to write merged file.

    """


    
    title_drift_dict = csv.DictReader(open(title_drift_file))
    


    print("Start")
    with open(csv_out, 'w', newline='') as csvfile:
        fieldnames = ["current_url","archive_url","current_title","archive_title","similarity_score","content_drift","Note",
                      "RA notes","current_pic","archive_pic","ssim_score","mse_score","vector_score","phash_score"]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        result_lst = []

        for row in title_drift_dict:
          archive_url = row["archive_url"]
          print("Archive url ", archive_url)
          result_lst = search(archive_url, scores_file)


          if(result_lst):  
              row["current_pic"] = result_lst[0]
              row["archive_pic"] = result_lst[1]
              row["ssim_score"] = result_lst[2]
              row["mse_score"] = result_lst[3]
              row["vector_score"] = result_lst[4]
              row["phash_score"] = result_lst[5]
          else:
              row["current_pic"] = ""
              row["archive_pic"] = ""
              row["ssim_score"] = ""
              row["mse_score"] = ""
              row["vector_score"] = ""
              row["phash_score"] = ""

          writer.writerow(row)
          print(row)

    """
    

    
    writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})
    writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam'})
    """
    print("done")
    
     
     

def main():

    title_drift_file = sys.argv[1]
    scores_file = sys.argv[2]
    csv_out = sys.argv[3]

    print("Getting title drift file: ", title_drift_file)
    print("Getting scores file: ", scores_file)
    create_output_file_with_scores(title_drift_file, scores_file, csv_out)


main()
