import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


def list2subdf(path_to_file, orig_df):
    """
    reads in a list of image ids returns a subset of dataframe
    :param path_to_file: absolute path to list of image ids
    :param orig_df: dataframe containing original ROI metadata from EcoTaxa
    :return: subset of df
    """
    with open(path_to_file, 'r') as ff:
        tmp = list(ff)
        ff.close()

    # strip new lines and file extensions
    tmp = [int(line.strip().split('.')[0]) for line in tmp]

    return orig_df[orig_df['object_original_objid'].astype(int).isin(tmp)]


# import data from the tsv file
#copes = pd.read_table(r'D:\LOV\all_copepoda.tsv', header=0)
copes = pd.read_table('/Users/eorenstein/Documents/eggs-data/all_copepoda.tsv', header=0)
copes['object_length_mm'] = copes['object_major']*copes['sample_pixel']  #fill in the major object length in mm

# Do the same for the eggs
#eggs = pd.read_table(r'D:\LOV\all_eggs.tsv', header=0)
eggs = pd.read_table('/Users/eorenstein/Documents/eggs-data/all_eggs.tsv', header=0)
eggs['object_length_mm'] = eggs['object_major']*eggs['sample_pixel']  #fill in the major object length in mm

# positive == eggs, negative == copepod
#ptf = r'D:/LOV/resnet18_1613491390_model_conv_1613494049'

# split by prof
#ptf = '/Users/eorenstein/Documents/eggs-data/outputs/resnet18_1613491390_model_conv_1613494049'

# split randomly
ptf = '/Users/eorenstein/Documents/eggs-data/outputs/resnet18_1613404759_model_conv_1613558460'

t_neg = list2subdf(os.path.join(ptf, 'copepod', 'copepod.txt'), copes)
f_pos = list2subdf(os.path.join(ptf, 'copepod', 'egg.txt'), copes)

t_pos = list2subdf(os.path.join(ptf, 'egg', 'egg.txt'), eggs)
f_neg = list2subdf(os.path.join(ptf, 'egg', 'copepod.txt'), eggs)

# look at the profiles represent the true pos and false neg
t_pos_profs = t_pos['sample_original_sampleid'].value_counts()
f_neg_profs = f_neg['sample_original_sampleid'].value_counts()

t_neg_profs = t_neg['sample_original_sampleid'].value_counts()
f_pos_profs = f_pos['sample_original_sampleid'].value_counts()

# make the original validation data by combining outputs
copes_val = t_neg.append(f_pos)
egg_val = t_pos.append(f_neg)

# plots by length
fig, ax = plt.subplots()
egg_val['object_length_mm'].transform('log').hist(bins=30, color='k', alpha=0.6, ax=ax)
t_pos['object_length_mm'].transform('log').hist(bins=30, color='b', alpha=0.6, ax=ax)
f_neg['object_length_mm'].transform('log').hist(bins=30, color='r', alpha=0.6, ax=ax)
ax.grid(False)
ax.legend(['whole val set', 'true positives', 'false negatives'])
ax.set_xlabel('log(mm)')
ax.set_ylabel('counts')
#ax.set_title('Size dist. egg output ResNet-18 trained split by profile (17/2/21)')
ax.set_title('Size dist. egg output ResNet-18 trained split randomly (17/2/21)')

fig1, ax1 = plt.subplots()
copes_val['object_length_mm'].transform('log').hist(bins=30, color='m', alpha=0.6, ax=ax1)
t_neg['object_length_mm'].transform('log').hist(bins=30, color='y', alpha=0.6, ax=ax1)
f_pos['object_length_mm'].transform('log').hist(bins=30, color='g', alpha=0.6, ax=ax1)
ax1.grid(False)
ax1.legend(['whole val set', 'true negative', 'false positive'])
ax1.set_xlabel('log(mm)')
ax1.set_ylabel('counts')
#ax1.set_title('Size dist. copepods ResNet-18 trained split by profile (17/2/21)')
ax1.set_title('Size dist. copepods ResNet-18 trained split randomly (17/2/21)')

# plots by latitude band
bounds = np.arange(-90, 110, 20)
fig2, ax2 = plt.subplots()
pd.cut(egg_val['object_lat'], bounds).value_counts().sort_index()\
    .plot.bar(ax=ax2, color='k', alpha=0.6, rot=45)
pd.cut(t_pos['object_lat'], bounds).value_counts().sort_index()\
    .plot.bar(ax=ax2, color='b', alpha=0.6, rot=45)
pd.cut(f_neg['object_lat'], bounds).value_counts().sort_index()\
    .plot.bar(ax=ax2, color='r', alpha=0.6, rot=45)
ax2.grid(False)
ax2.legend(['whole val set', 'true positives', 'false negatives'])
ax2.set_xlabel('latitude bands')
ax2.set_ylabel('counts')
#ax2.set_title('Lat. dist. eggs ResNet-18 split by profile (17/2/21)')
ax2.set_title('Lat. dist. eggs ResNet-18 split randomly (17/2/21)')

bounds = np.arange(-90, 110, 20)
fig3, ax3 = plt.subplots()
pd.cut(copes_val['object_lat'], bounds).value_counts().sort_index()\
    .plot.bar(ax=ax3, color='m', alpha=0.6, rot=45)
pd.cut(t_neg['object_lat'], bounds).value_counts().sort_index()\
    .plot.bar(ax=ax3, color='y', alpha=0.6, rot=45)
pd.cut(f_pos['object_lat'], bounds).value_counts().sort_index()\
    .plot.bar(ax=ax3, color='g', alpha=0.6, rot=45)
ax3.grid(False)
ax3.legend(['whole val set', 'true positives', 'false negatives'])
ax3.set_xlabel('latitude bands')
ax3.set_ylabel('counts')
#ax3.set_title('Lat. dist. copepods ResNet-18 trained split by profile (17/2/21)')
ax3.set_title('Lat. dist. copepods ResNet-18 trained split randomly (17/2/21)')
