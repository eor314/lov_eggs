import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.axes_divider import make_axes_area_auto_adjustable
import numpy as np

# import data from the tsv file
#copes = pd.read_table(r'D:\LOV\export_3068_20210122_1540\ecotaxa_export_3068_20210122_1540.tsv', header=0)
copes = pd.read_table('/Users/eorenstein/Documents/eggs-data/all_copepoda.tsv', header=0)

# find the unique project names and number of associate entries
uniq_copes = copes['sample_original_projname'].value_counts()

# get the average lat and lon of the samples for each project
lat_lon = copes.groupby('sample_original_projname').agg({'object_lat': ['mean'], 'object_lon': ['mean']})

fig1, ax1 = plt.subplots()
uniq_copes.plot(kind='barh', ax=ax1)
make_axes_area_auto_adjustable(ax1)
ax1.set_title('All Copepods (mean lat, mean long)')
ax1.set_ylabel('Project Name')
ax1.set_xlabel('# Copepods')

for ii, item in enumerate(uniq_copes.iteritems()):
    lat = lat_lon.loc[item[0]]['object_lat']['mean']
    lon = lat_lon.loc[item[0]]['object_lon']['mean']
    ax1.text(item[1]+3, ii+0.25, f'({np.round(lat,2)}, {np.round(lon,2)})',
             color='blue', fontweight='bold')

# Do the same for the eggs
eggs = pd.read_table('/Users/eorenstein/Documents/eggs-data/all_eggs.tsv', header=0)

# find the unique project names and number of associate entries
uniq_eggs = eggs['sample_original_projname'].value_counts()

# get the average lat and lon of the samples for each project
lat_lon = eggs.groupby('sample_original_projname').agg({'object_lat': ['mean'], 'object_lon': ['mean']})

fig1, ax1 = plt.subplots()
uniq_eggs.plot(kind='barh', ax=ax1, color='m')
make_axes_area_auto_adjustable(ax1)
ax1.set_title('All Eggs (mean lat, mean long)')
ax1.set_ylabel('Project Name')
ax1.set_xlabel('# Copepods')

for ii, item in enumerate(uniq_eggs.iteritems()):
    lat = lat_lon.loc[item[0]]['object_lat']['mean']
    lon = lat_lon.loc[item[0]]['object_lon']['mean']
    ax1.text(item[1]+3, ii+0.25, f'({np.round(lat,2)}, {np.round(lon,2)})',
             color='purple', fontweight='bold')

# look at the amount of eggs v. non-eggs for each cruise
pair_counts = pd.DataFrame(columns=['eggs', 'copes'], index=uniq_eggs.index)
for ii in uniq_eggs.index:
    pair_counts.loc[ii]['eggs'] = uniq_eggs[ii]
    pair_counts.loc[ii]['copes'] = uniq_copes[ii]

pair_counts['total'] = pair_counts.loc[:,['eggs','copes']].sum(axis=1)
pair_counts['% eggs'] = pair_counts['eggs']/pair_counts['total']
pair_counts['% copes'] = pair_counts['copes']/pair_counts['total']

# all together
fig, axs = plt.subplots(1, 2)
wd = 0.4
labs = pair_counts.index.tolist()
labs = [line.split('(')[0] for line in labs]

tmp = axs.tolist()
tmp.append(tmp[1].twinx())

bb1 = pair_counts.plot.bar(y=['copes', 'eggs'], color=['b', 'm'], ax=tmp[0], width=0.8, legend=False)
tmp[0].set_xticklabels(labs)
tmp[0].axis('tight')

bb2 = pair_counts.plot.bar(y='copes', ax=tmp[1], width=wd, color='b', position=1, legend=False)
bb3 = pair_counts.plot.bar(y='eggs', ax=tmp[2], width=wd, color='m', position=0, legend=False)
tmp[1].set_ylabel('copes')
tmp[2].set_ylabel('eggs')
tmp[1].set_xticklabels(labs)

plt.axis('tight')
plt.subplots_adjust(bottom=0.25)
plt.suptitle('Eggs v Copes')
fig.legend([bb2, bb3], labels=['copes', 'eggs'], loc='upper right', borderaxespad=0.05)

# area distribution
fig, ax = plt.subplots()
ax2 = ax.twinx()
bb1 = copes['object_area'].transform('log').hist(bins=30, color='b', alpha=0.6, ax=ax)
bb2 = eggs['object_area'].transform('log').hist(bins=30, color='m', alpha=0.6, ax=ax2)
ax.grid(False)
ax2.grid(False)
ax.set_ylabel('Copepod counts')
ax2.set_ylabel('Egg counts')
ax.set_xlabel('log(pixels)')
fig.legend([bb1, bb2], labels=['copes', 'eggs'], loc='lower left', bbox_to_anchor=(0.73, 0.75))
fig.suptitle('Area distribution')

# Major axis distribution
fig, ax = plt.subplots()
ax2 = ax.twinx()
bb1 = copes['object_major'].transform('log').hist(bins=30, color='b', alpha=0.6, ax=ax)
bb2 = eggs['object_major'].transform('log').hist(bins=30, color='m', alpha=0.6, ax=ax2)
ax.grid(False)
ax2.grid(False)
ax.set_ylabel('Copepod counts')
ax2.set_ylabel('Egg counts')
ax.set_xlabel('log(pixels)')
fig.legend([bb1, bb2], labels=['copes', 'eggs'], loc='lower left', bbox_to_anchor=(0.73, 0.75))
fig.suptitle('Major axis distribution')

fig, ax = plt.subplots()
ax2 = ax.twinx()
bb1 = copes[copes['sample_original_projname'] == 'UVP5 GREEN EDGE Ice Camp 2015']\
    ['object_major'].transform('log').hist(bins=30, color='b', alpha=0.6, ax=ax)
bb2 = eggs[eggs['sample_original_projname'] == 'UVP5 GREEN EDGE Ice Camp 2015']\
    ['object_major'].transform('log').hist(bins=30, color='m', alpha=0.6, ax=ax2)
ax.grid(False)
ax2.grid(False)
ax.set_ylabel('Copepod counts')
ax2.set_ylabel('Egg counts')
ax.set_xlabel('log(pixels)')
fig.legend([bb1, bb2], labels=['copes', 'eggs'], loc='lower left', bbox_to_anchor=(0.73, 0.75))
fig.suptitle('Major axis distribution from Green Edge Ice Camp 2015')

fig, ax = plt.subplots()
ax2 = ax.twinx()
bb1 = copes[copes['sample_original_projname'] == 'UVP5hd msm060 (2017)']\
    ['object_major'].transform('log').hist(bins=30, color='b', alpha=0.6, ax=ax)
bb2 = eggs[eggs['sample_original_projname'] == 'UVP5hd msm060 (2017)']\
    ['object_major'].transform('log').hist(bins=30, color='m', alpha=0.6, ax=ax2)
ax.grid(False)
ax2.grid(False)
ax.set_ylabel('Copepod counts')
ax2.set_ylabel('Egg counts')
ax.set_xlabel('log(pixels)')
fig.legend([bb1, bb2], labels=['copes', 'eggs'], loc='lower left', bbox_to_anchor=(0.73, 0.75))
fig.suptitle('Major axis distribution from UVP5hd msm060 (2017)')