import os
import glob
import cv2
from shutil import rmtree
import argparse


if __name__ == '__main__':

    # define parser
    parser = argparse.ArgumentParser(description='Loop over directory and make into psd')

    parser.add_argument('path_to_imgs', metavar='path_to_imgs', help='Absolute path to EcoTaxa export')
    parser.add_argument('output_path', metavar='output_path', help='where to store the processed images')
    parser.add_argument('--file_type', metavar='file_type',
                        default='jpg', choices=['jpg', 'png', 'tiff'], help='type of file to look for')

    args = parser.parse_args()
    ptf = args.path_to_imgs
    outptf = args.output_path
    ftype = args.file_type

    # list of images
    imgs = glob.glob(os.path.join(ptf, '*', f'*.{ftype}'))

    if os.path.exists(outptf):
        rmtree(outptf)
        os.mkdir(outptf)

    for item in imgs:
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
