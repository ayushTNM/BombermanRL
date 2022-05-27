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

from agent import Player, PrioritizedSweepingAgent, Random      # implementations

fix_dirs()

def main():
    # main_menu = menu_config()
    # menu_loop(main_menu)
    game = Game(GRID_SIZE, BOMB_RANGE, CRATE_CHANCE, WALL_CHANCE, REPETITIONS, EPISODES, MAX_N_CRATES,
                HYPERPARAMS, TILE_SIZE, IMAGES, OUTPUT)

    game.set_alg(None,PrioritizedSweepingAgent)
    game.set_render(None,False)
    game.set_render_best(None,True)
    game.set_bomb_limit(None,1)
    game.main()

# ------------- #
#   CONSTANTS   #
# ------------- #

# parsed
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
args = ParseWrapper(parser)()
DIMENSIONS, BOMB_RANGE, MAX_N_CRATES = args[0], args[1], args[2]
CRATE_CHANCE, WALL_CHANCE = args[3],args[4]
REPETITIONS, EPISODES = args[5], args[6]
HYPERPARAMS = {"alpha": args[7],"gamma": args[8],"epsilon": args[9],"n_planning_updates": args[10]}
OUTPUT = args[11] + str(args[0])

WIDTH = HEIGHT = DIMENSIONS                              # world dimensions (excluding border walls)
GRID_SIZE = np.array([WIDTH+2, HEIGHT+2], dtype=int)     # np.ndarray for math operations

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
IMAGES: list[str] = sorted(glob.glob(os.path.join('..','assets','sprites','**','*.png'))) # load in image files

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
    game = Game(GRID_SIZE, BOMB_RANGE, CRATE_CHANCE, WALL_CHANCE, REPETITIONS, EPISODES, MAX_N_CRATES,
                HYPERPARAMS, TILE_SIZE, IMAGES, OUTPUT)

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
    character = [('Prioritized Sweeping Agent', PrioritizedSweepingAgent),
             ('Player', Player),
             ('Random', Random)]
    render = [('No', False),
            ('Yes', True)]
    render_best = [('Yes', True),
                    ('No', False)]
    bomb_limit = [(str(i),i) for i in range(1,np.sum(GRID_SIZE-2)+1)]

    game.set_alg(None,character[0][1])
    game.set_render(None,render[0][1])
    game.set_render_best(None,render_best[0][1])
    game.set_bomb_limit(None,bomb_limit[0][1])

    play_options.add.selector('Character',
            character,
            onchange = game.set_alg)
    play_options.add.selector('Render (Agent Only)',
            render,
            onchange = game.set_render)
    play_options.add.selector('Render Best (Agent Only)',
            render_best,
            onchange = game.set_render_best)
    play_options.add.selector('Bomb_limit (Player/Random)',
            bomb_limit,
            onchange = game.set_bomb_limit)
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
