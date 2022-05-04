import pygame
import pygame_menu
import numpy as np
import game
from algorithm import Algorithm

width=20
height=20
grid_size = np.array([width+2,height+2],dtype=int)
(wall_chance,box_chance) = (0.18,.32)
font_size = 18

color_background = (153, 153, 255)
color_black = (0, 0, 0)
color_white = (255, 255, 255)
fps = 60.0
menu_background_color = (102, 102, 153)
menu_title_color = (51, 51, 255)

pygame.display.init()
pygame.display.set_mode((0,0),pygame.FULLSCREEN)
INFO = pygame.display.Info()

tile_size = int((INFO.current_h*0.9)/grid_size[1])
window_size = grid_size*tile_size

player_alg = Algorithm.PLAYER
# en1_alg = Algorithm.DIJKSTRA
# en2_alg = Algorithm.DFS
# en3_alg = Algorithm.DIJKSTRA
show_path = True
surface = pygame.display.set_mode(window_size)


def change_path(value, c):
    global show_path
    show_path = c


def change_player(value, c):
    print(value,c)
    global player_alg
    player_alg = c


# def change_enemy1(value, c):
#     global en1_alg
#     en1_alg = c


# def change_enemy2(value, c):
#     global en2_alg
#     en2_alg = c


# def change_enemy3(value, c):
#     global en3_alg
#     en3_alg = c

def main_background():
    global surface
    surface.fill(color_background)


def menu_loop():
    pygame.init()

    menu_percentage = 0.9  #percentage of window to use as Menu
    Game = game.game(grid_size, box_chance, wall_chance, tile_size)

    pygame.display.set_caption('Bomberman')
    clock = pygame.time.Clock()

    menu_theme = pygame_menu.themes.Theme(
        selection_color=color_white,
        widget_font=pygame_menu.font.FONT_BEBAS,
        title_font_size=font_size,
        title_font_color=color_black,
        title_font=pygame_menu.font.FONT_BEBAS,
        widget_font_color=color_black,
        widget_font_size=int(font_size*0.9),
        background_color=menu_background_color,
        title_background_color=menu_title_color,
        widget_font_shadow=False
    )

    play_menu = pygame_menu.Menu(
        theme=menu_theme,
        height=int(window_size[1] * menu_percentage),
        width=int(window_size[0] * menu_percentage),
        title='Play menu'
    )

    play_options = pygame_menu.Menu(theme=menu_theme,
        height=int(window_size[1] * menu_percentage),
        width=int(window_size[0] * menu_percentage),
        title='Options'
    )
    play_options.add.selector("Character 1", [("Player", Algorithm.PLAYER), ("DFS", Algorithm.DFS),
                                              ("DIJKSTRA", Algorithm.DIJKSTRA), ("None", Algorithm.NONE)], onchange=Game.set_alg)
    # play_options.add.selector("Character 2", [("DIJKSTRA", Algorithm.DIJKSTRA), ("DFS", Algorithm.DFS),
    #                                           ("None", Algorithm.NONE)], onchange=change_enemy1)
    # play_options.add.selector("Character 3", [("DIJKSTRA", Algorithm.DIJKSTRA), ("DFS", Algorithm.DFS),
    #                                           ("None", Algorithm.NONE)], onchange=change_enemy2,  default=1)
    # play_options.add.selector("Character 4", [("DIJKSTRA", Algorithm.DIJKSTRA), ("DFS", Algorithm.DFS),
    #                                           ("None", Algorithm.NONE)], onchange=change_enemy3)
    play_options.add.selector("Show path", [("Yes", True), ("No", False)], onchange=Game.set_path)

    play_options.add.button('Back', pygame_menu.events.BACK)

    play_menu.add.button('Start',
                         Game.run)

    play_menu.add.button('Options', play_options)
    play_menu.add.button('Return  to  main  menu', pygame_menu.events.BACK)

    about_menu_theme = pygame_menu.themes.Theme(
        selection_color=color_white,
        widget_font=pygame_menu.font.FONT_BEBAS,
        title_font_size=font_size,
        title_font_color=color_black,
        title_font=pygame_menu.font.FONT_BEBAS,
        widget_font_color=color_black,
        widget_font_size=int(font_size*0.7),
        background_color=menu_background_color,
        title_background_color=menu_title_color,
        widget_font_shadow=False
    )

    about_menu = pygame_menu.Menu(theme=about_menu_theme,
        height=int(window_size[1] * menu_percentage),
        width=int(window_size[0] * menu_percentage),
        title='About'
    )
    about_menu.add.label("Player_controls: ")
    about_menu.add.label("Movement:_Arrows")
    about_menu.add.label("Plant bomb:_Space")
    about_menu.add.label("Author:_Michal_Sliwa")
    about_menu.add.label("Sprite: ")

    about_menu.add.label("https://opengameart.org/content")
    about_menu.add.label("/bomb-party-the-complete-set")

    main_menu = pygame_menu.Menu(
        theme=menu_theme,
        height=int(window_size[1] * menu_percentage),
        width=int(window_size[0] * menu_percentage),
        title='Main menu'
    )

    main_menu.add.button('Play', play_menu)
    main_menu.add.button('About', about_menu)
    main_menu.add.button('Quit', pygame_menu.events.EXIT)
    while True:

        clock.tick(fps)

        main_background()

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()

        main_menu.mainloop(surface, main_background, disable_loop=False, fps_limit=0)
        main_menu.update(events)
        main_menu.draw(surface)

        pygame.display.flip()


menu_loop()
