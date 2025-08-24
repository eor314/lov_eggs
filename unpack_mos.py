import numpy as np
import json
import os
import glob
import sys
import re
import argparse
from cv2 import imwrite
from skimage.color import label2rgb
from utils.mosaic_tools import read_psd, read_nested_pd, layers2gray, retrieve_regions, get_subregions
from utils.img_proc import thresh, fill_gap, big_region, get_dim
from utils.xml_ops import populate_voc


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

    parser.add_argument('path_to_mos', metavar='path_to_mos', help='Absolute path to mosaic or directory of mosaics')
    parser.add_argument('path_to_coords', metavar='path_to_coords', help='Path to coordinate file or image list')
    parser.add_argument('output_path', metavar='output_path', help='Where to save the output masks')
    parser.add_argument('--make_voc', metavar='make_voc',
                        default=True, help='Indicate whether voc xml files is needed [bool]')
    parser.add_argument('--annotation_template', metavar='annotation_template',
                        default='lov_voc_template.xml', help='Location of template for VOC xml annotation file')
    parser.add_argument('--roi_per_dim', metavar='roi_per_dim', default=10,
                        help='the number of ROIs per axis in the mosaic')
    parser.add_argument('--orig_roi_ptf', metavar='orig_roi_ptf',
                        default=[], help='where the original ROIs live')

    # parse inputs from command line
    args = parser.parse_args()

    path_to_mos = args.path_to_mos
    path_to_coords = args.path_to_coords
    output_path = args.output_path
    make_voc = str2bool(args.make_voc)
    anntem = args.annotation_template
    roi_per_dim = int(args.roi_per_dim)
    orig_roi_ptf = args.orig_roi_ptf

    # if only processing one mosaic, put it into a dummy list for subsequent loops
    if os.path.isfile(path_to_mos):
        moz = [path_to_mos]
    elif os.path.isdir(path_to_mos):
        moz = sorted(glob.glob(os.path.join(path_to_mos, '*.psd')))
    else:
        sys.exit('Check that mosaic input is either path to PSD file or directory containing PSD files')

    # create output directories
    os.makedirs(os.path.join(output_path, 'Segmentation'), exist_ok=True)
    os.makedirs(os.path.join(output_path, 'JPEGImages'), exist_ok=True)
    os.makedirs(os.path.join(output_path, 'Annotations'), exist_ok=True)

    # if the input is a json document, process accordingly
    if os.path.isfile(path_to_coords):

        assert os.path.splitext(path_to_coords)[1] == '.json', 'Coordinate file must be json document'

        with open(path_to_coords, 'r') as ff:
            all_coords = json.load(ff)
            ff.close()

        # loop over the mosaics
        for mos in moz:

            # read in the mosaic
            psd = read_psd(mos)
            lays = layers2gray(psd)  # get list of layers
            orig = lays[0]
            mask = lays[1]

            # get the right coordinate set (assumes the numbering in the mosaic basename is consistent with keys in
            # coordinate dictionary)
            num = os.path.splitext(os.path.basename(mos))[0]
            num = re.sub('[^0-9]', '', num)

            # use the number to get the coordinate pd array
            coords = read_nested_pd(all_coords, f'mos_{num}')

            if orig_roi_ptf:
                coords['path'] = coords['path'].apply(lambda x: os.path.join(orig_roi_ptf, os.path.basename(x)))

            # get the mask associated with each region
            mask_rois = retrieve_regions(mask, coords)

            # cut out the subregions using original coordinates and ROI dimensions.
            orig_rois = retrieve_regions(orig, coords)

            # iterate over the images, generate and saves masks
            # assumes that the dictonary keys are file paths
            for kk in orig_rois.keys():

                # make a mask of the entire object
                tmp = fill_gap(thresh(orig_rois[kk], threshold=250))
                gen_msk, genbb = big_region(tmp, pad=5)  # assume default settings

                # binarize and invert the egg mask
                egg_msk = mask_rois[kk]
                egg_msk[np.nonzero(egg_msk < 250)] = 0
                egg_msk = egg_msk.astype(np.float32) / 255
                egg_msk = 1 - egg_msk

                # get the egg bounding box
                try:
                    _, eggbb = big_region(egg_msk, pad=5)

                    # make the bounding boxes into one array
                    bbox = np.vstack((genbb, eggbb))

                    # add them together to get the complete mask
                    # [0 == background, 1 == copepod, 2 == eggs]
                    msk = gen_msk + egg_msk

                except ValueError:

                    # handler if no egg mask
                    print('no eggs in', os.path.basename(kk))
                    bbox = np.array(genbb)
                    msk = gen_msk

                # for now assume using VOC file structure
                out_msk = os.path.join(output_path, 'Segmentation', os.path.basename(kk))

                # make mask into color image for storage [default for skimage routine sets cope as red, eggs as blue]
                msk = label2rgb(msk, bg_label=0)
                imwrite(out_msk.replace('jpg','png'), msk*255)

                out_roi = os.path.join(output_path, 'JPEGImages', os.path.basename(kk))

                if not os.path.exists(out_roi):
                    imwrite(out_roi, orig_rois[kk])

                # make the VOC file
                populate_voc(anntem, os.path.join(output_path, 'Annotations'),
                             kk, bbox, ['Copepod', 'Eggs'])

            print('done with', mos)

    # process data if image paths are stored as text files.
    # assumes text files contain list of ROIs in each mosaic
    elif os.path.isdir(path_to_coords):

        # loop over the mosaics
        for mos in moz:

            # get the text file corresponding to the mosaic
            xx = os.path.splitext(os.path.basename(mos))[0]
            tmp = os.path.join(path_to_coords, xx + '.txt')

            with open(tmp, 'r') as ff:
                roi_ptfs = list(ff)
                ff.close()

            roi_ptfs = [line.strip() for line in roi_ptfs]

            # check if roi list in windows format and reset as necessary
            if len(roi_ptfs[0].split('\\')) > 1:
                roi_ptfs = [line.split('\\')[-1] for line in roi_ptfs]
                roi_ptfs = [os.path.join('/Users/eorenstein/Documents/eggs-data/all_eggs_noscale',
                                         line) for line in roi_ptfs]  # hard coded for now (ECO 2/15/21)

            # read in the mosaic
            psd = read_psd(mos)
            lays = layers2gray(psd)  # get list of layers
            orig = np.array(lays[0])  # make the layer into array from PIL
            mask = np.array(lays[1])

            # rotate arrays and make normalize
            # must rotate since since PSD files aligned for annotation on a tablet
            orig = np.rot90(orig)
            mask = np.rot90(mask)

            # get the number of pixels per ROI dimension in the mosaic
            mm = orig.shape[0] // roi_per_dim
            nn = orig.shape[1] // roi_per_dim

            # make into subregions
            orig_subs = get_subregions(orig, roi_dim=roi_per_dim)
            mask_subs = get_subregions(mask, roi_dim=roi_per_dim)

            # loop over the image paths, extract, save as necessary
            for ii in range(len(roi_ptfs)):

                roi_ptf = roi_ptfs[ii]

                # get the original ROI dimensions
                wd, ht = get_dim(roi_ptf)

                # get the coordinates of the upper left corner of original ROI in the padded version
                xx = (mm - wd) // 2
                yy = (mm - ht) // 2

                # crop it out
                orig_crop = orig_subs[ii]
                orig_crop = orig_crop[yy:yy+ht, xx:xx+wd]
                egg_msk = mask_subs[ii]
                egg_msk = egg_msk[yy:yy+ht, xx:xx+wd]

                # get the full copepod mask
                tmp_mask = fill_gap(thresh(orig_crop))
                gen_msk, genbb = big_region(tmp_mask, pad=5)  # assume default settings

                # binarize and invert the egg mask
                egg_msk[np.nonzero(egg_msk < 250)] = 0
                egg_msk = egg_msk.astype(np.float32) / 255
                egg_msk = 1 - egg_msk

                # get the egg bounding box
                try:
                    _, eggbb = big_region(egg_msk, pad=5)

                    # make the bounding boxes into one array
                    bbox = np.vstack((genbb, eggbb))

                    # add them together to get the complete mask
                    # [0 == background, 1 == copepod, 2 == eggs]
                    msk = gen_msk + egg_msk

                except ValueError:

                    # handler if no egg mask
                    print('no eggs in', os.path.basename(roi_ptf))
                    bbox = np.array(genbb)
                    msk = gen_msk

                # for now assume using VOC file structure
                out_msk = os.path.join(output_path, 'Segmentation', os.path.basename(roi_ptf))

                # make mask into color image for storage [default for skimage routine sets cope as red, eggs as blue]
                msk = label2rgb(msk, bg_label=0)
                imwrite(out_msk, msk*255)

                out_roi = os.path.join(output_path, 'JPEGImages', os.path.basename(roi_ptf))

                if not os.path.exists(out_roi):
                    imwrite(out_roi, orig_crop)

                # make the VOC file
                populate_voc(anntem, os.path.join(output_path, 'Annotations'),
                             roi_ptf, bbox, ['Copepod', 'Eggs'])

            print('done with', mos)

    else:
        sys.exit('Ensure that path_to_coords points to directory or text files of json document with coordinate dictionaries')
