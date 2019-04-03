import argparse
import csv

import similarity_measures


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


def find_scores(image_dict, url_name_dict, ssim_flag, mse_flag, vec_flag, csv_out_name, do_print):
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
    csv_out_name : str
        The output CSV file name.
    do_print : bool
        If True then the urls and file names and scores will be printed to stdout.

    """

    with open(csv_out_name, 'w+') as csv_file_out:
        csv_writer = csv.writer(csv_file_out, delimiter=',', quoting=csv.QUOTE_ALL)

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
                    output.append("%.2f" % ssim_score)   # truncate to 2 decimal places
                if mse_flag:
                    mse_score = similarity_measures.calculate_mse(current_image_name, archive_image_name)
                    output.append("%.2f" % mse_score)
                if vec_flag:
                    vec_score = similarity_measures.calculate_vec(current_image_name, archive_image_name)
                    output.append("%.2f" % vec_score)

                csv_writer.writerow(output)

                if do_print:
                    print("{0}, {1}".format(output[2], output[3]), end='')
                    if ssim_flag:
                        print(", %.2f" % ssim_score, end='')
                    if mse_flag:
                        print(", %.2f" % mse_score, end='')
                    if vec_flag:
                        print(", %.2f" % vec_score, end='')
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
    args.vec : bool
        Whether or not to compute the vector comparison score.
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
    parser.add_argument('--vec', action='store_true', help="(optional) Include to calculate vector comparison score")
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
    if args.ssim is False and args.mse is False and args.vec is False:
        print("Must specify which scores you want to be calculated. Aborting...")
        exit()

    return args.csv, args.currdir, args.archdir, args.ssim, args.mse, args.vec, args.out, args.print


def main():
    csv_in_name, curr_img_dir, arch_img_dir, ssim_flag, mse_flag, vec_flag, csv_out_name, do_print = parse_args()

    print("Reading the input files ...")
    image_dict, url_name_dict = read_input_file(csv_in_name, curr_img_dir, arch_img_dir)

    find_scores(image_dict, url_name_dict, ssim_flag, mse_flag, vec_flag, csv_out_name, do_print)


main()
