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
    parser.add_argument('--subpct', metavar='subpct', default=0, help='amount to draw from list as % [default=0]')
    parser.add_argument('--file_type', metavar='file_type',
                        default='jpg', choices=['jpg', 'png', 'tiff'], 
                        help='file extension to append to ROI objid [default=0]')
    
    args = parser.parse_args()

    ptf = args.path_to_imgs
    outptf = args.output_path
    proc_list = args.proc_list
    subpct = args.subpct
    ftype = args.file_type
    
    
    # check inputs
    assert (os.path.isdir(ptf)), 'check that path_to_images is valid file path'
    assert (os.path.isfile(proc_list)), 'check that proc_list points to a text file'
    
    if subpct == 0:
        # symlink the whole list
        with open(proc_list, 'r') as ff:
            to_symlink = list(ff)
            ff.close()
        
        to_symlink = [os.path.join(ptf, f'{line.strip()}.{ftype}') for line in to_symlink]
        
        if not os.path.exists(outptf):
            os.mkdir(outptf)
        
        for line in to_symlink:
            os.symlink(line, os.path.join(outptf, os.path.basename(line)))
            
        print('symlinked', len(to_symlink), 'from', ptf, 'to', outptf)
        
    else:
        # symlink a subset of the file (assumes training and validation data have already been split)
        subpct = float(subpct)  # make sure the percent is float
        
        # read the file
        with open(proc_list, 'r') as ff:
            to_symlink = list(ff)
            ff.close()
            
        # get the index for spliting
        ind = int(np.floor(len(to_symlink)*subpct))
        to_symlink = to_symlink[0:ind]
        
        to_symlink = [os.path.join(ptf, f'{line.strip()}.{ftype}') for line in to_symlink]
        
        if not os.path.exists(outptf):
            os.mkdir(outptf)
        
        for line in to_symlink:
            os.symlink(line, os.path.join(outptf, os.path.basename(line)))
            
        print('symlinked', len(to_symlink), 'from', ptf, 'to', outptf)