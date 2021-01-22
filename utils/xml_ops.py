from bs4 import BeautifulSoup
import glob
import os
from make_mosaic_psd import get_dim


def populate_voc(template, outdir, imgptf, bbox, label):
    """
    iterate over all the xml files in the annotations directory, consolidate, and copy
    :param template: xml template to work from
    :param outdir: path to output directory (where new files are copied)
    :param imgptf: where the image lives
    :param bbox: bounding box coordinates [list of tuples]
    :param label: labels corresponding to bboxes and segments [list of ind]
    """

    # read in the annotations
    with open(template, 'r') as ff:
        temp = ff.read()
        ff.close()

    # make it into a soup object
    bs_data = BeautifulSoup(temp, 'xml')

    # insert folder path
    fold = bs_data.folder
    fold.string = os.path.split(imgptf)[0]

    # insert filename
    fname = bs_data.filename
    fname.string = os.path.split(imgptf)[1]

    # get the dimensions
    wd, ht = get_dim(imgptf)
    width = bs_data.size.width
    width.string = str(wd)
    height = bs_data.size.height
    height.string = str(ht)

    # bounding box info
    # for now just select the first tuple and hardcode other into [012221]
    bb = bbox[0]
    name = bs_data.object.find('name')  # have to use find since 'name' heading shadows bs4 method
    name.string = label[0]
    xmin = bs_data.object.bndbox.xmin
    xmin.string = str(bb[1])
    ymin = bs_data.object.bndbox.ymin
    ymin.string = str(bb[0])
    xmax = bs_data.object.bndbox.xmax
    xmax.string = str(bb[3])
    ymax = bs_data.object.bndbox.ymax
    ymax.string = str(bb[2])

    outpath = os.path.join(outdir, os.path.splitext(os.path.basename(imgptf))[0]+'.xml')

    # save it
    with open(outpath, 'w') as ff:
        ff.write(str(bs_data))
        ff.close()