import numpy as np
from skimage import morphology, measure


def thresh(img, threshold=245):
    """
    Naively thresholds an image based on uint8 pixel value
    Assume white background
    :param img: nparray
    :param threshold: int [0,255]
    :return: binary mask
    """
    mask = np.zeros(img.shape)
    mask[img < threshold] = 1

    return mask


def fill_gap(bn_img, struct='disk', dim=3):
    """
    fill holes in binary mask
    :param bn_img: binary mask [np.array]
    :param struct: structuring element to use ['disk', 'diamond', 'square']
    :param dim: size of structuring element [int]
    :return out: filled mask [np.array]
    """
    # set element
    if struct == 'disk':
        elm = morphology.disk(dim)
    elif struct =='square':
        elm = morphology.square(dim)
    elif struct == 'diamond':
        elm = morphology.diamond(dim)

    # assume same structuring element for both closing stages
    out = morphology.binary_dilation(bn_img, elm)
    out = morphology.binary_erosion(out, elm)

    return out


def big_region(bn_img, conn=2, bg=0):
    """
    return a binary mask with only the biggest subregion
    :param bn_img: binary mask [np.array]
    :param conn: how to establish connectivity. [1==cross, 2==box]
    :param bg: pixel value to consider as background
    :return out: mask with original dims and just one region
    """

    # label connected components
    lab = morphology.label(bn_img, connectivity=conn, background=bg)

    # measure the area of each region
    props = measure.regionprops_table(lab, properties=['area', 'label'])

    # get the index of the largest
    ind = np.argmax(props['area'])

    # select the biggest region
    out = lab == props['label'][ind]

    return out.astype(np.int)

