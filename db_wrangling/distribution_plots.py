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

# get the average lat and lon of the samples for each project
lat_lon = copes.groupby('sample_original_projname').agg({'object_lat': ['mean'], 'object_lon': ['mean']})
lat_lon = eggs.groupby('sample_original_projname').agg({'object_lat': ['mean'], 'object_lon': ['mean']})

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

## area distribution
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

## Major axis distribution
fig, ax = plt.subplots()
ax2 = ax.twinx()
bb1 = copes['object_length_mm'].transform('log').hist(bins=30, color='b', alpha=0.6, ax=ax)
bb2 = eggs['object_length_mm'].transform('log').hist(bins=30, color='m', alpha=0.6, ax=ax2)
ax.grid(False)
ax2.grid(False)
ax.set_ylabel('Copepod counts')
ax2.set_ylabel('Egg counts')
ax.set_xlabel('log(mm)')
fig.legend([bb1, bb2], labels=['copes', 'eggs'], loc='lower left', bbox_to_anchor=(0.73, 0.75))
fig.suptitle('Major axis distribution')

## major axis distribution for three cruises
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

## major axis distribution by latitude bands
bounds = np.arange(-90, 110, 20)
outptf = r'D:\LOV\size_dist_plots'

for ii, val in enumerate(bounds):
    fig, ax = plt.subplots()
    ax2 = ax.twinx()
    bb1 = copes_match[(val <= copes_match['object_lat']) & (copes_match['object_lat'] < bounds[ii+1])]\
        ['object_major'].transform('log').hist(bins=30, color='b', alpha=0.6, ax=ax)
    bb2 = eggs[(val <= eggs['object_lat']) & (eggs['object_lat'] < bounds[ii+1])]\
        ['object_major'].transform('log').hist(bins=30, color='m', alpha=0.6, ax=ax2)
    ax.grid(False)
    ax2.grid(False)
    ax.set_ylabel('Copepod counts')
    ax2.set_ylabel('Egg counts')
    ax.set_xlabel('log(pixels)')
    fig.legend([bb1, bb2], labels=['copes', 'eggs'], loc='lower left', bbox_to_anchor=(0.73, 0.75))
    fig.suptitle(f'Major axis distribution between {val} and {bounds[ii+1]}')

    outfile = os.path.join(outptf, f'band-{val}-{bounds[ii+1]}.png')
    fig.savefig(outfile)

## proportion of eggs to copepods in latitude bands
eggs_lat = pd.cut(eggs['object_lat'], bounds).value_counts().sort_index()
copes_lat = pd.cut(copes_match['object_lat'], bounds).value_counts().sort_index()
comp = eggs_lat / copes_lat
ax = comp.plot.bar(rot=45)
ax.set_xlabel('lat bands')
ax.set_ylabel('# eggs/# copes')
ax.set_title('proportion of eggs by latitude band')

## lat bands in mm
bounds = np.arange(-90, 110, 20)
outptf = r'D:\LOV\size_dist_plots'

for ii, val in enumerate(bounds):
    fig, ax = plt.subplots()
    ax2 = ax.twinx()
    bb1 = copes_match[(val <= copes_match['object_lat']) & (copes_match['object_lat'] < bounds[ii+1])]\
        ['object_length_mm'].transform('log').hist(bins=30, color='b', alpha=0.6, ax=ax)
    bb2 = eggs[(val <= eggs['object_lat']) & (eggs['object_lat'] < bounds[ii+1])]\
        ['object_length_mm'].transform('log').hist(bins=30, color='m', alpha=0.6, ax=ax2)
    ax.grid(False)
    ax2.grid(False)
    ax.set_xlim(-2.5, 1)
    ax.set_ylabel('Copepod counts')
    ax2.set_ylabel('Egg counts')
    ax.set_xlabel('log(mm)')
    fig.legend([bb1, bb2], labels=['copes', 'eggs'], loc='lower left', bbox_to_anchor=(0.73, 0.75))
    fig.suptitle(f'Major axis distribution between {val} and {bounds[ii+1]}')

    outfile = os.path.join(outptf, f'mm-band-{val}-{bounds[ii+1]}.png')
    fig.savefig(outfile)