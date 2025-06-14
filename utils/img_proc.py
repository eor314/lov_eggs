import numpy as np
import cv2
from PIL import Image
from skimage import morphology, measure


def read_crop_image(img, has_scalebar=False):
    """
    read an image, crop pixels at the bottom and possibly crop to center on the object
    :param img: absolute path to image [str]
    :param has_scalebar: number of pixels to crop at the bottom [int]
    :return: the image, cropped
    """
    im = cv2.imread(img, 0)

    # crop bottom
    if has_scalebar:
        h = im.shape[0]
        im = im[0:(h-31),:]

    # NB: this seems dangerous since the background is not pure white on UVP images
    # # center on object
    # im = 255 - im
    # sum_col = np.sum(im, 0)
    # sum_row = np.sum(im, 1)
    #
    # obj_col = np.where(sum_col > 100)
    # min_col = np.min(obj_col)
    # max_col = np.max(obj_col)
    #
    # obj_row = np.where(sum_row > 100)
    # min_row = np.min(obj_row)
    # max_row = np.max(obj_row)
    #
    # im = im[min_row:max_row,min_col:max_col]
    # im = 255 - im
    #
    # cv2.imshow('image',im)
    # cv2.waitKey(0)

    return im


def get_dim(img, has_scalebar=False):
    """
    return biggest of image dimensions
    :param img: absolute path to image [str]
    :return: max(width, height) [int]
    """
    im = read_crop_image(img, has_scalebar=has_scalebar)
    hgt, wid = im.shape
    return [wid, hgt]


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


def big_region(bn_img, conn=2, bg=0, pad=0):
    """
    return a binary mask with only the biggest subregion
    :param bn_img: binary mask [np.array]
    :param conn: how to establish connectivity. [1==cross, 2==box]
    :param bg: pixel value to consider as background
    :param pad: pixel value to pad bounding box. if zero, assume box not needed
    :return out_mask: mask with original dims and just one region
    :return out_bbox: bounding box coordinates of upper left and lower right corners
    """

    # label connected components
    lab = morphology.label(bn_img, connectivity=conn, background=bg)

    # measure the area of each region
    props = measure.regionprops(lab)

    # get the index of the largest
    ars = [item.area for item in props]
    ind = np.argmax(ars)

    # select the biggest region
    out_mask = lab == props[ind].label

    # get the bounding box
    if pad != 0:
        out_bbox = props[ind].bbox
        out_bbox = np.asarray(out_bbox) + np.array([-pad, -pad, pad, pad])

        return out_mask.astype(np.int), out_bbox
    else:
        return out_mask.astype(np.int)


def pad_img(img, new_dim):
    """
    create a padded square image with original in center
    :param img: image as ndarray [uint8]
    :param new_dim: new dimension for padding [int]
    :return out: padded image [uint8]
    :return offset: offset in x and y [tuple]
    """
    ht, wd = img.shape

    # create new image of desired size and color (blue) for padding
    out = np.full((new_dim, new_dim), 255, dtype=np.uint8)

    # compute center offset
    xx = (new_dim - wd) // 2
    yy = (new_dim - ht) // 2

    # copy img image into center of result image
    out[yy:yy+ht, xx:xx+wd] = img

    return out, (yy, xx)


def tile_images(images, tile_dim, resize=128, has_scalebar=False):
    """
    takes a list of images, pads, tiles and retains coords of each
    :param images: input list of image paths
    :param tile_dim: number to tile in each dimension as int
    :param resize: size to resize the input images
    :return out: mosaic array
    :return out_coords: list of coordinates of upper left corner of each ROI
    """

    # make empty array of white background
    out = np.ones((resize*tile_dim, resize*tile_dim))*255
    out = out.astype(np.uint8)
    out_coords = []

    # tiles image across the rows
    for idx, img in enumerate(images):
        ii = idx % tile_dim
        jj = idx // tile_dim

        # read gray scale image
        im_in = read_crop_image(img, has_scalebar=has_scalebar)
        pd_im, offset = pad_img(im_in, resize)

        out[jj*resize:jj*resize+resize, ii*resize:ii*resize+resize] = pd_im

        # save the coordinates where the original ROI lives [yy, xx]
        out_coords.append([jj*resize+offset[0], ii*resize+offset[1]])

    return out, out_coords

