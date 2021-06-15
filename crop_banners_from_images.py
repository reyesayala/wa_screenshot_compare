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


#python prog.py --l1=1,2,3,4
def main():

	# input_dir, output_dir, new_dimensions = parse_args()
    import read_config_file
    import config
    print("Reading the input files ...")
    crop_images(config.pics_archived_banners_dir, config.pics_archived_no_banners_dir, [config.dim_left, config.dim_top, config.dim_right, config.dim_bottom])


main()
