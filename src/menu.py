"""
Bomberman RL
---
Script that should be called to run the experiment
---
For information on usage, just type `python3 menu.py -h` in your terminal
---
Authors: Ayush Kandhai, Josef Hamelink
Date: May 2022
"""

# python standard library
import os                       # directories
import glob                     # locating image files
import argparse                 # quicker experiment setup
# dependencies
import numpy as np              # arrays
import pygame, pygame_menu      # rendering, human interaction
# local imports
from parse import ParseWrapper  # outsourcing argument parsing
from helper import fix_dirs     # making directory system foolproof
from game import Game           # script for running the game

fix_dirs()

def main():
    main_menu = menu_config()
    menu_loop(main_menu)

# ------------- #
#   CONSTANTS   #
# ------------- #

# parsed
parser = argparse.ArgumentParser()
DIMENSIONS, MAX_N_CRATES, CRATE_CHANCE, WALL_CHANCE, REPETITIONS, EPISODES, AGENT, FAST, OVERWRITE = ParseWrapper(parser)()

# TODO add bomb range arg?

WIDTH = HEIGHT = DIMENSIONS                              # world dimensions (excluding border walls)
GRID_SIZE = np.array([WIDTH+2, HEIGHT+2], dtype=int)     # np.ndarray for math operations

# RL agent
ALPHA: float = 1.0              # learning rate (update rule)
GAMMA: float = .99              # discount rate (update rule)
EPSILON: float = 0.1            # exploration rate (action selection)
N_PLANNING_UPDATES: int = 10    # model-based reinforcement learning

# colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_BACKGROUND = (153, 153, 255)          # indigo
MENU_BACKGROUND_COLOR = (102, 102, 153)     # aegean
MENU_TITLE_COLOR = (51, 51, 255)            # cobalt

# pygame
FPS = 60.0
FONT_SIZE = 18
pygame.display.init()
INFO = pygame.display.Info()
TILE_SIZE = int((INFO.current_h*0.95) / GRID_SIZE[1])
WINDOW_SIZE = GRID_SIZE * TILE_SIZE
SURFACE = pygame.display.set_mode(WINDOW_SIZE)
IMAGES: list[str] = sorted(glob.glob(os.path.join('..','images','**','*.png'))) # load in image files

# ------------- #
#   functions   #
# ------------- #

def main_background():
    global SURFACE; SURFACE.fill(COLOR_BACKGROUND)

def menu_config() -> pygame_menu.Menu:
    pygame.init()
    menu_percentage = 0.9                       # % of window to use as menu
    pygame.display.set_caption('Bomberman')     # window bar caption

    # create the Game instance
    game = Game(GRID_SIZE, REPETITIONS, EPISODES,
                WALL_CHANCE, CRATE_CHANCE, MAX_N_CRATES,
                ALPHA, GAMMA, EPSILON, N_PLANNING_UPDATES,
                TILE_SIZE, IMAGES)

    if AGENT: game.set_alg('hello world', 'PrioritizedSweepingAgent')
    if FAST: game.set_render('bye rendering', False)
    if OVERWRITE: game.set_overwrite('just for fun', True)

    # menu GUI settings, inherited by play_menu, play_options and main_menu
    menu_theme = pygame_menu.themes.Theme(
        selection_color = COLOR_WHITE,
        widget_font = pygame_menu.font.FONT_BEBAS,
        title_font_size = FONT_SIZE,
        title_font_color = COLOR_BLACK,
        title_font = pygame_menu.font.FONT_BEBAS,
        widget_font_color = COLOR_BLACK,
        widget_font_size = int(FONT_SIZE * 0.9),
        background_color = MENU_BACKGROUND_COLOR,
        title_background_color = MENU_TITLE_COLOR,
        widget_font_shadow = False
    )

    play_menu = pygame_menu.Menu(
        theme = menu_theme,
        height = int(WINDOW_SIZE[1] * menu_percentage),
        width = int(WINDOW_SIZE[0] * menu_percentage),
        title = 'Play menu'
    )
    play_options = pygame_menu.Menu(
        theme = menu_theme,
        height = int(WINDOW_SIZE[1] * menu_percentage),
        width = int(WINDOW_SIZE[0] * menu_percentage),
        title = 'Options'
    )

    play_options.add.selector('Character 1',
            [('Player', 'Player'),
             ('Prioritized Sweeping Agent', 'PrioritizedSweepingAgent'),
             ('Random', None)],
            onchange = game.set_alg)
    play_options.add.selector('Render (Agent Only)',
            [('Yes', True),
             ('No', False)],
            onchange = game.set_render)
    play_options.add.button('Back',
            pygame_menu.events.BACK)

    play_menu.add.button('Start', game.main)
    play_menu.add.button('Options', play_options)
    play_menu.add.button('Return  to  main  menu', pygame_menu.events.BACK)

    # create the main Menu instance that contains all information
    main_menu = pygame_menu.Menu(
        theme = menu_theme,
        height = int(WINDOW_SIZE[1] * menu_percentage),
        width = int(WINDOW_SIZE[0] * menu_percentage),
        title = 'Main menu'
    )

    main_menu.add.button('Play', play_menu)
    main_menu.add.button('Quit', pygame_menu.events.EXIT)
    
    return main_menu

def menu_loop(main_menu: pygame_menu.Menu) -> None:
    clock = pygame.time.Clock()
    
    while True:
        clock.tick(FPS)
        main_background()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: exit()

        main_menu.mainloop(SURFACE, main_background, disable_loop=False, fps_limit=0)
        main_menu.update(events)
        main_menu.draw(SURFACE)
        pygame.display.flip()

if __name__ == '__main__':
    main()
