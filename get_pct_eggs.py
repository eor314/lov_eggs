import numpy as np
import pandas as pd
import os
import glob
import cv2
import skimage
import matplotlib.pyplot as plt
from utils.img_proc import thresh

path_to_segs = '/Users/eorenstein/Documents/eggs-data/VOCeggs/Segmentation'

segs = glob.glob(os.path.join(path_to_segs, '*.jpg'))
segs.sort()

test = cv2.imread(segs[1])

bod = np.zeros(test.shape[0:2])
bod[np.nonzero(test[:, :, 0] > 50)] = 1

np.sum(bod)

egg = np.zeros(test.shape[0:2])
egg[np.nonzero(test[:, :, 2] > 50)] = 1

np.sum(egg)

fig, ax = plt.subplots(1, 3)
ax[0].imshow(test)
ax[1].imshow(bod, cmap='gray')
ax[2].imshow(egg, cmap='gray')

output = pd.DataFrame(columns=['img-id', 'egg (px)', 'body (px)'])
output['img-id'] = [os.path.basename(line) for line in segs]

for ii in range(len(segs)):
    test = cv2.imread(segs[ii])

    bod = np.zeros(test.shape[0:2])
    bod[np.nonzero(test[:, :, 0] > 50)] = 1
    output.loc[ii]['body (px)'] = np.sum(bod)

    egg = np.zeros(test.shape[0:2])
    egg[np.nonzero(test[:, :, 2] > 50)] = 1
    output.loc[ii]['egg (px)'] = np.sum(egg)

output['pct egg'] = output['egg (px)']/output['body (px)']
output['pct egg'] = pd.to_numeric(output['pct egg'])
output['egg (px)'] = pd.to_numeric(output['egg (px)'])
output['body (px)'] = pd.to_numeric(output['body (px)'])

output['pct egg'].hist(grid=False, bins=15)
plt.xlabel('% egg pixels')
plt.ylabel('counts')
plt.title('% egg distribution (# ROIs = 1490)')

mx_egg_seg = os.path.join('/Users/eorenstein/Documents/eggs-data/VOCeggs/Segmentation', output['pct egg'].idxmax())
mx_egg_img = os.path.join('/Users/eorenstein/Documents/eggs-data/VOCeggs/JPEGImages', output['pct egg'].idxmax())

mx_egg_seg = cv2.imread(mx_egg_seg)
mx_egg_img = cv2.imread(mx_egg_img, 0)

fig, ax = plt.subplots(1, 2)
ax[0].imshow(mx_egg_img, cmap='gray')
ax[0].set_title('max egg image')
ax[0].set_xticks([])
ax[0].set_yticks([])

ax[1].imshow(mx_egg_seg)
ax[1].set_xticks([])
ax[1].set_yticks([])
ax[1].set_title('max % egg segmentation')

fig.suptitle('image id: ' + os.path.splitext(output['pct egg'].idxmax())[0] +
             ', % egg px=' + str(np.round(output['pct egg'].max(), decimals=2)))
