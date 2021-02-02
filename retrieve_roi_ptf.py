import numpy as np
import glob
import os
from utils.mosaic_tools import read_psd, layers2gray
from utils.img_proc import pad_img
import cv2


if __name__ == '__main__':

    mos_ptf = glob.glob(os.path.join(r'D:\LOV\Eggs copepods', 'sans*'))
    ptimgs = glob.glob(os.path.join(r'D:\LOV\all_eggs_noscale', '*.jpg'))
    ptimgs.sort()
    mos_ptf.sort()

    outdir = r'D:\LOV\Eggs copepods\img-lists'

    # mos_ptf = [line for line in mos_ptf if os.path.basename(line) in ['Sans titre2.psd', 'Sans titre15.psd']]

    for mos in mos_ptf:

        psd = read_psd(mos)
        tmp = layers2gray(read_psd(mos))
        orig = tmp[0]
        del tmp

        orig = np.rot90(np.array(orig))
        orig = orig.astype(np.float64) / 255
        mm = orig.shape[0]//10
        nn = orig.shape[1]//10
        subs = [orig[x:x+mm, y:y+nn] for x in range(0, orig.shape[0], mm) for y in range(0, orig.shape[1], nn)]

        ims_resize = np.zeros([mm*nn, len(ptimgs)])
        flag = 0
        for img in ptimgs:
            im = cv2.imread(img, 0)
            try:
                tmp, _ = pad_img(im, mm)
                tmp = tmp / 255
                ims_resize[:, flag] = tmp.flatten()
            except ValueError:
                print(os.path.basename(img), 'is too big')

            # increment flag no matter what to make sure the ROI name look up is correct
            flag += 1

        # iterate over the regions and return the index of closest ROI
        sub_ptf = []
        ims_tp = ims_resize.transpose()
        flag = 0
        for sub in subs:
            yy = np.sum(np.square(ims_tp - sub.flatten()), 1)
            ind = np.argmin(yy)
            sub_ptf.append(ptimgs[ind])
            print('done with', flag, 'for', os.path.basename(mos))
            flag += 1

        outptf = os.path.join(outdir, os.path.splitext(os.path.basename(mos))[0]+'.txt')
        with open(outptf, 'w') as ff:
            for line in sub_ptf:
                ff.write(line + '\n')
            ff.close

        print('done with', os.path.basename(mos))
