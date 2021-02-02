import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import glob
import sys
import argparse
from utils.mosaic_tools import read_psd, read_nested_pd, layers2gray, retrieve_regions
from utils.img_proc import thresh, fill_gap, big_region


def str2bool(v):
    """
    returns a boolean from argparse input
    """

    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected')


if __name__ == '__main__':

    # define parser
    parser = argparse.ArgumentParser(description='Unpack annotated mosaics saved as PSD files')

    parser.add_argument('path_to_mos', metavar='path_to_mos', help='Absolute path to directory of mosaics')
    parser.add_argument('path_to_coords', metavar='path_to_coords', help='Path to coordinate file or image list')
    parser.add_argument('output_path', metavar='output_path', help='Where to save the output mosaics')
    parser.add_argument('--make_voc', metavar='make_voc',
                        default=False, help='Indicate whether voc format is needed [bool]')
    parser.add_argument('--file_type', metavar='file_type',
                        default='jpg', choices=['jpg', 'png', 'tiff'], help='type of file to look for')

    args = parser.parse_args()

    path_to_mos = args.path_to_mos
    path_to_coords = args.path_to_coords
    file_type = args.file_type
    output_path = args.output_path
    make_voc = str2bool(args.make_voc)

    # if only processing one mosaic, put it into a dummy list for subsequent loops
    if os.path.isfile(path_to_mos):
        moz = [path_to_mos]
    elif os.path.isdir(path_to_mos):
        moz = glob.glob(os.path.join(path_to_mos, '*.psd'))
    else:
        sys.exit('Check that mosaic input is either path to PSD file or directory containing PSD files')

    if os.path.isfile(path_to_coords):

        assert os.path.splitext(path_to_coords)[1] == '.json', 'Coordinate file must be json document'

        with open(path_to_coords, 'r') as ff:
            all_coords = json.load(ff)
            ff.close()

        moz = glob.glob(os.path.join('/Users/eorenstein/Documents/eggs-data/Eggs copepods', '*.psd'))

        # select just the last mosaic for now
        mos = [line for line in moz if '19' in os.path.basename(line)]
        mos = mos[0]

        # open the correct dictionary
        coords = read_nested_pd(all_coords, 'mos_19')

        psd = read_psd(mos)
        lays = layers2gray(read_psd(mos))  # this grabs both the mask and the original mosaic
        #img = layers2gray(read_psd(mos), layer='Layer 002')  # this just grabs the mask

        # show the original mosaics
        orig = lays[0]
        mask = lays[1]

# display the original annotated mosaic
fig, ax = plt.subplots()
ax.imshow(np.rot90(psd.numpy())[0:1500, 0::])
ax.set_xticks([])
ax.set_yticks([])
ax.set_title('Mosaic annotated by Louis')

# cut out the subregions using original coordinates and ROI dimensions.
orig_rois = retrieve_regions(orig, coords)
mask_rois = retrieve_regions(mask, coords)

# process the psd file too for display purposes
psd_rois = retrieve_regions(psd.numpy(), coords)

# just work on biggest subregion for now
psd_big = psd_rois['D:\\LOV\\all_eggs_noscale\\62057085.jpg']
cope = orig_rois['D:\\LOV\\all_eggs_noscale\\62057085.jpg']
egg_mask = mask_rois['D:\\LOV\\all_eggs_noscale\\62057085.jpg']

# make pixel mask, again working on biggest region
tmp = fill_gap(thresh(cope))
cope_msk = big_region(tmp)

# binarize the egg mask
egg_msk = egg_mask.astype(np.float32) / 255
egg_msk = 1 - egg_msk  # invert

# ratio of egg pixels to copepod pixels
ovig_pct = np.sum(egg_msk)/np.sum(cope_msk.astype(np.float32)-egg_msk)

# add the masks together. now 0==background, 1==copepod, 2==eggs
msk = cope_msk + egg_msk

# display the biggest copepod and associated mask
fig1, ax1 = plt.subplots(2, 2)

ax1[0,0].imshow(psd_big)
ax1[0,0].set_xticks([])
ax1[0,0].set_yticks([])
ax1[0,0].set_title('ROI w/ mask')

ax1[0,1].imshow(cope, cmap='gray')
ax1[0,1].set_xticks([])
ax1[0,1].set_yticks([])
ax1[0,1].set_title('ROI')

ax1[1,0].imshow(egg_mask, cmap='gray')
ax1[1,0].set_xticks([])
ax1[1,0].set_yticks([])
ax1[1,0].set_title('eggs via manual seg')

ax1[1,1].imshow(msk, cmap='gray')
ax1[1,1].set_xticks([])
ax1[1,1].set_yticks([])
ax1[1,1].set_title('auto cope + eggs')
