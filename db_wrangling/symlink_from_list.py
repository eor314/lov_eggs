import numpy as np
import argparse
import os
import glob


if __name__ == '__main__':

    # parser stuff
    parser = argparse.ArgumentParser(description='output symlink to desired directory from list of ROIs')

    parser.add_argument('path_to_imgs', metavar='path_to_imgs', help='Absolute path to original image dir')
    parser.add_argument('output_path', metavar='output_path', help='where to symlink images')
    parser.add_argument('proc_list', metavar='proc_list', help='list of items to symlink')
    parser.add_argument('--subset', action='store_true', help='take a subset of the whole image list')
    parser.add_argument('--ind', metavar='ind', default=1000, help='index to save')
    parser.add_argument('--subpct', metavar='subpct', default=0, help='amount to draw from list as % [default=0]')
    parser.add_argument('--file_type', metavar='file_type',
                        default='jpg', choices=['jpg', 'png', 'tiff'], 
                        help='file extension to append to ROI objid [default=0]')
    parser.add_argument('--randomize', action='store_true', 
                        help='randomize the image-id list before saving symlink')
    
    args = parser.parse_args()

    ptf = args.path_to_imgs
    outptf = args.output_path
    proc_list = args.proc_list
    subpct = float(args.subpct)
    ftype = args.file_type
    randomize = args.randomize
    ind = int(args.ind)
    subset = args.subset
    
    
    # check inputs
    assert (os.path.isdir(ptf)), 'check that path_to_images is valid file path'
    assert (os.path.isfile(proc_list)), 'check that proc_list points to a text file'
    
    # get the list
    with open(proc_list, 'r') as ff:
        to_symlink = list(ff)
        ff.close()

    if subpct != 0:
        ind = int(np.floor(len(to_symlink)*subpct))

    if not subset:
        to_symlink = [os.path.join(ptf, f'{line.strip()}.{ftype}') for line in to_symlink]
        
        if randomize:
            np.random.shuffle(to_symlink)
        
        if not os.path.exists(outptf):
            os.mkdir(outptf)
        
        for line in to_symlink:
            os.symlink(line, os.path.join(outptf, os.path.basename(line)))
            
        print('symlinked', len(to_symlink), 'from', ptf, 'to', outptf)
        
    else:
        # symlink a subset of the file (assumes training and validation data have already been split)
        
        # read the file
        with open(proc_list, 'r') as ff:
            to_symlink = list(ff)
            ff.close()
            
        # get the subset
        to_symlink = to_symlink[0:ind]
        
        to_symlink = [os.path.join(ptf, f'{line.strip()}.{ftype}') for line in to_symlink]
        
        if randomize:
            np.random.shuffle(to_symlink)
        
        if not os.path.exists(outptf):
            os.mkdir(outptf)
        
        for line in to_symlink:
            os.symlink(line, os.path.join(outptf, os.path.basename(line)))
            
        print('symlinked', len(to_symlink), 'from', ptf, 'to', outptf)