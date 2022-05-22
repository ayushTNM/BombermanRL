# python standard library
import time                 # timing episode runs
from typing import Any      # type hinting
# dependencies
import numpy as np          # arrays, math
import pygame               # rendering, human interaction
# local imports
from environment import Environment                             # obtaining rewards for agent
from agent import Agent                                         # type hinting
from agent import Player, PrioritizedSweepingAgent, Random      # implementations

BACKGROUND = (107, 142, 35)     # moss green

class Game:
    def __init__(self, grid_size: np.ndarray, n_repetitions: int, n_episodes: int,
                 wall_chance: int, crate_chance: int, max_n_crates: int, 
                 alpha: float, gamma: float, epsilon: float, n_planning_updates: int,
                 tile_size: int, images: list[str]):

        self.grid_size = grid_size
        self.wall_chance = wall_chance / 100
        self.crate_chance = crate_chance / 100
        self.tile_size = tile_size
        self.load_images(images)
        self.n_repetitions = n_repetitions
        self.n_episodes = n_episodes
        self.max_n_crates = max_n_crates
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.n_planning_updates = n_planning_updates

        # these can be modified from pygame menu
        self.render = True
        self.alg = 'Player'

        self.agent = None
        self.wait_bg = False

        pygame.font.init()
        self.font = pygame.font.SysFont('Bebas', 100)
        self.display = pygame.display.set_mode(self.grid_size * self.tile_size)
        pygame.display.set_caption('Bomberman')
        self.clock = pygame.time.Clock()

        # define announcements
        self.winSurface = self.font.render('Win', False, (0, 0, 0))
        self.loseSurface = self.font.render('Lose', False, (0, 0, 0))
        self.waitSurface = self.font.render('Please Wait', False, (0, 0, 0))

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

    def set_alg(self, _, c: str): self.alg = c          # called from pygame menu
    def set_render(self, _, c: str): self.render = c    # called from pygame menu

    def draw(self):
        """Renders a frame on pygame window"""
        if self.render or self.alg == 'Player' or self.wait_bg:
            self.display.fill(BACKGROUND)
            self.env.render(self.loadedImgs, self.tile_size, self.display)

            if self.agent.alive:
                self.display.blit(self.agent.animation[self.agent.direction][self.agent.frame],
                    (self.agent.x * (self.tile_size / self.agent.step), self.agent.y * (self.tile_size / self.agent.step), self.tile_size, self.tile_size))
            if self.wait_bg:
                font_w = self.waitSurface.get_width()
                font_h = self.waitSurface.get_height()
                self.display.blit(self.waitSurface, (self.display.get_width() // 2 - font_w//2,  self.display.get_height() // 2 - font_h//2))
                self.wait_bg = False

            pygame.display.update()

    def render_best(self, actions: list[int], r: int) -> None:
        """
        After an agent has trained for a number of episodes,
        this function can be used to render the best sequence of actions it has found
        """
        backup_render = self.render
        self.render = True
        self.env.reset(self.agent)
        self.draw()
        time.sleep(1)
        print('least steps:',len(actions),'bombs:',sum(np.array(actions)==5),'r:',r)
        while len(actions)>0:
            self.clock.tick(15)
            dt = self.clock.get_fps()
            self.env.step(actions[0], self.agent, dt, self.draw)
            actions.pop(0)
            self.draw()
        self.game_over()
        self.render = backup_render

    def main(self):

        for crate_count in np.arange(1, self.max_n_crates+1):   # train agent for each number of crates
            self.wait_bg = 1 - self.render
            
            agent, self.fps, args, imgs = self.experiment_setup(crate_count)

            for _ in range(self.n_repetitions):
                self.agent = agent(*args)           # initialize Agent based on specific arguments
                self.agent.load_animations(imgs)
                
                best_actions = []
                best_c_r = float('-inf')            # best run => least negative cumulative reward

                for ep in range(self.n_episodes):
                    c_r, actions = self.playout()

                    if c_r > best_c_r and self.agent.type == 'PrioritizedSweepingAgent':
                        best_c_r, best_actions = c_r, actions

                    if self.agent.type == 'Player':
                        self.game_over()
                        break
                    elif self.agent.type in {'PrioritizedSweepingAgent', 'Random'}:     # can be replaced by else later on
                        print(f'episode: {ep}, number of actions: {len(actions)}, reward: {c_r}')
                else:               # if loop was not broken out of, i.e. agent = RL or random
                    print('Done')
                    continue        # move to next episode
                break               # else, break out of "crate_count" loop and return to menu
            else:                   # if last episode has been reach (agent = RL or random)
                if actions != None:
                    self.render_best(best_actions, best_c_r)
                continue
            break

    def playout(self) -> tuple[int, list[int]]:
        """
        Does one playout of an episode
        ---
        Returns cumulative reward and list of actions taken
        """
        done: bool = False
        actions: list[int] = []
        c_r: int = 0
        self.agent, s = self.env.reset(self.agent)
        self.draw()
        while self.agent.alive and 2 in self.env.grid:
            self.clock.tick(self.fps)
            dt = self.clock.get_fps()

            a = self.agent.select_action(s, self.epsilon)
            actions.append(a)
            reward, next_state = self.env.step(a, self.agent, dt, self.draw)
            
            if self.agent.type == 'PrioritizedSweepingAgent':
                done = len(np.unique(self.env.grid, return_counts=True)[1]) == 2
                self.agent.update(s, a, reward, next_state, done, self.n_planning_updates)
            s = next_state
            c_r += reward
        
        return c_r, actions

    def experiment_setup(self, crate_count: int) -> tuple[Agent, float, list[Any], list[pygame.Surface]]:
        """Very ugly function you do not want to interact with"""
        if self.alg == 'Player':
            self.env = Environment(*self.grid_size, self.wall_chance, self.crate_chance)
            while not 2 in self.env.grid:
                self.env = Environment(*self.grid_size, self.wall_chance, self.crate_chance)
        elif self.alg == 'PrioritizedSweepingAgent':
            self.env = Environment(*self.grid_size, self.wall_chance, crate_count=crate_count, seed=42)
        else:
            self.env = Environment(*self.grid_size, self.wall_chance, crate_count=crate_count)

        data = {
            'Player': [Player, 15, [(self.env.x, self.env.y)], self.loadedImgs['player']],
                
            'PrioritizedSweepingAgent':[PrioritizedSweepingAgent, 0, 
            [self.env.n_states, self.env.action_size(), self.alpha, self.gamma, (self.env.x,self.env.y)], self.loadedImgs['agent']],
                
            None:[Random, 0, [(self.env.x,self.env.y)], self.loadedImgs['agent']]
            }

        agent, self.fps, args, imgs = data[self.alg] # unpack data based on algorithm chosen
        return (agent, self.fps, args, imgs)

    def game_over(self):
        self.clock.tick(self.fps)
        dt = self.clock.get_fps()
        self.env.update_bombs(dt)
        _, counts = np.unique(self.env.grid, return_counts=True)
        self.draw()
        if len(counts) == 2:
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
