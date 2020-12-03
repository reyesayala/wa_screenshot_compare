import argparse
import csv
import importlib
from PIL import	Image
from PIL import	ImageChops
import os

#adapted from https://stackoverflow.com/questions/14041562/python-pil-detect-if-an-image-is-completely-black-or-white

def	image_is_black(image_file):
	if	not	image_file.getbbox():
		#print("Image	is completely black")
		return(True)
	else:
		return(False)
		
def	image_is_white(image_file):
	if	not	ImageChops.invert(image_file).getbbox():
		#print("Image	is completely white")
		return(True)
	else:
		return(False)



def	find_blank_images(image_dir, csv_out_name):	

	file_list = os.listdir(image_dir)
	with open(csv_out_name, 'w') as csv_file_out:
		csv_writer = csv.writer(csv_file_out,	delimiter=',', quoting=csv.QUOTE_ALL)

		header = ["blank_image_file_name"]
		csv_writer.writerow(header)

		
		for filename in file_list:
			try:
				im =	Image.open(image_dir+filename)
				if(image_is_black(im)) or (image_is_white(im)):
					print("Image: ", image_dir+filename+" is blank")
					output = [image_dir+filename]
					csv_writer.writerow(output)
			except IOError:
# filename not an image	file
				print("File:	", filename, "is not an	image file")
	
	csv_file_out.close()






def	parse_args():
	"""Parses the command line	arguments.
	Returns
	args.imagedir : str
		Directory	with screenshots.
	args.out :	str
		The CSV file to write the file names of the blank images, if there are any.

	"""

	parser	= argparse.ArgumentParser()
	parser.add_argument("--imagedir", type=str, help="Directory with screenshots of the websites")
	parser.add_argument("--out", type=str,	help="The file name	to write the names of blank	files, if applicable")

	args =	parser.parse_args()

	# some	error checking
	if	args.imagedir is None:
		print("Must provide directory with screenshots")
		exit()
	if	args.out is	None:
		print("Must provide output file")
		exit()

	return	args.imagedir, args.out


def	main():
	img_dir, out_name,	= parse_args()

	print("Reading	the	input files	...")
	find_blank_images(img_dir,	out_name)



main()
