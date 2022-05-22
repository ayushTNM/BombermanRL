# python standard library
import os
import sys
import re   
from collections import Counter, OrderedDict    # data processing
# dependencies
import numpy as np                              # arrays, math
import matplotlib.pyplot as plt                 # plotting

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
    # spinner frames
    frames = ['╀', '╄', '┾', '╆', '╁', '╅', '┽', '╃']

    def __init__(self, n_iters: int, process_name: str = 'placeholder') -> None:
        self.n_iters = n_iters
        print(f'Running {n_iters} repetitions for {process_name}...')

    def __call__(self, iteration: int) -> None:
        """Updates and displays a progress bar on the command line"""
        percentage = 100 * (iteration+1) // self.n_iters    # floored percentage
        if percentage != 0 and percentage == 100 * iteration // self.n_iters: return
        steps = 50 * (iteration+1) // self.n_iters          # chars representing progress

        # green char, bold char, reset after
        format_done = lambda string: f'\033[32m\033[1m{string}\033[0m'
        # red char, faint char, reset after
        format_todo = lambda string: f'\033[31m\033[2m{string}\033[0m'
        done_char = format_done('━')
        todo_char = format_todo('─')

        spin_char = format_done(self.frames[percentage%8])
        bar = (steps)*done_char + (50-steps)*todo_char                  # the actual bar
        
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
        self.ax.plot(data, label=label, color=self.colors[color_index])
        self.ax.axhline(y=max(data), color=self.colors[color_index], linestyle=':', alpha=.3)
        
    def save(self, name: str = 'placeholder', overwrite: bool = False):
        """Saves a figure to results directory with given name"""
        self.ax.legend()
        if os.path.exists(os.path.join('..','results',f'{name}.png')) and not overwrite:
            yn = '_'
            while yn.lower() not in 'yn':
                yn = input(f'File "\033[1m{name.split(os.path.sep)[-1]}.png\033[0m" already exists.\nOverwrite? [y/n]: ')
            if yn.lower() == 'y':
                self.fig.savefig(os.path.join('..','results',f'{name}.png'), dpi=300)
                print('Figure saved successfully')
        else:
            self.fig.savefig(os.path.join('..','results',f'{name}.png'), dpi=300)
            print('Figure saved successfully')
