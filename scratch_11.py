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


# make plots of pairs of extracted rois to make sure everything in lining up
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

"""
## display rois and masks
# display the original annotated mosaic
fig, ax = plt.subplots()
ax.imshow(np.rot90(psd.numpy())[0:1500, 0::])
ax.set_xticks([])
ax.set_yticks([])
ax.set_title('Mosaic annotated by Louis')

# process the psd file too for display purposes
psd_rois = retrieve_regions(psd.numpy(), coords)

# just work on biggest subregion for now
psd_big = psd_rois['D:\\LOV\\all_eggs_noscale\\62057085.jpg']
cope = orig_rois['D:\\LOV\\all_eggs_noscale\\62057085.jpg']
egg_mask = mask_rois['D:\\LOV\\all_eggs_noscale\\62057085.jpg']

# make pixel mask, again working on biggest region
tmp = fill_gap(thresh(cope))
cope_msk = big_region(tmp)

# binarize the egg mask
egg_msk = egg_mask.astype(np.float32) / 255
egg_msk = 1 - egg_msk  # invert

# ratio of egg pixels to copepod pixels
ovig_pct = np.sum(egg_msk)/np.sum(cope_msk.astype(np.float32)-egg_msk)

# add the masks together. now 0==background, 1==copepod, 2==eggs
msk = cope_msk + egg_msk

# display the biggest copepod and associated mask
fig1, ax1 = plt.subplots(2, 2)

ax1[0,0].imshow(psd_big)
ax1[0,0].set_xticks([])
ax1[0,0].set_yticks([])
ax1[0,0].set_title('ROI w/ mask')

ax1[0,1].imshow(cope, cmap='gray')
ax1[0,1].set_xticks([])
ax1[0,1].set_yticks([])
ax1[0,1].set_title('ROI')

ax1[1,0].imshow(egg_mask, cmap='gray')
ax1[1,0].set_xticks([])
ax1[1,0].set_yticks([])
ax1[1,0].set_title('eggs via manual seg')

ax1[1,1].imshow(msk, cmap='gray')
ax1[1,1].set_xticks([])
ax1[1,1].set_yticks([])
ax1[1,1].set_title('auto cope + eggs')
"""

# reformat image lists for mac
outfile = '/Users/eorenstein/Documents/eggs-data/img-lists-mac'
ptf = '/Users/eorenstein/Documents/eggs-data/all_eggs_noscale'
os.mkdir(outfile)
infiles = glob.glob(os.path.join('/Users/eorenstein/Documents/eggs-data/img-lists', 'Sans*'))

for infile in infiles:
    with open(infile, 'r') as ff:
        tmp = list(ff)
        ff.close()
    tmp = [line.strip() for line in tmp]
    tmp = [os.path.join(ptf, line.split('\\')[-1]) for line in tmp]
    with open(os.path.join(outfile, os.path.basename(infile)), 'w') as ff:
        for line in tmp:
            ff.write(line+'\n')
        ff.close()

