import argparse
import csv
import importlib
from PIL import Image
from PIL import ImageChops
import os
from skimage import io
import time


def read_input_file(csv_in_name, curr_img_dir, arch_img_dir):
    """Opens up the given CSV file and parses the file names and urls.

    Parameters
    ----------
    csv_in_name : str
        The input CSV file name.
    curr_img_dir : str
        The directory that contains the current website images.
    arch_img_dir : str
        The directory that contains the archive website images.

    Returns
    -------
    image_name_dict : dict
        A dictionary where the current screenshot file name references a list of the archive screenshot file names.
        ie: {"current.image.png" : ["archive.image.1.png", "archive.image.2.png"]}
    url_name_dict : dict
        A dictionary where url references its respective screenshot file names.
        ie: {"http://example.site.1.com" : "example.image.1.png", "http://example.site.2.com" : "example.image.2.png"}

    Notes
    -----
    Assumes that the input CSV file has rows in the following order:
        current URL, archive URL, current image name, archive image names

    """

    print("File name: ", csv_in_name)
    image_name_dict = {}
    url_name_dict = {}

    with open(csv_in_name, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        line_count = 0
        compare_name = ''

        for row in csv_reader:
            line_count += 1
            if line_count == 1:     # skip the first row in csv because it's the header
                continue
            current_image_path = "{0}/{1}".format(curr_img_dir, row[2])
            archive_image_path = "{0}/{1}".format(arch_img_dir, row[3])
            current_url = row[0]
            archive_url = row[1]
            url_name_dict[current_image_path] = current_url
            url_name_dict[archive_image_path] = archive_url

            if compare_name != current_image_path:
                compare_name = current_image_path
                image_name_dict[current_image_path] = [archive_image_path]
            elif compare_name == current_image_path:
                image_name_dict[current_image_path].append(archive_image_path)

        print('Processed ', line_count, ' image pairings.')

    return image_name_dict, url_name_dict

def image_is_black(image_file):
    if  not image_file.getbbox():
        print("Image   is completely black")
        return(True)
    else:
        return(False)
        
def image_is_white(image_file):
    if  not ImageChops.invert(image_file).getbbox():
        print("Image   is completely white")
        return(True)
    else:
        return(False)

#from https://stackoverflow.com/questions/14041562/python-pil-detect-if-an-image-is-completely-black-or-white
#the approach involving getbbox is faulty
def is_monochromatic_image(img):
    extr = img.getextrema()
    a = 0
    for i in extr:
        if isinstance(i, tuple):
            a += abs(i[0] - i[1])
        else:
            a = abs(extr[0] - extr[1])
            break
    return a == 0


def open_images(current_image_name, archive_image_name):
    current_image = io.imread(current_image_name)
    archive_image = io.imread(archive_image_name)
    return current_image, archive_image


def find_scores(image_dict, url_name_dict, ssim_flag, mse_flag, hausdorff_flag, phash_flag, percent_flag, nrmse_flag, psnr_flag, csv_out_name, blank_csv_name, do_print):
    """Calculates the image similarity scores of the given images

    Parameters
    ----------
    image_dict : dict
        A dictionary where the current screenshot file name references a list of the archive screenshot file names.
        ie: {"current.image.png" : ["archive.image.1.png", "archive.image.2.png"]}
    url_name_dict : dict
        A dictionary where url references its respective screenshot file names.
        ie: {"http://example.site.1.com" : "example.image.1.png", "http://example.site.2.com" : "example.image.2.png"}
    ssim_flag : bool
        If True then the structural similarity score will be calculated.
    mse_flag : bool
        If True then the mean squared error will be calculated.
    percent_flag :bool
        If True then then percentage similarity score will be calculated.
    csv_out_name : str
        The output CSV file name.
    do_print : bool
        If True then the urls and file names and scores will be printed to stdout.

    """
    similarity_measures = importlib.import_module("similarity_measures")

    with open(csv_out_name, 'w+') as csv_file_out, open(blank_csv_name, 'w+') as blank_file_out:
        csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)
        blank_csv_writer = csv.writer(blank_file_out, delimiter=',', quoting=csv.QUOTE_ALL)

        header = ["current_url", "archive_url", "current_file_name", "archive_file_name"]
        if ssim_flag:
            header.append("ssim_score")
        if mse_flag:
            header.append("mse_score")
        if percent_flag:
            header.append("percent_score")
        if phash_flag:
            header.append("phash_score")
        if hausdorff_flag:
            header.append("hausdorff_score")
        if nrmse_flag:
            header.append("nrmse_score")
        if psnr_flag:
            header.append("psnr_score")
        csv_writer.writerow(header)

        blank_header = ["blank_image_file_name"]
        blank_csv_writer.writerow(blank_header)


        for current_image_name, archive_image_list in image_dict.items():
            for archive_image_name in archive_image_list:
                output = [url_name_dict[current_image_name], url_name_dict[archive_image_name],
                          current_image_name, archive_image_name]

                is_valid = True;

                image_name_pair = [current_image_name, archive_image_name];

                for image_name in image_name_pair :
                    try:
                        print(current_image_name, archive_image_name)
                        im =    Image.open(image_name)
                        if(is_monochromatic_image(im)):
                            print("Image: ", image_name+" is blank")
                            csv_output = [image_name];
                            blank_csv_writer.writerow(csv_output);
                            is_valid = False;
                    except FileNotFoundError as e:
                        is_valid = False;
                        print("File not found", image_name);
                    except IOError as e:
                        
                        # filename not an image file
                        print(e);
                        print("File:    ", image_name, "is not an   image file")
                        is_valid = False;
                    except:
                        print("Unknown error")
                        is_valid = False;



                if is_valid:
                    
                    result = open_images(current_image_name, archive_image_name)
                    current_image = result[0]
                    archive_image = result[1]
                    print("Results: ")
                    
                    
                    if ssim_flag:
                        ssim_score = similarity_measures.calculate_ssim(current_image_name, archive_image_name, current_image, archive_image)
                        if ssim_score is None:
                            continue
                        else: 
                            output.append("%.2f" % ssim_score)   # truncate to 2 decimal places
                    if mse_flag:
                        mse_score = similarity_measures.calculate_mse(current_image_name, archive_image_name, current_image, archive_image)
                        output.append("%.2f" % mse_score)
                    if percent_flag:
                        percent_score = similarity_measures.calculate_percent(current_image_name, archive_image_name, current_image, archive_image)
                        output.append("%.2f" % percent_score)
                    if phash_flag:
                        phash_score = similarity_measures.calculate_phash(current_image_name, archive_image_name)
                        output.append("%.2f" % phash_score)
                    if hausdorff_flag:
                        hausdorff_score = similarity_measures.calculate_hausdorff(current_image_name, archive_image_name, current_image, archive_image)
                        output.append("%.2f" % hausdorff_score)
                    if nrmse_flag:
                        nrmse_score = similarity_measures.calculate_nrmse(current_image, archive_image)
                        output.append("%.2f" % nrmse_score)
                    if psnr_flag:
                        psnr_score = similarity_measures.calculate_psnr(current_image, archive_image)
                        output.append("%.2f" % psnr_score)
                    csv_writer.writerow(output)

                    if do_print:
                        print("{0}, {1}".format(output[2], output[3]), end='')
                        if ssim_flag:
                            print(", %.2f" % ssim_score, end='')
                        if mse_flag:
                            print(", %.2f" % mse_score, end='')
                        if percent_flag:
                            print(", %.2f" % percent_score, end='')
                        if phash_flag:
                            print(", %.2f" % phash_score, end='')
                        if hausdorff_flag:
                            print(", %.2f" % hausdorff_score, end='')
                        if nrmse_flag:
                            print(", %.2f" % nrmse_score, end='')
                        if psnr_flag:
                            print(", %.2f" % psnr_score, end='')
                        print('\n', end='')


def parse_args():
    """Parses the command line arguments.

    Returns
    -------
    args.csv : str
        The CSV file with screenshot file names.
    args.currdir : str
        Directory with screenshots of the current websites.
    args.archdir : str
        Directory with screenshots of the archive websites.
    args.out : str
        The CSV file to write the results of the comparisons.
    args.ssim : bool
        Whether or not to compute the structural similarity score.
    args.mse : bool
        Whether or not to compute the mean squared error.
    args.percent: bool
        Whether or not to compute the percentage similarity
    args.hausdorff: bool
        Whether or not to compute the Hausdorff distance
    args.print : bool
        Whether or not to print the result to stdout.

    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, help="The CSV file with screenshot file names")
    parser.add_argument("--currdir", type=str, help="Directory with screenshots of the current websites")
    parser.add_argument("--archdir", type=str, help="Directory with screenshots of the archive websites")
    parser.add_argument("--out", type=str, help="The CSV file to write the results of the comparisons")
    parser.add_argument('--ssim', action='store_true', help="(optional) Include to calculate structural similarity")
    parser.add_argument('--mse', action='store_true', help="(optional) Include to calculate mean square error")
    parser.add_argument('--hausdorff', action ='store_true', help="(optional) Include to calculate hausdorff_distance")
    parser.add_argument('--phash', action ='store_true', help="(optional) Include to calculate perceptual hash")
    parser.add_argument('--percent', action='store_true', help="(optional) Include to calculate percentage similarity")
    parser.add_argument('--nrmse', action='store_true', help="(optional) Include to normalized root mean square error")
    parser.add_argument('--psnr', action='store_true', help="(optional) Include to calculate peak signal to noise ratio")
    parser.add_argument('--print', action='store_true', help="(optional) Include to print results to stdout")

    args = parser.parse_args()

    # some error checking
    if args.currdir is None or args.archdir is None:
        print("Must provide directory with current and archive screenshots")
        exit()
    if args.csv is None:
        print("Must provide input file")
        exit()
    if args.out is None:
        print("Must provide output file")
        exit()
    if args.ssim is False and args.mse is False and args.percent is False and args.phash is False and args.hausdorff is False:
        print("Must specify which scores you want to be calculated. Aborting...")
        exit()

    return args.csv, args.currdir, args.archdir, args.ssim, args.mse, args.hausdorff, args.phash, args.percent, args.out, args.print


def main():
    # csv_in_name, curr_img_dir, arch_img_dir, ssim_flag, mse_flag, percent_flag, hausdorff_flag, phash_flag, csv_out_name, do_print = parse_args()
    import read_config_file
    import config
    import time
    
    #begin timer
    start = time.time()
    print("Starting the calculations")
    print("Reading the input files ...")
    image_dict, url_name_dict = read_input_file(config.file_names_csv, config.current_pics_dir, config.archive_pics_dir)

    find_scores(image_dict, url_name_dict, config.ssim, config.mse, config.hausdorff, config.phash, config.percent, config.nrmse, config.psnr, config.scores_file_csv, config.blank_file_csv, config.print)
    print("Finished calculating similarity scores")
    end = time.time()
    print("Elapsed time in seconds: ", end - start)


main()
