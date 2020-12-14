import numpy as np
import os
import glob
import cv2
from skimage import filters, morphology, color, measure
from scipy import ndimage
from shutil import rmtree


def rmscale(img, thresh=1):
    """
    remove the scale bar and other information from lov images
    :param img: jpeg image file
    :param thresh: pixel value to remove (1 for black txt on white background)
    :return: images w/o size info
    """
    # get connected components
    edges = cv2.Canny(img, 220, 225)
    edges = morphology.closing(edges, morphology.square(5))
    #edges = filters.scharr(img)
    #filt = filters.gaussian(img, sigma=11)
    #thresh = np.where(filt < filters.thresholding.threshold_otsu(filt), 0., 1.0)
    #thresh = morphology.dilation(thresh, morphology.square(3))
    #edges = morphology.closing(edges, morphology.square(3))
    fill = ndimage.binary_fill_holes(edges)
    #lose = morphology.erosion(fill, morphology.square(1))
    lab = morphology.label(fill, connectivity=2, background=0)

    # get the region properties for each region
    props = measure.regionprops(lab, img)
    max_coord = 0
    ind = 0

    for xx in range(0, len(props)):
        if (props[xx].centroid[0] > max_coord) and (props[xx].area > 10):
            max_coord = props[xx].centroid[0]
            ind = xx

    msk = (lab) == props[ind].label
    #msk = morphology.binary_dilation(msk, selem=morphology.square(5))
    out = np.copy(img)
    out[msk] = 255

    return out


if __name__ == '__main__':

    ptf = r"D:\LOV\all_arctic_eggs"
    outptf = r"D:\LOV\all_eggs_noscale"
    ptfs = glob.glob(os.path.join(ptf, '*.jpg'))

    if os.path.exists(outptf):
        rmtree(outptf)
        os.mkdir(outptf)

    for item in ptfs:
        im = cv2.imread(item)
        im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        #xx = rmscale(im)
        xx = im[0:-31, :]
        outname = os.path.join(outptf, os.path.basename(item))
        if os.path.exists(outname):
            os.remove(outname)
            cv2.imwrite(outname, xx)
        else:
            cv2.imwrite(outname, xx)
