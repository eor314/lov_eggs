import numpy as np
import os
import glob
import cv2
from PIL import Image
import pandas as pd
import argparse
import json
from shutil import rmtree
from utils.img_proc import tile_images


def get_dim(img):
    """
    return biggest of image dimensions
    :param img: absolute path to image [str]
    :return: max(width, height) [int]
    """
    im = Image.open(img)
    wid, hgt = im.size
    return [wid, hgt]


def image_list(ptf, ext='jpg'):
    """
    read in images from file
    :param ptf: absolute path to file containing images to tile [str]
    :param ext: file extension to read (default == 'jpg') [str]
    :return: list of absolute paths
    """

    out = glob.glob(os.path.join(ptf, f'*.{ext}'))
    return out


def divide_list(img_list, num_img):
    """
    splits list into appropriate length for tiling and extract dims
    :param img_list: list of absolute image paths [list of strs]
    :param num_img: number of images per mosaic [int]
    :return: dictionary of panda arrays
    """

    # randomize the image paths in place
    np.random.shuffle(img_list)

    # break the list into chunks
    chunks = {f'mos_{ind}': pd.DataFrame(img_list[ii:ii+num_img], columns=['path']) for
                ind, ii in enumerate(range(0, len(img_list), num_img))}

    return chunks


if __name__ == '__main__':

    # define parser
    parser = argparse.ArgumentParser(description='Create a set of mosaics of set number of images from list')

    parser.add_argument('path_to_imgs', metavar='path_to_imgs', help='Absolute path to directory of images')
    parser.add_argument('output_path', metavar='output_path', help='Where to save the output mosaics')
    parser.add_argument('--num_images', metavar='num_images',
                        default=100, help='Number of image per mosaic (make sure is is a perfect square)')
    parser.add_argument('--file_type', metavar='file_type',
                        default='jpg', choices=['jpg', 'png', 'tiff'], help='type of file to look for')

    args = parser.parse_args()

    path_to_imgs = args.path_to_imgs
    file_type = args.file_type
    output_path = args.output_path
    num_imgs = int(args.num_images)

    # make the output directory if it does not exist, otherwise delete what is in there
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    else:
        rmtree(output_path)

    # get the list of images
    imgs = image_list(path_to_imgs, file_type)

    # get the chunks of paths
    mos_imgs = divide_list(imgs, num_imgs)

    # iterate over dataframes, get dims of each
    print('making', len(mos_imgs.keys()), 'mosaics')
    for kk in mos_imgs.keys():
        tmp = mos_imgs[kk]

        # get the dimensions of each image
        tmp['dims'] = tmp['path'].apply(lambda x: get_dim(x))
        tmp[['width', 'height']] = pd.DataFrame(tmp['dims'].tolist())

        # get the biggest dimension of all ROIs
        mx_dim = tmp[['width', 'height']].max(axis=1).max()

        # tile the ROIs
        tmp_mos, tmp_coor = tile_images(tmp['path'].to_list(), 10, resize=mx_dim)

        # put the coordinates into the dataframe
        tmp['upper_left_coord'] = tmp_coor

        # remove dims and serialize back into master dictionary
        tmp = tmp.drop(columns=['dims'])
        mos_imgs[kk] = tmp.to_json(orient='records')

        # save the mosaic to the desired directory
        cv2.imwrite(os.path.join(output_path, f'{kk}.{file_type}'), tmp_mos)

        print('done with', kk)

    # save the dictionary as JSON for retrieving masks later
    with open(os.path.join(output_path, 'dims_coords.json'), 'w') as ff:
        json.dump(mos_imgs, ff)
        ff.close()
