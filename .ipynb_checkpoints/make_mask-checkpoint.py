import numpy as np
import argparse
import cv2
import os
import glob
from utils.img_proc import thresh, fill_gap, big_region
from utils.xml_ops import populate_voc


if __name__ == '__main__':

    # parser stuff
    parser = argparse.ArgumentParser(description='Make and saves masks from UVP images')

    parser.add_argument('path_to_imgs', metavar='path_to_imgs', help='Absolute path to image dir')
    parser.add_argument('output_path', metavar='output_path', help='where to store the processed images')
    parser.add_argument('--template', metavar='template',
                        default='lov_voc_template.xml', help='absolute path to xml template file lives')
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
    template = args.template

    # list of images
    imgs = glob.glob(os.path.join(ptf, f'*.{ftype}'))

    # create the output directory (assuming VOC2012 file structure)
    outdir = os.path.join(outptf, 'Segmentation')
    anndir = os.path.join(outptf, 'Annotations')

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    if not os.path.exists(anndir):
        os.mkdir(anndir)

    flag = 0
    for img in imgs:
        
        # create the path to save out the segmentation
        outpath = os.path.join(outdir, os.path.basename(img))
        anntemp = os.path.join(anndir, os.path.basename(img))
        
        # check for path existance and skip or delete as necessecary
        if os.path.exists(outpath) and os.path.exists(anntemp):
            continue
        elif os.path.exists(outpath) and not os.path.exists(anntemp):
            os.remove(outpath)
        else:
            pass

        # read in the image as numpy array in uint8
        orig = cv2.imread(img)
        orig = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)

        # threshold it
        mask = thresh(orig, threshold=args.thresh_val)

        # close holes
        mask = fill_gap(mask, struct=args.struct_el, dim=args.stel_size)

        # select the biggest region
        mask, bbox = big_region(mask, conn=args.connect, bg=args.back_gr, pad=args.padding)
        mask = mask*255

        cv2.imwrite(outpath, mask)

        # populate the XML annotation file
        populate_voc(template,
                     anndir, img, np.array(bbox), ['Copepod'])

        flag += 1
        if flag % 1000 == 0:
            print('Done with', flag, 'of', len(imgs))
