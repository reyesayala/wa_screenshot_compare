"""
adapted from code at: http://scikit-image.org/docs/stable/auto_examples/transform/plot_ssim.html#sphx-glr-auto-examples-transform-plot-ssim-py
===========================
Structural similarity index
===========================

When comparing images, the mean squared error (MSE)--while simple to
implement--is not highly indicative of perceived similarity.  Structural
similarity aims to address this shortcoming by taking texture into account
[1]_, [2]_.

The example shows two modifications of the input image, each with the same MSE,
but with very different mean structural similarity indices.

.. [1] Zhou Wang; Bovik, A.C.; ,"Mean squared error: Love it or leave it? A new
       look at Signal Fidelity Measures," Signal Processing Magazine, IEEE,
       vol. 26, no. 1, pp. 98-117, Jan. 2009.

.. [2] Z. Wang, A. C. Bovik, H. R. Sheikh and E. P. Simoncelli, "Image quality
       assessment: From error visibility to structural similarity," IEEE
       Transactions on Image Processing, vol. 13, no. 4, pp. 600-612,
       Apr. 2004.


       python calculate_similarity.py --csv=2217/index/filenames.csv --cpics=2217/pics_current --apics=2217/pics_archive --out=2217/index/output.txt --ssim --print
"""

import numpy as np
import cv2

from skimage import img_as_float
#from skimage.measure import compare_ssim as ssim
from skimage.metrics import structural_similarity as ssim
from skimage import io
from skimage.metrics import hausdorff_distance
from skimage.metrics import normalized_root_mse
from skimage.metrics import peak_signal_noise_ratio
from skimage.metrics import mean_squared_error

from PIL import Image, ImageFile
import imagehash


ImageFile.LOAD_TRUNCATED_IMAGES = True

def cropping_images(image_filename_a, image_filename_b):
    o_width, o_height = image_filename_a.shape[:2]
    a_width, a_height = image_filename_b.shape[:2]
    f_width = min(o_width, a_width)
    f_height = min(o_height, a_height)
    image_filename_a_cropped = image_filename_a[0:f_width, 0:f_height]
    image_filename_b_cropped = image_filename_b[0:f_width, 0:f_height]

    return image_filename_a_cropped, image_filename_b_cropped


def calculate_ssim(current_image_name, archive_image_name, current_image, archive_image):
    """Calculates the structural similarity score of the two given images

    Parameters
    ----------
    current_image_name : str
        The current website screenshot file path.
    archive_image_name : str
        The archive website screenshot file path.

    Returns
    -------
    ssim_noise : float
        The ssim score.

    References
    ----------
    .. [1] http://scikit-image.org/docs/stable/auto_examples/transform/plot_ssim.html#
            sphx-glr-auto-examples-transform-plot-ssim-py

    """
    #checks if images are same size (shape for ndarrays)
    if(current_image.shape == archive_image.shape):
        #current_image_float = img_as_float(current_image)
        #archive_image_float = img_as_float(archive_image)
        #datarange = archive_image_float.max() - archive_image_float.min()
        ssim_score = ssim(current_image, archive_image, channel_axis = -1)
    
    else: 
    
        (current_image_cropped, archive_image_cropped) = cropping_images(current_image, archive_image)
        #current_image_float = img_as_float(current_image_cropped)
        #archive_image_float = img_as_float(archive_image_cropped)
        #datarange = archive_image_float.max() - archive_image_float.min()
        #print("Current_image size: ", current_image_cropped.size, "Shape: ", current_image.shape, "Data type: ", current_image.dtype)
        ssim_score = ssim(current_image_cropped, archive_image_cropped, channel_axis = -1)
    
    return ssim_score

def calculate_psnr(current_image, archive_image):
    """Calculates the peak signal to noise ratio (PSNR) of the two given images

    Parameters
    ----------
    current_image_name : str
        The current website screenshot file path.
    archive_image_name : str
        The archive website screenshot file path.
    current_image: ndarray
        A matrix representing the image
    archive_image: ndarray
        A matrix representing the image

    Returns
    -------
    nrootmse : float
        The normalized root mean squared error value.

    References
    ----------
    .. [1]  https://scikit-image.org/docs/stable/api/skimage.metrics.html#skimage.metrics.normalized_root_mse
    
       [2]  https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=8d8fd7f146ff6020b80c8758a413c40d9854b0d6
       
       [3]  https://www.scirp.org/journal/paperinformation?paperid=90911

    """
    if(current_image.shape == archive_image.shape):
        psnr = peak_signal_noise_ratio(current_image, archive_image)
    else:
        (current_image_cropped, archive_image_cropped) = cropping_images(current_image, archive_image)
        psnr = peak_signal_noise_ratio(current_image_cropped, archive_image_cropped)


    return psnr

def calculate_nrmse(current_image, archive_image):

    """Calculates the normalized root of the mean square error of the two given images

    Parameters
    ----------
    current_image_name : str
        The current website screenshot file path.
    archive_image_name : str
        The archive website screenshot file path.
    current_image: ndarray
        A matrix representing the image
    archive_image: ndarray
        A matrix representing the image

    Returns
    -------
    nrootmse : float
        The normalized root mean squared error value.

    References
    ----------
    .. [1]  https://scikit-image.org/docs/stable/api/skimage.metrics.html#skimage.metrics.normalized_root_mse
    
       [2]  https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=8d8fd7f146ff6020b80c8758a413c40d9854b0d6
       
       [3]  https://www.scirp.org/journal/paperinformation?paperid=90911

    """
    
    if(current_image.shape == archive_image.shape):
        nrootmse = normalized_root_mse(current_image, archive_image)
    else:
        (current_image_cropped, archive_image_cropped) = cropping_images(current_image, archive_image)
        nrootmse = normalized_root_mse(current_image_cropped, archive_image_cropped)


    #print("NRMSE : ", nrootmse)
    return nrootmse

def calculate_mse(current_image_name, archive_image_name, current_image, archive_image):
    """Calculates the mean square error of the two given images

    Parameters
    ----------
    current_image_name : str
        The current website screenshot file path.
    archive_image_name : str
        The archive website screenshot file path.

    Returns
    -------
    mse_noise : float
        The mean squared error value.

    References
    ----------
    .. [1]  https://www.pyimagesearch.com/2014/09/15/python-compare-two-images/

    """



    # current_image_float = img_as_float(current_image)
    # archive_image_float = img_as_float(archive_image)
    # mse_noise = np.linalg.norm(current_image_float - archive_image_float)
    
    if(current_image.shape == archive_image.shape):
        mse = mean_squared_error(current_image, archive_image)
    else: 
        (current_image_cropped, archive_image_cropped) = cropping_images(current_image, archive_image)
        mse = mean_squared_error(current_image_cropped, archive_image_cropped)
    
    return mse


def calculate_percent(current_image_name, archive_image_name, current_image, archive_image):
    """Calculates the percentage similarity score of the two given images

    Parameters
    ----------
    current_image_name : str
        The current website screenshot file path.
    archive_image_name : str
        The archive website screenshot file path.

    Returns
    -------
    percent_score : float
        The percentage similarity score.

    References
    ----------
    .. [1] https://rosettacode.org/wiki/Percentage_difference_between_images#Python

    """

    (current_image_cropped, archive_image_cropped) = cropping_images(current_image, archive_image)
    current_image = cv2.cvtColor(current_image_cropped, cv2.COLOR_BGR2RGB)
    current_image = Image.fromarray(current_image)
    archive_image = cv2.cvtColor(archive_image_cropped, cv2.COLOR_BGR2RGB)
    archive_image = Image.fromarray(archive_image)
    assert current_image.mode == archive_image.mode, "Different kinds of images."
    assert current_image.size == archive_image.size, "Different sizes."

    pairs = zip(current_image.getdata(), archive_image.getdata())
    if len(current_image.getbands()) == 1:
        # for gray-scale jpegs
        dif = sum(abs(p1 - p2) for p1, p2 in pairs)
    else:
        dif = sum(abs(c1 - c2) for p1, p2 in pairs for c1, c2 in zip(p1, p2))

    ncomponents = current_image.size[0] * current_image.size[1] * 3

    percent_score = 100 - ((dif / 255.0 * 100) / ncomponents)    # convert to percentage match
    
    #print("Percentage similarity: ", percent_score)

    return percent_score



def calculate_phash(current_image_name, archive_image_name):
    """Calculates the phash score of the two given images

    Parameters
    ----------
    current_image_name : str
        The current website screenshot file path.
    archive_image_name : str
        The archive website screenshot file path.

    Returns
    -------
    phash_score : float
        The phash score.

    References
    ----------
    .. [1] https://rosettacode.org/wiki/Percentage_difference_between_images#Python

    """
    current_image = Image.open(current_image_name)
    archive_image = Image.open(archive_image_name)
    cur_hash = imagehash.phash(current_image)
    archive_hash = imagehash.phash(archive_image)
    phash_score = cur_hash - archive_hash
    return phash_score
    
def calculate_hausdorff(current_image_name, archive_image_name, current_image, archive_image):
    """Calculates the Hausdorff distance of the two given images
    
    References
    ----------
    ..[1] https://scikit-image.org/docs/stable/api/skimage.metrics.html#skimage.metrics.hausdorff_distance
    
    """
    hausdorff = hausdorff_distance(current_image, archive_image)
    return hausdorff
    
