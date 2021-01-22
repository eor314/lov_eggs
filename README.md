# lov_eggs

Preprocess plankton image data for object detection, segmentation, and deep regression models. Create and parse mosaics for segmentation annotation in Photoshop. Tested with Anaconda run in PyCharm on Windows 10.

Requirements:
- numpy
- PIL
- Cython
- pytoshop
- cv2
- argparse
- pandas
- sklearn
- bs4

### NameError name packbits is not defined
pytoshop has a NameError in python 3.7 when trying to write psd files. Was able to fix from this <a href='https://github.com/mdboom/pytoshop/issues/9#issuecomment-534904333'>issue discussion</a>:

> open this file:
> ~\Programs\Python\Python36\lib\site-packages\pytoshop\codecs.py

> Change the packbits import statement from this:
```
try:
  from . import packbits # type: ignore
except ImportError:
  pass
```
> To this
```
try:
  import packbits # type: ignore
except ImportError:
  pass
```
