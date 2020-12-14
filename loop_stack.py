import numpy as np
import os
import glob
import cv2
from stack_photoshop import save_stack
import argparse

if __name__ == '__main__':

    # define parser
    parser = argparse.ArgumentParser(description='Loop over directory and make into psd')

    parser.add_argument('path_to_imgs', metavar='path_to_imgs', help='Absolute path to directory of images')
    parser.add_argument('--file_type', metavar='file_type',
                        default='jpg', choices=['jpg', 'png', 'tiff'], help='type of file to look for')

    args = parser.parse_args()

    path_to_imgs = args.path_to_imgs
    file_type = args.file_type

    # get the list of mosaics
    img_paths = glob.glob(os.path.join(path_to_imgs, f'*.{file_type}'))

    for img_ptf in img_paths:

        # read image as gray scale
        im = cv2.imread(img_ptf, 0)

        # create empty label layer of same size
        lab = np.zeros(im.shape)

        # make the sub directory
        outdir = os.path.join(path_to_imgs, os.path.basename(os.path.splitext(img_ptf)[0]))

        # make the psd file
        save_stack(im, lab, outdir, fmt=['psd'])
