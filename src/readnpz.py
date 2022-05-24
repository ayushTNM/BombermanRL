import os
import datetime
import numpy as np
from helper import LearningCurvePlot

dirname = 'plot6'
cwd = os.getcwd()

plot = LearningCurvePlot(title=f'Learning Curves {dirname[-1]}x{dirname[-1]}', filename=f'{dirname}_final', save_data=False)

filenames = sorted(os.listdir(os.path.join(cwd,'..','npz',dirname)))
# filter out unusable files such as "icon?", ".DS_Store", ...
npz_filenames = []
for filename in filenames:
    if filename.endswith('.npz'): npz_filenames.append(filename)
# create plot, one npz file at a time
for idx, npz_filename in enumerate(npz_filenames):
    file = np.load(os.path.join(cwd,'..','npz',dirname,npz_filename))
    n_crates = int(npz_filename.split('_')[0])
    runtime = npz_filename.split('_')[1].split('.')[0]
    dt = datetime.datetime.strptime(runtime, "%H%M%S").time()
    data = file[file.files[0]]
    label = f'{n_crates} crates, {dt}'
    plot.add_curve(data=data, color_index=idx, label=label)

plot.save()
