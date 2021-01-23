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
            temp = temp.covert('LA')

            out.append(temp)

    else:
        # composite and return just the layers specified in the input list
        for lay_name in layer:
            temp = img.composite(layer_filter=lambda x: x.is_visible() and x.name == lay_name)
            temp = temp.convert('LA')

            out.append(temp)

    return out


def retrieve_regions(img, dim_coords):
    """
    slice and dice a mosaic back into regions of the original size
    :param img: gray scale PIL or numpy array
    :param dim_coords: pandas dictionary containing coordinates and dimensions of subregions
    :return: dictionary of subregions
    """

    #TODO Iterate over each ROI and snip out according to coordinates and dimensions