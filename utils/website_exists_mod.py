import argparse
import csv
import time
import urllib.request
import urllib.error
import logging
import socket


def	check_website_availability(url, timeout_duration):
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
		if isinstance(e.reason, socket.timeout):
			print(error_message)
			logging.info(error_message)
			return "LIVE", error_message
		else:
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



def	is_website_exist(url, timeout_duration):
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

	site_status, site_message = check_website_availability(url, timeout_duration)
	if	site_status	== "FAIL":
		return site_status, site_message,	"Website does not exist"
	else:
		return site_status, site_message,	"Website exists"


