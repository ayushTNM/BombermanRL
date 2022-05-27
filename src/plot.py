# python standard library
import os           # directories
import re           # directories
import datetime     # adding runtimes to labels
import argparse     # getting data directory name
# dependencies
import numpy as np                          # arrays
import matplotlib.pyplot as plt             # plotting
from scipy.signal import savgol_filter      # smoothing plots

def main():
    """Usage
    ---
    output = name of folder in npz directory that contains your data
    
    the plot will be saved as "<output>_lc", where output is the same as specified above    
    
    make sure you're working from src, otherwise the npz dir will not be found
    """
    dirname = get_dirname().input
    plot_results(dirname)

def get_dirname() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str, help=f"name of npz subdirectory holding your data")
    return parser.parse_args()

def plot_results(output: str) -> None:
    part_one = 'Learning Curves'
    if (num := re.findall(r'\d+', output)):
        part_two = f' ({num[0]}x{num[0]})'
    else:
        part_two = ''
    plot = LearningCurvePlot(title = part_one+part_two)

    cwd = os.getcwd()
    filenames = sorted(os.listdir(os.path.join(cwd,'..','npz',output)))
    # filter out unusable files such as "icon?", ".DS_Store", ...
    npz_filenames = []
    for filename in filenames:
        if filename.endswith('.npz'): npz_filenames.append(filename)
    # create plot, one npz file at a time
    for idx, npz_filename in enumerate(npz_filenames):
        file = np.load(os.path.join(cwd,'..','npz',output,npz_filename))
        n_crates = int(npz_filename.split('_')[0])
        runtime = npz_filename.split('_')[1].split('.')[0]
        dt = datetime.datetime.strptime(runtime, "%H%M%S").time()
        raw_data = file[file.files[0]]
        data: np.array = np.average(raw_data, axis=0)
        label = f'{n_crates} crates, {dt}'
        plot.add_curve(data=data, color_index=idx, label=label)

    plot.save(filename=f'{output}_lc')

class LearningCurvePlot:
    # color cycle
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red',
              'tab:purple', 'tab:cyan', 'tab:pink', 'tab:olive']

    def __init__(self, title: str = 'placeholder') -> None:
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlabel('Episode')
        self.ax.set_ylabel('Cumulative reward')
        self.ax.set_title(title)

    def add_curve(self, data: np.ndarray, color_index: int = 0, label: str = None) -> None:
        """Adds a vector with results to the plot"""
        self.ax.plot(data, color=self.colors[color_index], alpha = 0.3)
        smoothing = data.shape[0]//10 + (1+ (data.shape[0]//10) % 2)
        self.ax.plot(savgol_filter(data, smoothing, 1), label=label, color=self.colors[color_index])
        
    def save(self, filename: str = 'placeholder') -> None:
        """Saves a figure to results directory with given name"""
        self.ax.legend()
        if os.path.exists(os.path.join('..','results',f'{filename}.png')):
            yn = '_'
            while yn.lower() not in 'yn':
                yn = input(f'File "\033[1m{filename.split(os.path.sep)[-1]}.png\033[0m" already exists.\nOverwrite? [y/n]: ')
            if yn.lower() == 'n':
                return
        self.fig.savefig(os.path.join('..','results',f'{filename}.png'), dpi=300)
        print(f'Figure {filename}.png saved successfully')


if __name__ == '__main__':
    main()
