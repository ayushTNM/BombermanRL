"""
Memory
---
This script produces plots visualizing the memory consumption of arrays used by the PS agent
depending on environment dimensions and the number of crates in said environment
---
Author: Josef Hamelink
---
Date: May 2022
"""

# python standard library
import os                                       # directories
# dependencies
import numpy as np                              # arrays
import matplotlib as mpl                        # text formatting
import matplotlib.pyplot as plt                 # figure
import mpl_toolkits.axes_grid1 as axes_grid1    # grid subplot
# local imports
from helper import fix_dirs                     # directories

def main():
    
    global dim_range, cc_range, ldr, lcr

    dim_range = range(5, 11)   	# range of dimensions we want to plot: 5-10
    cc_range = range(4, 11)    	# range of crate counts we want to plot: 4-10
    ldr  = len(dim_range)
    lcr = len(cc_range)

    Q_res = np.zeros(shape=(ldr, lcr))
    N_res = np.zeros(shape=(ldr, lcr))

    for i, dim in enumerate(dim_range):
        for j, cc in enumerate(cc_range):
            Q_res[i,j] = Q_array_memory(dim, cc)
            N_res[i,j] = N_array_memory(dim, cc)
    
    fig = plt.figure()
    plt.rcParams.update({'font.size': 8})

    grid = axes_grid1.AxesGrid(fig, 111, nrows_ncols=(1, 2), axes_pad = 0.3, cbar_location = "bottom",
                            cbar_mode="each", cbar_size="10%", cbar_pad="5%")

    add_subplot(grid, Q_res, 0, 'Q Table (memory in MB)')
    add_subplot(grid, N_res, 1, 'N Table (memory in GB)')

    fix_dirs()
    plt.savefig(os.path.join(os.getcwd(),'..','results','memory.png'), bbox_inches='tight', dpi=200)


def Q_array_memory(dim: int, cc: int) -> float:
    """Calculates the chunk of memory needed to hold the Q-values based on dimension and crate count (MB)"""
    n_states = (dim+2)**2 * 2**cc
    n_actions = 6
    n_slots = n_states * n_actions
    n_bytes = 8 * n_slots  	# default float contains 64 bits (8 bytes)
    n_megabytes = n_bytes * 2**(-20)
    return round(n_megabytes, 1)

def N_array_memory(dim: int, cc: int) -> float:
    """Calculates the chunk of memory needed to hold the N-values based on dimension and crate count (GB)"""
    n_states = (dim+2)**2 * 2**cc
    n_actions = 6
    n_slots = n_states * n_actions * n_states
    n_bytes = 8 * n_slots  # default int contains 64 bits (8 bytes)
    n_gigabytes = n_bytes * 2**(-30)
    return round(n_gigabytes, 1)

def add_subplot(grid: axes_grid1.ImageGrid, res: np.ndarray, plot_idx: int, title: str) -> None:
    """Creates one subplot and adds it to the grid"""
    im = grid[plot_idx].imshow(res, cmap='viridis', interpolation='none')
    im.axes.xaxis.tick_top()
    im.axes.xaxis.set_label_position('top')
    im.axes.set_xticks(ticks=range(lcr), labels=cc_range)
    im.axes.set_yticks(ticks=range(ldr), labels=dim_range)
    im.axes.tick_params(axis='both', top=False, left=False)
    im.axes.set_xlabel('number of crates')
    im.axes.set_ylabel('world dimensions')
    im.axes.set_title(title)
    grid.cbar_axes[plot_idx].colorbar(im)

    textcolors = ('black', 'white')
    kw = {'fontsize': 6,
          'horizontalalignment': 'center',
          'verticalalignment': 'center'}

    threshold = im.norm(res.max())/2.0
    valfmt = mpl.ticker.StrMethodFormatter("{x:.1f}")

    for i in range(res.shape[0]):
        for j in range(res.shape[1]):
            kw.update(color=textcolors[int(im.norm(res[i, j]) < threshold)])
            im.axes.text(j, i, valfmt(res[i, j], None), **kw)


if __name__ == '__main__':
    main()
