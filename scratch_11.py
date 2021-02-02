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
import collections

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



ptfs = glob.glob(os.path.join('/Users/eorenstein/Documents/eggs-data/img-lists','*.txt'))
ptfs.sort()

rois = []
for xx in ptfs:

    with open(xx, 'r') as ff:
        temp = list(ff)
        ff.close()

    if 'Sans titre19' in os.path.basename(xx):
        rois.extend(temp[0:34])
    else:
        rois.extend(temp)

rois = [line.strip() for line in rois]
rois = [os.path.splitext(line.split('\\')[-1])[0] for line in rois]

# get unique list elements
seen = set()
uniq = [x for x in rois if x not in seen and not seen.add(x)]

# get elements that show up more than once
dups = [item for item, count in collections.Counter(rois).items() if count > 1]

# all egg images
eggs = glob.glob(os.path.join('/Users/eorenstein/Documents/eggs-data/all_eggs_noscale', '*.jpg'))

with open('/Users/eorenstein/Documents/eggs-data/img-lists/unique.txt', 'w') as ff:
    for line in uniq:
        ff.write(line + '\n')
    ff.close()

with open('/Users/eorenstein/Documents/eggs-data/img-lists/dups.txt', 'w') as ff:
    for line in dups:
        ff.write(line + '\n')
    ff.close()

proc = [line for line in eggs if os.path.splitext(os.path.basename(line))[0] not in uniq]

with open('/Users/eorenstein/Documents/eggs-data/img-lists/to_process_020221.txt', 'w') as ff:
    for line in proc:
        ff.write(line + '\n')
    ff.close()
