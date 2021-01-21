import numpy as np
import argparse
import cv2
import os
import glob
from utils.img_proc import thresh, fill_gap, big_region


if __name__ == '__main__':

    # parser stuff
    parser = argparse.ArgumentParser(description='Make and saves masks from UVP images')

    parser.add_argument('path_to_imgs', metavar='path_to_imgs', help='Absolute path to image dir')
    parser.add_argument('output_path', metavar='output_path', help='where to store the processed images')
    parser.add_argument('--file_type', metavar='file_type',
                        default='jpg', choices=['jpg', 'png', 'tiff'], help='type of file to look for')
    parser.add_argument('--thresh_val', metavar='tresh_val', default=245, help='uint8 value for naive thresholding')
    parser.add_argument('--struct_el', metavar='stuct_el', default='disk',
                        choices=['disk', 'diamond', 'square'], help='structuring element shape')
    parser.add_argument('--stel_size', metavar='stel_size', default=3, help='radius of structuring element')
    parser.add_argument('--connect', metavar='connect', default=2,
                        help='connectivity to consider in connected component analysis [see skimage label for details]')
    parser.add_argument('--back_gr', metavar='back_gr', default=0,
                        help='pixel value to consider background [see skimage label for details]')
    parser.add_argument('--padding', metavar='padding', default=5,
                        help='pixel value to pad bounding box [set to zero if do not need]')

    args = parser.parse_args()

    ptf = args.path_to_imgs
    outptf = args.output_path
    ftype = args.file_type

    # list of images
    imgs = glob.glob(os.path.join(ptf, f'*.{ftype}'))

    # create the output directory (assuming VOC2012 file structure)
    outdir = os.path.join(outptf, 'Segmentation')

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    flag = 0
    for img in imgs:

        # read in the image as numpy array in uint8
        orig = cv2.imread(img)
        orig = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)

        # threshold it
        mask = thresh(orig, threshold=args.thresh_val)

        # close holes
        mask = fill_gap(mask, struct=args.struct_el, dim=args.stel_size)

        # select the biggest region
        mask = big_region(mask, conn=args.connect, bg=args.back_gr, pad=args.padding)
        mask = mask*255

        outpath = os.path.join(outdir, os.path.basename(img))

        cv2.imwrite(outpath, mask)

        flag += 1
        if flag % 100 == 0:
            print('Done with', flag, 'of', len(imgs))
