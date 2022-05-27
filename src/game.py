# python standard library
import time                     # timing episode runs
from datetime import datetime   # displaying experiment start time
from typing import Any          # type hinting
# dependencies
import numpy as np              # arrays, math
import pygame                   # rendering, human interaction
# local imports
from environment import Environment                 # obtaining rewards for agent
from agent import Agent                             # type hinting
from helper import DataManager, ProgressBar         # storing arrays, progress visualization
from plot import plot_results                       # final results plotting

BACKGROUND = (107, 142, 35)     # moss green

class Game:
    def __init__(self, grid_size: np.ndarray, bomb_range: int, crate_chance: int,wall_chance: int,
                n_repetitions: int, n_episodes: int, max_n_crates: int, hyperparams,
                tile_size: int, images: list[str], output: str = 'plot'):

        self.grid_size = grid_size
        self.tile_size = tile_size
        self.load_images(images)
        self.wall_chance = wall_chance/100
        self.crate_chance = crate_chance/100
        self.n_repetitions = n_repetitions
        self.n_episodes = n_episodes
        self.max_n_crates = max_n_crates
        self.params = {"bomb_range":bomb_range,"step":1,"death":0}
        self.hyperparams = hyperparams
        self.output_name = output

        # these can be modified from pygame menu or CLI arguments
        self.RL = True
        self.wait_bg = False
        self.agent = None
        self.stats = []

        pygame.font.init()
        self.font = pygame.font.SysFont('Bebas', 100)
        self.display = pygame.display.set_mode(self.grid_size * self.tile_size)
        pygame.display.set_caption('Bomberman')
        self.clock = pygame.time.Clock()

        # define announcements
        self.winSurface = self.font.render('Win', False, (0, 0, 0))
        self.loseSurface = self.font.render('Lose', False, (0, 0, 0))
        self.waitSurface = self.font.render('Training Agent', False, (0, 0, 0))

    def load_images(self, images: list[str]) -> None:
        """Loads all images in list :param images: to attribute self.loadedImgs"""
        self.loadedImgs= {}
        for img in images:
            imgName=img.replace('\\','/').split('/')
            if (folder:=imgName[-2]) not in self.loadedImgs.keys():
                self.loadedImgs.update({folder:{}})
            loadedImg: pygame.Surface = pygame.image.load(img)
            scaledImg: pygame.Surface = pygame.transform.scale(loadedImg, (self.tile_size, self.tile_size))
            self.loadedImgs[folder].update({imgName[-1].split('.')[-2]:scaledImg})

    def set_alg(self, _, c: str): 
        self.alg=c
        self.RL = True if c.__name__ == 'PrioritizedSweepingAgent' else False   # called from pygame menu
    def set_render(self, _, c: bool): self.render = c                           # called from pygame menu
    def set_render_best(self, _, c: bool): self.render_best = c                 # called from pygame menu
    def set_bomb_limit(self, _, c: bool): self.params.update({"bomb_limit":c})  # called from pygame menu

    def draw(self):
        """Renders a frame on pygame window"""
        if self.render or not self.RL or self.wait_bg:
            self.display.fill(BACKGROUND)
            self.env.render(self.loadedImgs, self.tile_size, self.display)

            if self.agent.alive:
                self.display.blit(self.agent.animation[self.agent.direction][self.agent.frame],
                                  (self.agent.x * (self.tile_size / self.agent.step),
                                   self.agent.y * (self.tile_size / self.agent.step),
                                   self.tile_size, self.tile_size))
            if self.wait_bg:
                font_w = self.waitSurface.get_width()
                font_h = self.waitSurface.get_height()
                self.display.blit(self.waitSurface,
                                  (self.display.get_width() // 2 - font_w//2,
                                   self.display.get_height() // 2 - font_h//2))
                self.wait_bg = False

            if self.stats:
                pygame.draw.rect(self.display, (200,200,200), pygame.Rect(self.display.get_width()//2-180, 5, 360, 85))
                for idx, statSurface in enumerate(self.stats):
                    self.display.blit(statSurface, (self.display.get_width() // 2 - statSurface.get_width() // 2, 10 + 25*idx))
            pygame.display.update()

    def replay_best(self, actions: list[int], r: int) -> None:
        """
        After an agent has trained for a number of episodes,
        this function can be used to render the best sequence of actions it has found
        """
        temp_render,temp_fps = self.render, self.env.fps

        statFont = pygame.font.SysFont('Bebas', 40)
        statSurface1 = statFont.render(f'Best total reward found: {r}', False, (231,113,123))
        statSurface2 = statFont.render(f'Bombs placed: {(bp := actions.count(5))}', False, (247,240,226))
        statSurface3 = statFont.render(f'Steps moved: {len(actions)-bp}', False, (131,105,224))
        # self.stats = [statSurface1, statSurface2, statSurface3]

        self.env.fps = 5
        self.render = True
        self.env.reset(self.agent)
        self.draw()
        time.sleep(1)
        for action in actions:
            self.env.step(action, self.agent, self.draw)
            self.draw()
        self.game_over()

        self.env.fps,self.render = temp_fps,temp_render
        self.stats = []

    def main(self):

        if self.RL:
            vault = DataManager(dirname=self.output_name)
            start: float = time.perf_counter()              # <-- timer start
            print(f'\nStarting experiment at {datetime.now().strftime("%H:%M:%S")}')   

        for crate_count in np.arange(1, self.max_n_crates+1):   # train agent for each number of crates

            data = self.experiment_setup(crate_count)
            tic = datetime.now().time()

            for rep in range(self.n_repetitions):
                self.agent = self.alg((self.env.x, self.env.y), self.loadedImgs,**self.params)           # initialize Agent based on specific arguments
                
                for ep in range(self.n_episodes):
                    c_r, actions = self.playout()
                    
                    if self.RL: 
                        data['progress'](np.ravel_multi_index ((rep,ep),(self.n_repetitions,self.n_episodes)))
                        data['rewards'][rep,ep] = c_r

                        if c_r > data['best_c_r']:
                            data['best_c_r'], data['best_actions'] = c_r, actions

                    else:
                        self.game_over()
                        break
                else:               # if loop was not broken out of, i.e. agent = RL or random
                    continue        # move to next repetition
                break               # else, break out of "crate_count" loop and return to menu
            else:                   # if last episode has been reached (agent = RL or random)
                vault.save_array(data=data['rewards'], id=crate_count,tic=tic)
                if actions != None and self.render_best:
                    self.replay_best(data['best_actions'], data['best_c_r'])
                continue
            break

        if self.RL:
            end: float = time.perf_counter()                # <-- timer end
            minutes: int = int((end-start) // 60)
            seconds: float = round((end-start) % 60, 1)
            stringtime: str = f'{minutes}:{str(seconds).zfill(4)} min' if minutes else f'{seconds} sec'
            print(f'\nExperiment finished in {stringtime}\n')
            try: int(self.output_name)
            except ValueError: plot_results(self.output_name)

    def playout(self) -> tuple[int, list[int]]:
        """
        Does one playout of an episode
        ---
        Returns cumulative reward and list of actions taken
        """
        done: bool = False
        actions: list[int] = []
        c_r: int = 0
        s=None
        if self.RL: self.agent, s = self.env.reset(self.agent)
        self.draw()
        while self.agent.alive and 2 in self.env.grid:
            
            a = self.agent.select_action(s)
            actions.append(a)
            reward, next_state = self.env.step(a, self.agent, self.draw)

            if self.RL:
                done = not np.sum(self.env.grid == 2)
                self.agent.update(s, a, reward, next_state, done)
                s = next_state
                c_r += reward

        return c_r, actions

    def experiment_setup(self, crate_count: int) -> tuple[Agent, float, list[Any], list[pygame.Surface]]:
        """Very ugly function you do not want to interact with"""
        fps=0
        data = None
        if not self.RL:
            if self.alg.__name__ != "Random":
                fps=15
                self.params.update({"step":3,"death":1})
            self.env = Environment(*self.grid_size, self.wall_chance, self.crate_chance, fps=fps)
        else:
            data = {"rewards" : np.zeros(shape=(self.n_repetitions, self.n_episodes)),
                    "progress" : ProgressBar(self.n_repetitions*self.n_episodes, process_name=f'{crate_count} crates'),
                    "best_actions" : [],
                    "best_c_r" : float('-inf')}                # best run => least negative cumulative reward}
            self.wait_bg = not self.render
            self.env = Environment(*self.grid_size, self.wall_chance, crate_count=crate_count, seed=28041993)
            self.params.update(self.hyperparams | {"n_states":self.env.n_states,"n_actions":self.env.n_actions})

        return data

    def game_over(self):
        self.env.update_bombs(self.draw)
        self.draw()
        if not np.sum(self.env.grid==2):
            font_w = self.winSurface.get_width()
            font_h = self.winSurface.get_height()
            self.display.blit(self.winSurface, (self.display.get_width() // 2 - font_w//2,  self.display.get_height() // 2 - font_h//2))
            pygame.display.update()
            time.sleep(2)
        else:
            font_w = self.loseSurface.get_width()
            font_h = self.loseSurface.get_height()
            self.display.blit(self.loseSurface, (self.display.get_width() // 2 - font_w//2, self.display.get_height() // 2 - font_h//2))
            pygame.display.update()
            time.sleep(2)
        self.draw()
