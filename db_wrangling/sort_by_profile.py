import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.axes_divider import make_axes_area_auto_adjustable
import numpy as np
import os

# import data from the tsv file
copes = pd.read_table(r'D:\LOV\all_copepoda.tsv', header=0)
#copes = pd.read_table('/Users/eorenstein/Documents/eggs-data/all_copepoda.tsv', header=0)
copes['object_length_mm'] = copes['object_major']*copes['sample_pixel']  #fill in the major object length in mm

# Do the same for the eggs
eggs = pd.read_table(r'D:\LOV\all_eggs.tsv', header=0)
#eggs = pd.read_table('/Users/eorenstein/Documents/eggs-data/all_eggs.tsv', header=0)
eggs['object_length_mm'] = eggs['object_major']*eggs['sample_pixel']  #fill in the major object length in mm

# find the unique project names and number of associate entries
uniq_copes = copes['sample_original_projname'].value_counts()
uniq_eggs = eggs['sample_original_projname'].value_counts()

# remove projects that don't have egg annotations
no_eggs = [line for line in uniq_copes.index if line not in uniq_eggs.index]
copes_match = copes[~copes['sample_original_projname'].isin(no_eggs)]

## get the list of unique profiles in the copes dataset
cope_profs = copes_match['sample_original_sampleid'].value_counts().index.to_list()

# randomize
np.random.shuffle(cope_profs)

# separate into an 80-20 train-val split and plot
ind = int(len(cope_profs)*0.8)
fig, ax = plt.subplots()
bb1 = copes_match[copes_match['sample_original_sampleid'].isin(cope_profs[0:ind])]\
    ['object_length_mm'].transform('log').hist(bins=30, color='r', alpha=0.6, ax=ax, density=True)
bb2 = copes_match[copes_match['sample_original_sampleid'].isin(cope_profs[ind::])]\
    ['object_length_mm'].transform('log').hist(bins=30, color='g', alpha=0.6, ax=ax, density=True)
ax.grid(False)
ax.set_ylabel('counts')
ax.set_xlabel('log(mm)')
ax.legend(['train set', 'test set'])
#fig.legend([bb1, bb2], labels=['train set', 'test set'], loc='lower left', bbox_to_anchor=(0.73, 0.75))
ax.set_title(f'Major axis distribution splitting copepod profiles 80/20')

## get the list of unique profiles in the eggs dataset
egg_profs = eggs['sample_original_sampleid'].value_counts().index.to_list()

# randomize
np.random.shuffle(egg_profs)

# separate into an 80-20 train-val split and plot
ind = int(len(egg_profs)*0.8)
fig, ax = plt.subplots()
bb1 = eggs[eggs['sample_original_sampleid'].isin(egg_profs[0:ind])]\
    ['object_length_mm'].transform('log').hist(bins=30, color='r', alpha=0.6, ax=ax, density=True)
bb2 = eggs[eggs['sample_original_sampleid'].isin(egg_profs[ind::])]\
    ['object_length_mm'].transform('log').hist(bins=30, color='g', alpha=0.6, ax=ax, density=True)
ax.grid(False)
ax.set_ylabel('counts')
ax.set_xlabel('log(mm)')
ax.legend(['train set', 'test set'])
#fig.legend([bb1, bb2], labels=['train set', 'test set'], loc='lower left', bbox_to_anchor=(0.73, 0.75))
ax.set_title(f'Major axis distribution splitting egg profiles 80/20')