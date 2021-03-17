import argparse
import csv
import time
import urllib.request
import urllib.error
import logging


def	process_website(url, timeout_duration):
	"""Run	a request to see if	the	given url is available.

	Parameters
	----------
	url : str
		The url to check.
	timeout_duration : str
	    Duration before timeout when going to each website.

	Returns
	-------
	site_status : str
		LIVE if website can still	be reached or is redirected.
		FAIL if not.
	site_message :	str
		An error describing why the site can't be	reached	or a message saying	the	site was redirected.


	References
	----------
	..	[1]	https://stackoverflow.com/questions/1726402/in-python-how-do-i-use-urllib-to-see-if-a-website-is-404-or-200

	"""

	try:
		conn = urllib.request.urlopen(url, timeout = timeout_duration)
	except	urllib.error.HTTPError as e:
		#	Return code	error (e.g.	404, 501, ...)
		error_message	= 'HTTPError: {}'.format(e.code)
		print(error_message)
		logging.info(error_message)
		return "FAIL", error_message
	except	urllib.error.URLError as e:
		#	Not	an HTTP-specific error (e.g. connection	refused)
		error_message	= 'URLError: {}'.format(e.reason)
		print(error_message)
		logging.info(error_message)
		return "FAIL", error_message
	except	Exception as e:
		#	other reasons such as "your	connection is not secure"
		print(e)
		logging.info(e)
		return "FAIL", e
	except:
		#	broad exception	for	anything else
		print("Unknown error")
		logging.info("Unknown	error")
		return "FAIL", "Unknown error"

	# check if	redirected
	if conn.geturl() != url:
		print("Redirected	to {}".format(conn.geturl()))
		logging.info("Redirected to {}".format(conn.geturl()))
		return "LIVE", "Redirected to	{}".format(conn.geturl())

	# reaching	this point means it	received code 200
	print("Return code	200")
	logging.info("Return code 200")
	return	"LIVE",	"Return	code 200"



def	check_website(url, timeout_duration):
	"""Calls the function or command to take a	screenshot

	Parameters
	----------
	url : str
		The target url.
	timeout_duration : str
	    Duration before timeout when going to each website.

	Returns
	-------
	site_status : str
		LIVE if website can still	be reached or is redirected.
		FAIL if not.
	site_message :	str
		An error describing why the site can't be	reached	or a message saying	the	site was redirected.
	string: str
		Whether a website is still available

	"""

	site_status, site_message = process_website(url, timeout_duration)
	if	site_status	== "FAIL":
		return site_status, site_message,	"Website does not exist"
	else:
		return site_status, site_message,	"Website exists"




def	check_site_availability(csv_in_name, csv_out_name, timeout_duration):
	"""Fetches	urls from the input	CSV	and	takes a	screenshot

	Parameters
	----------
    csv_in_name : str
        The CSV file with the current urls.
    csv_out_name : str
        The CSV file to write the availablity results.
    timeout_duration : str
	    Duration before timeout when going to each website.
	"""

	with open(csv_in_name,	'r') as	csv_file_in:
		csv_reader = csv.reader(csv_file_in)
		with open(csv_out_name, 'w+')	as csv_file_out:
			csv_writer = csv.writer(csv_file_out, delimiter=',',	quoting=csv.QUOTE_ALL)
			csv_writer.writerow(["Id","url", "availability", "site_status", "site_message"])

			line_count =	0
			next(csv_reader)	 # skip	header
			url_counter = 1
			fail_counter = 0
			success_counter = 0
			while True:
				try:
					line =	next(csv_reader)
				except StopIteration:
					break
				line_count += 1

				url	= line[0]

				print("url[%d]: %s: "%(url_counter, url))
				site_status, site_message, availability =	check_website(url, timeout_duration)
				if availability == "Website does not exist":
					fail_counter += 1
				else:
					success_counter += 1

				csv_writer.writerow([url_counter, url, availability, site_status, site_message])
				url_counter += 1
	
	print("-"*10+"report"+"-"*10)
	print(" total url: %d \n available url: %d \n non-available url: %d" %(url_counter-1, success_counter, fail_counter))
	print("-"*10+"report"+"-"*10)


def parse_args():
    """Parses the arguments passed in from the command line.

    Returns
    ----------
    csv_in_name : str
        The CSV file with the current urls.
    csv_out_name : str
        The CSV file to write the availablity results.
    timeout_duration : str
	    Duration before timeout when going to each website.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", type=str, help="The CSV file with the current urls")
    parser.add_argument("--output", type=str, help="The CSV file to write the output")
    parser.add_argument("--timeout", type = str, help="(optional) Specify duration before timeout, in seconds, default 30 seconds")

    args = parser.parse_args()

    # some error checking
    if args.output is None:
        print("invalid output file\n")
        exit()
    if args.input is None:
        print("Must provide input file\n")
        exit()

    csv_in_name = args.input
    csv_out_name = args.output
    timeout_duration = args.timeout
    if timeout_duration is None:
        timeout_duration = 30
    else:
        try:
            timeout_duration = int(args.timeout)
        except:
            print("Invalid format for timeout")
            exit()

    return csv_in_name, csv_out_name, timeout_duration
				

def	main():
	csv_in_name, csv_out_name, timeout_duration = parse_args()
	print("Starting")
	check_site_availability(csv_in_name, csv_out_name, timeout_duration)


main()
