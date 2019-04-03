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

from skimage import img_as_float
from skimage.measure import compare_ssim as ssim
from skimage import io

from PIL import Image


def calculate_ssim(current_image_name, archive_image_name):
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

    current_image = io.imread(current_image_name)
    current_image_float = img_as_float(current_image)

    archive_image = io.imread(archive_image_name)
    archive_image_float = img_as_float(archive_image)

    datarange = archive_image_float.max() - archive_image_float.min()
    ssim_noise = ssim(current_image_float, archive_image_float, multichannel=True, data_range=datarange)

    return ssim_noise


def calculate_mse(current_image_name, archive_image_name):
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

    current_image = io.imread(current_image_name)
    archive_image = io.imread(archive_image_name)

    # current_image_float = img_as_float(current_image)
    # archive_image_float = img_as_float(archive_image)
    # mse_noise = np.linalg.norm(current_image_float - archive_image_float)

    mse_noise = np.sum((current_image.astype("float") - archive_image.astype("float")) ** 2)
    mse_noise /= float(current_image.shape[0] * current_image.shape[1])

    return mse_noise


# source: https://rosettacode.org/wiki/Percentage_difference_between_images#Python
def calculate_vec(current_image_name, archive_image_name):
    """Calculates the vector difference score of the two given images

    Parameters
    ----------
    current_image_name : str
        The current website screenshot file path.
    archive_image_name : str
        The archive website screenshot file path.

    Returns
    -------
    vec_score : float
        The vector difference score.

    References
    ----------
    .. [1] https://rosettacode.org/wiki/Percentage_difference_between_images#Python

    """
    current_image = Image.open(current_image_name)
    archive_image = Image.open(archive_image_name)
    assert current_image.mode == archive_image.mode, "Different kinds of images."
    assert current_image.size == archive_image.size, "Different sizes."

    pairs = zip(current_image.getdata(), archive_image.getdata())
    if len(current_image.getbands()) == 1:
        # for gray-scale jpegs
        dif = sum(abs(p1 - p2) for p1, p2 in pairs)
    else:
        dif = sum(abs(c1 - c2) for p1, p2 in pairs for c1, c2 in zip(p1, p2))

    ncomponents = current_image.size[0] * current_image.size[1] * 3

    vec_score = 100 - ((dif / 255.0 * 100) / ncomponents)    # convert to percentage match

    return vec_score
