import json
import numpy as np
import pandas
import glob
import os
import matplotlib.pyplot as plt
from utils.mosaic_tools import read_nested_pd, read_psd, layers2gray, retrieve_regions
from utils.img_proc import pad_img
import cv2
from shutil import rmtree

ptfs = glob.glob(os.path.join(r'D:\LOV\Eggs copepods\img-lists', '*.txt'))

for ptf in ptfs:

    xx = os.path.splitext(os.path.basename(ptf))[0]
    mos = f'D:\\LOV\\Eggs copepods\\{xx}.psd'

    with open(ptf, 'r') as ff:
        img_ptfs = list(ff)
        ff.close()

    outdir = f'C:\\Users\\eor34\\Desktop\\temp\\{xx}'

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    img_ptfs = [line.strip() for line in img_ptfs]

    psd = read_psd(mos)
    lays = layers2gray(read_psd(mos))
    # show the original mosaics
    orig = lays[0]

    orig = np.rot90(np.array(orig))
    orig = orig.astype(np.float64) / 255
    mm = orig.shape[0]//10
    nn = orig.shape[1]//10
    subs = [orig[x:x+mm, y:y+nn] for x in range(0, orig.shape[0], mm) for y in range(0, orig.shape[1], nn)]

    for ii in range(len(img_ptfs)):
        tmp = cv2.imread(img_ptfs[ii], 0)
        ht, wd = tmp.shape

        xx = (mm - wd) // 2
        yy = (mm - ht) // 2

        sub = subs[ii]
        sub_crop = sub[yy:yy+ht, xx:xx+wd]
        fig, ax = plt.subplots(1,2)
        ax[0].imshow(sub_crop,cmap='gray')
        ax[0].set_title('from sans titre 14')

        ax[1].imshow(tmp, cmap='gray')
        ax[1].set_title('from minimization list')
        fig.suptitle(img_ptfs[ii] + ' ' + str(ii))
        plt.savefig(os.path.join(outdir, f'{ii}_{xx}.png'))
        plt.close()

    print(f'done with {xx}')



ptfs = glob.glob(os.path.join(r'D:\LOV\Eggs copepods\img-lists', '*.txt'))

rois = []
for xx in ptfs:
    with open(xx, 'r') as ff:
        rois.extend(ff)
        ff.close()

rois = [line.strip() for line in rois]