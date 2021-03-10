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


def	check_site_availability(url):
	"""Run	a request to see if	the	given url is available.

	Parameters
	----------
	url : str
		The url to check.

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
		conn = urllib.request.urlopen(url)
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
	if	conn.geturl() != url:
		print("Redirected	to {}".format(conn.geturl()))
		logging.info("Redirected to {}".format(conn.geturl()))
		return "LIVE", "Redirected to	{}".format(conn.geturl())

	# reaching	this point means it	received code 200
	print("Return code	200")
	logging.info("Return code 200")
	return	"LIVE",	"Return	code 200"

def	take_screenshot(url):
	"""Calls the function or command to take a	screenshot

	Parameters
	----------
	archive_id	: str
		The archive ID.
	url_id	: str
		The url ID.
	url : str
		The url to take a	screenshot of.
	pics_out_path : str
		Directory	to output the screenshots.
	timeout_duration :	str
		Duration before timeout when going to	each website.
	screenshot_method : int
		Which	method to take the screenshots,	0 for chrome, 1	for	puppeteer, 2 for cutycapt.
	chrome_args : list
		Contains extra arguments for chrome that can be passed into pyppeteer. None if no	additional arguments.
	screensize	: list
		Contains two int which are height	and	width of the browser viewport.
	keep_cookies :	bool
		Whether or not to	run	click_button() to attempt to remove	cookies	banners. False to remove.
		
	Returns
	-------
	site_status : str
		LIVE if website can still	be reached or is redirected.
		FAIL if not.
	site_message :	str
		An error describing why the site can't be	reached	or a message saying	the	site was redirected.
	screenshot_message	: str
		Message indicating whether the screenshot	was	successful.

	"""

	site_status, site_message = check_site_availability(url)
	if	site_status	== "FAIL":
		return site_status, site_message,	"Website does not exist"
	else:
		return site_status, site_message,	"Website exists"




def	screenshot_csv(csv_in_name,	csv_out_name):
	"""Fetches	urls from the input	CSV	and	takes a	screenshot

	Parameters
	----------
	csv_in_name : str
		The CSV file with	the	current	urls.
	csv_out_name :	str
		The CSV file to write	the	index.
	pics_out_path : str
		Directory	to output the screenshots.
	screenshot_method : int
		Which	method to take the screenshots,	0 for chrome, 1	for	puppeteer, 2 for cutycapt.
	timeout_duration :	str
		Duration before timeout when going to	each website.
	read_range	: list
		Contains two int which tell the programs to only take	screenshots	between	these lines	in the csv_in.
	chrome_args : list
		Contains extra arguments for chrome that can be passed into pyppeteer. None if no	additional arguments.
	screensize	: list
		Contains two int which are height	and	width of the browser viewport.
	keep_cookies :	bool
		Whether or not to	run	click_button() to attempt to remove	cookies	banners. False to remove.
	"""

	with open(csv_in_name,	'r') as	csv_file_in:
		csv_reader = csv.reader(csv_file_in)
		with open(csv_out_name, 'w+')	as csv_file_out:
			csv_writer =	csv.writer(csv_file_out, delimiter=',',	quoting=csv.QUOTE_ALL)
			csv_writer.writerow(["url", "site_status", "site_message"])

			line_count =	0
			next(csv_reader)	 # skip	header
			while True:
				try:
					line =	next(csv_reader)
				except StopIteration:
					break
				line_count += 1

				url	= line[0]

				print(url)

				site_status, site_message, screenshot_message =	take_screenshot(url)

				csv_writer.writerow([url, site_status, site_message])
				

def	main():
	print("Starting")
	screenshot_csv("wildfires_urls.txt", "wildfires_site_availability.csv")


main()
