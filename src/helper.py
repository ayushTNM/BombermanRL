# python standard library
import os
import sys
import re   
from collections import Counter, OrderedDict    # data processing
# dependencies
import numpy as np                              # arrays, math
import matplotlib.pyplot as plt                 # plotting
from scipy.signal import savgol_filter          # smoothing plots

def fix_dirs() -> None:
    """Changes cwd to src, and creates a results dir on the same level if not already present"""
    cwd = os.getcwd()
    if cwd.split(os.sep)[-1] != 'src':
        if not os.path.exists(os.path.join(cwd, 'src')):
            raise FileNotFoundError('Please work from either the parent directory "BombermanRL",',
                                    'or from "src" in order to run any files that are in "src".')
        os.chdir(os.path.join(cwd, 'src'))
        cwd = os.getcwd()
        caller = re.search(r'src(.*?).py', str(sys._getframe(1))).group(1)[1:] + '.py'
        print(f'\n WARNING: Working directory changed to "{cwd}".',
              f'Consider running "{caller}" from "src" dir next time.')
    if not os.path.exists(results_dir := os.path.join(cwd, '..', 'results')):
        os.mkdir(results_dir)

class ProgressBar:
    frames = [f'\033[32m\033[1m{s}\033[0m' for s in ['╀', '╄', '┾', '╆', '╁', '╅', '┽', '╃']]   # spinner frames
    done_char = '\033[32m\033[1m━\033[0m'   # green bold ━, reset after
    todo_char = '\033[31m\033[2m─\033[0m'   # red faint ─, reset after
    spin_frame = 0

    def __init__(self, n_iters: int, process_name: str = 'placeholder') -> None:
        self.n_iters = n_iters
        print(f'Running {n_iters} repetitions for {process_name}...')
        print('\r' + 50 * self.todo_char + ' ' + self.frames[0] + ' 0%', end='')

    def __call__(self, iteration: int) -> None:
        """Updates and displays a progress bar on the command line"""
        percentage = 100 * (iteration+1) // self.n_iters    # floored percentage
        if percentage != 0 and percentage == 100 * iteration // self.n_iters: return
        steps = 50 * (iteration+1) // self.n_iters          # chars representing progress
        self.spin_frame += 1

        spin_char = self.frames[self.spin_frame%8]
        bar = (steps)*self.done_char + (50-steps)*self.todo_char        # the actual bar
        
        if iteration+1 == self.n_iters: suffix = ' complete\n'
        else: suffix = ' ' + spin_char + ' ' + str(percentage) + '% '	# spinner and percentage
        
        print('\r' + bar + suffix, end='')
        return

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
        
    def save(self, name: str = 'placeholder') -> None:
        """Saves a figure to results directory with given name"""
        self.ax.legend()
        if os.path.exists(os.path.join('..','results',f'{name}.png')):
            yn = '_'
            while yn.lower() not in 'yn':
                yn = input(f'File "\033[1m{name.split(os.path.sep)[-1]}.png\033[0m" already exists.\nOverwrite? [y/n]: ')
            if yn.lower() == 'y':
                self.fig.savefig(os.path.join('..','results',f'{name}.png'), dpi=300)
                print(f'Figure {name}.png saved successfully')
        else:
            self.fig.savefig(os.path.join('..','results',f'{name}.png'), dpi=300)
            print(f'Figure {name}.png saved successfully')
        exit()
