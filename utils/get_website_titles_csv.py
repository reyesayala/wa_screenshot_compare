import bs4
import urllib.request
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import argparse
import csv
import logging
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver import FirefoxOptions

def get_cosine_similarity(archive_title,current_title):

    X = current_title.lower()
    Y = archive_title.lower()

    # tokenization
    X_list = word_tokenize(X) 
    Y_list = word_tokenize(Y)

    # sw contains the list of stopwords
    sw = stopwords.words('english') 
    l1 =[];l2 =[]

    # remove stop words from the string
    X_set = {w for w in X_list if not w in sw} 
    Y_set = {w for w in Y_list if not w in sw}

    # form a set containing keywords of both strings 
    rvector = X_set.union(Y_set) 
    for w in rvector:
        if w in X_set: l1.append(1) # create a vector
        else: l1.append(0)
        if w in Y_set: l2.append(1)
        else: l2.append(0)
    c = 0

    # cosine formula 
    for i in range(len(rvector)):
            c+= l1[i]*l2[i]

    divisor =  float((sum(l1)*sum(l2))**0.5)

    if (divisor == 0):
        cosine = 0
    else:
        cosine = c / divisor
    
    
    return(cosine)


def content_drift_check(csv_in, csv_out, threshold):
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(firefox_options=opts)

    with open(csv_in, 'r') as csv_file_in:
        csv_reader = csv.reader(csv_file_in)
        with open(csv_out, 'w+') as csv_file_out:
            csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
            csv_writer.writerow(
                ["current_url", "archive_url", "current_title", "archive_title", "similarity_score", "content_drift", "Note"])

            line_count = 0
            next(csv_reader)  # skip header

            while True:
                try:
                    line = next(csv_reader)
                except StopIteration:
                    break
                line_count += 1

                cur_url = line[0];
                archive_url = line[1];

                try:
                    print("current_url: ", cur_url);
                    print("archive_url: ", archive_url);
                    current_title = (bs4.BeautifulSoup(urllib.request.urlopen(cur_url), "html.parser")).title.text
                    archive_title = (bs4.BeautifulSoup(urllib.request.urlopen(archive_url), "html.parser")).title.text
                    cur_note = ""

                    # current_title_soup = (bs4.BeautifulSoup(urllib.request.urlopen(cur_url), "html.parser"))
                    # current_title = current_title_soup.find("title").text
                    # archive_title_soup = (bs4.BeautifulSoup(urllib.request.urlopen(archive_url), "html.parser"))
                    # archive_title = archive_title_soup.find("title").text

                    # session = HTMLSession()
                    # current_response = session.get(cur_url);
                    # current_soup = BeautifulSoup(current_response.content, 'html.parser');
                    # current_title = current_soup.find("title").text
                    # archive_response = session.get(archive_url)
                    # archive_soup = BeautifulSoup(archive_response.content, 'html.parser');
                    # archive_title = archive_soup.find("title").text
                except Exception as e:
                    print("html Error Message: Getting title error")
                    print(e)
                    logging.info("html Error Message: Getting title error")
                    logging.info("html - current url: #{0}\n; archive url{1};".format(cur_url, archive_url))
                    logging.info(e)
                    try:
                        driver.get(cur_url)
                        current_title = driver.title
                        driver.close()
                        driver.get(archive_url)
                        archive_title = driver.title
                        driver.close()
                    except Exception as e:
                        print("selenium Error Message: Getting title error")
                        print(e)
                        logging.info("selenium Error Message: Getting title error")
                        logging.info("selenium - current url: #{0}\n; archive url{1};".format(cur_url, archive_url))
                        logging.info(e)
                        current_title = "_NAN_"
                        archive_title = "_NAN_"
                        cur_note = cur_note + "Error Retriving Title"

                try:
                    print("getting similarity score")
                    if (current_title == "_NAN_" or archive_title == "_NAN_"):
                        similarity = "_NAN_"
                        content_flag = "_NAN_"
                    else:
                        similarity = get_cosine_similarity(archive_title, current_title)
                        if(similarity > threshold):
                            content_flag = "On-topic"
                        else:
                            content_flag = "Off-topic"
                    print("score: ", similarity)
                    print("content_drift: ", content_flag)
                except Exception as e:
                    print("Error Message: Similarity error")
                    print(e)
                    logging.info("Error Message: Getting Similarity error")
                    logging.info("current url: #{0}\n; archive url{1}".format(cur_url, archive_url))
                    logging.info(e)
                    similarity = "_NAN_"
                    content_flag = "_NAN_"
                    cur_note = cur_note + "Error Calculating Similarity"
                
                csv_writer.writerow([cur_url, archive_url, current_title, archive_title, similarity, content_flag, cur_note])
    driver.quit()

def set_up_logging(log_out):
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

    logging.basicConfig(filename=(log_out), filemode='a',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S %p', level=logging.INFO)

def	parse_args():
	"""Parses the command line	arguments.
	Returns
	args.csv_in : str
		csv	with urls.
	args.csv_out :	str
		The CSV file to write the content drift status.

	"""

	parser	= argparse.ArgumentParser()
	parser.add_argument("--csv_in", type=str, help="Directory of csv with websites urls")
	parser.add_argument("--csv_out", type=str,	help="The file name	to write the content drift result")
	parser.add_argument("--log_out", type=str,	help="The file name	to write the log files")
	parser.add_argument("--threshold", type=float, help="The threshold value for the similiarity comparison (range: [0, 1])")

	args =	parser.parse_args()

	# some	error checking
	if	args.csv_in is None:
		print("Must provide input csv directory")
		exit()
	if	args.csv_out is	None:
		print("Must provide output file")
		exit()
	if	args.log_out is	None:
		args.log_out = args.csv_out[:-4] + "_log.txt"
	if	args.threshold is None:
		args.threshold = 0.6

	return	args.csv_in, args.csv_out, args.log_out, args.threshold


def	main():
	csv_in, csv_out, log_out, threshold= parse_args()

	print("Reading	the	input files	...")
	set_up_logging(log_out);
	content_drift_check(csv_in,	csv_out, threshold)



main()



