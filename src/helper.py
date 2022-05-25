# python standard library
import os, sys, re                      # directories
from datetime import datetime, date     # saving raw results
# dependencies
import numpy as np                              # arrays, math

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
    if not os.path.exists(npz_dir := os.path.join(cwd, '..', 'npz')):
        os.mkdir(npz_dir)

class ProgressBar:
    frames = [f'\033[32m\033[1m{s}\033[0m' for s in ['╀', '╄', '┾', '╆', '╁', '╅', '┽', '╃']]   # spinner frames
    done_char = '\033[32m\033[1m━\033[0m'   # green bold ━, reset after
    todo_char = '\033[31m\033[2m─\033[0m'   # red faint ─, reset after
    spin_frame = 0

    def __init__(self, n_iters: int, process_name: str = 'placeholder') -> None:
        self.n_iters = n_iters
        print(f'Training for {process_name}...')
        print('\r' + 50 * self.todo_char + ' ' + self.frames[0] + ' 0%', end='')

    def __call__(self, iteration: int) -> None:
        """Updates and displays a progress bar on the command line"""
        percentage = 100 * (iteration+1) // self.n_iters    # floored percentage
        if percentage == 100 * iteration // self.n_iters: return    # prevent printing same line multiple times
        steps = 50 * (iteration+1) // self.n_iters          # chars representing progress
        self.spin_frame += 1

        spin_char = self.frames[self.spin_frame%8]
        bar = (steps)*self.done_char + (50-steps)*self.todo_char        # the actual bar
        
        if iteration+1 == self.n_iters: suffix = ' complete\n'
        else: suffix = ' ' + spin_char + ' ' + str(percentage) + '% '	# spinner and percentage
        print('\r' + bar + suffix, end='')
        return

class DataManager:
    def __init__(self, dirname: str = '') -> None:
        self.tic = datetime.now().time()
        if not dirname:
            self.dirname = str(self.tic).split('.')[0].replace(':', '')
        else: self.dirname = dirname
        if not os.path.exists(data_dir := os.path.join(os.getcwd(),'..','npz', self.dirname)): os.mkdir(data_dir)
    
    def save_array(self, data: np.ndarray, id: int) -> None:
        toc = datetime.now().time()
        dt = datetime.combine(date.today(), toc) - datetime.combine(date.today(), self.tic)
        strtime = str(id) + '_0' + str(dt).split('.')[0].replace(':', '')
        np.savez(os.path.join('..','npz',self.dirname,f'{strtime}.npz'), array=data)
        self.tic = toc
