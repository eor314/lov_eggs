import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.axes_divider import make_axes_area_auto_adjustable
import numpy as np

# import data from the tsv file
copes = pd.read_table(r'D:\LOV\export_3068_20210122_1540\ecotaxa_export_3068_20210122_1540.tsv', header=0)

# find the unique project names and number of associate entries
uniq_proj = copes['sample_original_projname'].value_counts()

# get the average lat and lon of the samples for each project
lat_lon = copes.groupby('sample_original_projname').agg({'object_lat': ['mean'], 'object_lon': ['mean']})

fig1, ax1 = plt.subplots()
uniq_proj.plot(kind='barh', ax=ax1)
make_axes_area_auto_adjustable(ax1)
