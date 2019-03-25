# this program gets the list of current URLs and then creates a list of corresponding archived screenshots

import argparse
import csv

import similarity_measures


# create dict with the current image as key and a list of archive images as value
# from the input csv file
def read_input_file(input_csv, current_images_dir, archive_images_dir):
    """Opens up the given CSV file and parses the file names and urls.

    Parameters
    ----------
    input_csv : string
        The input CSV file name that contains the urls and file names.
    current_images_dir : string
        The directory that contains the current website images.
    archive_images_dir : string
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

    print("File name: ", input_csv)
    image_name_dict = {}
    url_name_dict = {}

    with open(input_csv, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        line_count = 0
        compare_name = ''

        for row in csv_reader:
            line_count += 1
            if line_count == 1:     # skip the first row in csv because it's the header
                continue
            current_image_path = "{0}/{1}".format(current_images_dir, row[2])
            archive_image_path = "{0}/{1}".format(archive_images_dir, row[3])
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


def find_scores(image_dict, url_name_dict, ssim_flag, mse_flag, vec_flag, out_file_name, do_print):
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
    vec_flag :bool
        If True then the vector comparison score will be calculated.
    out_file_name : string
        The output CSV file name to write the results to.
    do_print : bool
        If True then the urls and file names and scores will be printed to stdout.

    """

    with open(out_file_name, 'w+') as out_file:
        csv_writer = csv.writer(out_file, delimiter=',', quoting=csv.QUOTE_ALL)

        header = ["current_url", "archive_url", "current_file_name", "archive_file_name"]
        if ssim_flag:
            header.append("ssim_score")
        if mse_flag:
            header.append("mse_score")
        if vec_flag:
            header.append("vector_score")
        csv_writer.writerow(header)

        for current_image_name, archive_image_list in image_dict.items():
            for archive_image_name in archive_image_list:
                output = [url_name_dict[current_image_name], url_name_dict[archive_image_name],
                          current_image_name, archive_image_name]

                if ssim_flag:
                    ssim_score = similarity_measures.calculate_ssim(current_image_name, archive_image_name)
                    output.append(str(ssim_score))
                if mse_flag:
                    mse_score = similarity_measures.calculate_mse(current_image_name, archive_image_name)
                    output.append(str(mse_score))
                if vec_flag:
                    vec_score = similarity_measures.calculate_vec(current_image_name, archive_image_name)
                    output.append(str(vec_score))

                csv_writer.writerow(output)

                if do_print:
                    # print("{0}, {1}, {2}, {3}".format(output[2], ssim_score, mse_score, vec_score))

                    # print("{0}, {1}, {2}, {3} ".format(output[0], output[0], output[0], output[0]), end='')
                    # if ssim_flag:
                    #     print("{}, ".format(ssim_score))
                    # if mse_flag:
                    #     print("{}, ".format(mse_score))
                    # if vec_flag:
                    #     print("{}, ".format(vec_score))
                    # todo
                    pass


# for handling the command line switches
def parse_args():
    """Parses the arguments passed in from the command line"""

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, help="CSV file with screenshot file names")
    parser.add_argument("--currdir", type=str, help="directory with screenshots of the current websites")
    parser.add_argument("--archdir", type=str, help="directory with screenshots of the archive websites")
    parser.add_argument('--ssim', action='store_true', help="include to calculate structural similarity")
    parser.add_argument('--mse', action='store_true', help="include to calculate mean square error")
    parser.add_argument('--vec', action='store_true', help="include to calculate vector comparison score")
    parser.add_argument("--out", type=str, help="output csv file to write the results of the comparisons")
    parser.add_argument('--print', action='store_true', help="include to print results of stdout")

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
    if args.ssim is False and args.mse is False and args.vec is False:
        print("Must specify which scores you want to be calculated. Aborting...")
        exit()

    return args.csv, args.currdir, args.archdir, args.ssim, args.mse, args.vec, args.out, args.print


def main():
    input_csv, current_images_dir, archive_images_dir, ssim_flag, mse_flag, vec_flag, out_file, do_print = parse_args()

    print("Reading the input files ...")
    image_dict, url_name_dict = read_input_file(input_csv, current_images_dir, archive_images_dir)

    find_scores(image_dict, url_name_dict, ssim_flag, mse_flag, vec_flag, out_file, do_print)


main()
