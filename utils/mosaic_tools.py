import numpy as np
import pandas as pd
from psd_tools import PSDImage
import os


def read_nested_pd(pd_dict, entry):
    """
    Return a pd DataFrame from a dictionary of json seralized data
    :param pd_dict: dictionary object of json seralized DataFrames
    :param entry: name of the desired mosaic
    :return: pd DataFrame
    """

    # extract the string
    temp = pd_dict[entry]

    # make into the dataframe
    out = pd.read_json(temp)

    return out


def read_psd(ptf):
    """
    read in a psd file and strip any extra space from layer names
    :param ptf: absolute path to psd file
    :return: PSDImage object
    """
    # make sure it is a psd file
    assert os.path.splitext(ptf)[1] == '.psd', 'input not a PSD file'

    # open it
    img = PSDImage.open(ptf)

    # strip any extra characters from the layer names
    for layer in img:
        layer.name = layer.name.strip()

    return img


def layers2gray(img, layer=None):
    """
    extract and convert each layer to gray scale PIL object
    :param img: PSD image
    :param layer: list of layer names to extract [default=None to extract all visible]
    :return: list of gray scale PIL object(s)
    """

    out = []

    if not layer:
        # composite and return all the visible layers in the PSD object
        for lay in img:

            # composite channels to PIL
            temp = lay.composite()
            temp = temp.convert('L')

            out.append(temp)

    else:
        # composite and return just the layers specified in the input list
        # check that layer is indeed a list
        assert isinstance(layer, list), "make sure layer list is in fact a list"

        for lay_name in layer:
            temp = img.composite(layer_filter=lambda x: x.is_visible() and x.name == lay_name)
            temp = temp.convert('L')

            out.append(temp)

    return out


def retrieve_regions(img, dim_coords):
    """
    slice and dice a mosaic back into regions of the original size
    :param img: gray scale PIL
    :param dim_coords: pandas dictionary containing coordinates and dimensions of subregions
    :return: dictionary of subregions
    """

    # make into numpy array
    xx = np.array(img)

    # rotate back to original coordinates
    xx = np.rot90(xx)

    out = {}
    # iterate over each row of the data frame and retrieve the mask
    for idx, row in dim_coords.iterrows():
        ww = row['width']
        hh = row['height']
        coord = row['upper_left_coord']

        sub = xx[coord[0]:coord[0] + hh, coord[1]:coord[1] + ww]
        out[row['path']] = sub

    return out


def get_subregions(img, roi_dim=10):
    """
    slice and dice a mosaic into subregions of even size. assumes square mosaic (example, 10 rois x 10 rois).
    :param img: numpy array of mosaic
    :param roi_dim: number of rois per side [int]
    :return: list of numpy arrays of square dimensions
    """

    # get the dimensions of the padded rois in the current array
    mm = img.shape[0] // roi_dim
    nn = img.shape[1] // roi_dim

    # slice array accordingly (will return square subregions)
    subs = [img[x:x + mm, y:y + nn] for x in range(0, img.shape[0], mm)
            for y in range(0, img.shape[1], nn)]

    return subs

