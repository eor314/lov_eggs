import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# import data from the tsv file
#copes = pd.read_table(r'D:\LOV\all_copepoda.tsv', header=0)
copes = pd.read_csv('/Users/eorenstein/Documents/eggs-data/copepod_update.csv')
copes['object_length_mm'] = copes['object_major']*copes['sample_pixel']  #fill in the major object length in mm

# Do the same for the eggs
#eggs = pd.read_table(r'D:\LOV\all_eggs.tsv', header=0)
eggs = pd.read_csv('/Users/eorenstein/Documents/eggs-data/eggs_update.csv')
eggs['object_length_mm'] = eggs['object_major']*eggs['sample_pixel']  #fill in the major object length in mm

## get the list of unique profiles in the copes dataset
cope_profs = copes['sample_original_sampleid'].value_counts().index.to_list()

## get the list of unique profiles in the eggs dataset
egg_profs = eggs['sample_original_sampleid'].value_counts().index.to_list()

# randomize
np.random.shuffle(egg_profs)
train_ind = int(len(egg_profs)*0.7)  # select 70% for training
val_ind = train_ind + int(len(egg_profs)*0.15)  # select 15% for validation
egg_train = eggs[eggs['sample_original_sampleid'].isin(egg_profs[0:train_ind])]
egg_val = eggs[eggs['sample_original_sampleid'].isin(egg_profs[train_ind:val_ind])]
egg_test = eggs[eggs['sample_original_sampleid'].isin(egg_profs[val_ind::])]

# make sure the egg profiles in the validation data are also taken from copepods (ie to have complete profiles)
cope_test = copes[copes['sample_original_sampleid'].isin(egg_profs[val_ind::])]
cope_train = copes[copes['sample_original_sampleid'].isin(egg_profs[0:train_ind])]
cope_val = copes[copes['sample_original_sampleid'].isin(egg_profs[train_ind:val_ind])]
cope_other = copes[~copes['sample_original_sampleid'].isin(egg_profs)]

# save to lists
#outpath = r'D:/LOV/VOCCopepodEgg/ImageLists/'
outpath = '/Users/eorenstein/Documents/eggs-data/ImageLists/SplitByProfile-230221'
egg_train['object_original_objid'].astype(int).to_csv(os.path.join(outpath, 'egg_train.txt'),
                                                      header=False, index=False)
egg_test['object_original_objid'].astype(int).to_csv(os.path.join(outpath, 'egg_test.txt'),
                                                     header=False, index=False)
egg_val['object_original_objid'].astype(int).to_csv(os.path.join(outpath, 'egg_val.txt'),
                                                     header=False, index=False)
cope_train['object_original_objid'].astype(int).to_csv(os.path.join(outpath, 'cope_train.txt'),
                                                       header=False, index=False)
cope_test['object_original_objid'].astype(int).to_csv(os.path.join(outpath, 'cope_test.txt'),
                                                       header=False, index=False)
cope_other['object_original_objid'].astype(int).to_csv(os.path.join(outpath, 'cope_other.txt'),
                                                       header=False, index=False)
cope_val['object_original_objid'].astype(int).to_csv(os.path.join(outpath, 'cope_val.txt'),
                                                       header=False, index=False)
