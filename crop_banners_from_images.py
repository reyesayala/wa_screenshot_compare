from PIL import Image
import argparse
import os

'''
in order to remove banner from British Library UK OA collection, use the following dimensions
#box = (0,43,1024,768)
'''
def crop_images(input_dir, output_dir, new_dimensions):


	for file_name in os.listdir(input_dir):
		try: 
			image = Image.open(input_dir + "/" + file_name)
			box = (new_dimensions[0], new_dimensions[1], new_dimensions[2], new_dimensions[3])
			cropped_image = image.crop(box)
			cropped_image.save(output_dir + "/" + file_name)
			image.close()
		except Exception:
			pass
		
	print("All images have been succesfully cropped\n")

# for handling the command line switches
def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("--input_dir", type=str, help="directory of current screenshots with banners that need to be removed")
	parser.add_argument("--output_dir", type=str, help="directory where screenshots without the banners will be saved")
	parser.add_argument('--new_dimensions', type=str, help="dimension you wish the new screenshot to be")

	args = parser.parse_args()

	# some error checking
	if args.input_dir is None:
		print("Must provide input directory for image files\n")
		exit()
	if args.output_dir is None:
		print("Must provide output directory for image files\n")
		exit()
	if args.new_dimensions is None:
		print("Must provide new dimensions for output files\n")
		exit()

	#read the new dimensions argument as a list
	new_dimensions_list = args.new_dimensions.split(',')  # ['1','2','3','4']
	#convert all elements of list to integers
	new_dimensions_list2 = list(map(int, new_dimensions_list))


	
	return(args.input_dir, args.output_dir, new_dimensions_list2)

#python prog.py --l1=1,2,3,4
def main():

	input_dir, output_dir, new_dimensions = parse_args()
	print("Reading the input files ...")
	crop_images(input_dir, output_dir, new_dimensions)


main()
