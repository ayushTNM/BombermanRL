# python standard library
import sys                              # quitting pygame
from typing import Callable, Optional   # type hinting
# dependencies
import numpy as np                      # arrays, math
import pygame                           # rendering, human interaction
# local imports
from agent import Agent                 # type hinting

class Environment(object):
    
    def __init__(self, width: int, height: int, wall_chance: float, crate_chance: float = -1,
                fps: int = 0,crate_count: int = -1, seed: int = None):
        
        self.width = width
        self.height = height
        self.wall_chance = wall_chance
        self.crate_chance = crate_chance
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.shape = np.array([self.width, self.height])
        self.crate_count = crate_count
        self.bombs, self.explosions = [], []
        self.rng = np.random.default_rng(seed)
        self.generate()
        pass

    def to_state(self, location: tuple[int, int]) -> int:
        """Returns the current state of the agent represented as an integer"""
        location = tuple(np.array(location)-1)
        return np.ravel_multi_index((*location,*self.exploded_crates), (*self.shape-2,*[2 for _ in range(self.crate_count)]))

    def generate(self):
        """Generates the entire environment"""
        self.create_grid()
        self.find_start_location()

        mask = (np.arange(self.grid.shape[0])[np.newaxis,:]-self.y)**2 + (np.arange(self.grid.shape[1])[:,np.newaxis]-self.x)**2 >= 2**2
        mask = np.bitwise_and(self.reachable,mask,dtype=int)
        crate_idxs=np.array(list(zip(*np.where(mask == True))))
        if self.crate_chance == -1:
            self.crate_locs = crate_idxs[self.rng.choice(len(crate_idxs),self.crate_count,replace=False)]
            self.crate_chance = self.crate_count/np.sum(self.free_idxs)
        else:
            self.crate_locs = crate_idxs[self.rng.random(len(crate_idxs))< self.crate_chance]
            self.crate_count = len(self.crate_locs)
        self.grid[tuple([*self.crate_locs.T])] = 2

        self.backup_pos = (self.x,self.y)
        self.backup_grid = self.grid.copy()
        self.n_states = self.height * self.width * (2**self.crate_count)
        self.n_actions = len(self.possible_actions())

    def create_grid(self) -> None:
        """Creates a grid"""
        self.grid = np.zeros(tuple(self.shape),dtype=int)
        self.grid[:,[0,-1]] = self.grid[[0,-1]] = 1             # create walled borders
        self.grid[1:self.grid.shape[0]-1,1:self.grid.shape[1]-1] = self.rng.random(tuple(np.array(self.shape)-2)) < self.wall_chance
        self.free_idxs: list[tuple[int, int]] = list(zip(*np.where(self.grid==0)))     # legal starting positions

    def find_start_location(self) -> None:
        count: int = 0
        x, y = self.free_idxs[self.rng.integers(len(self.free_idxs))]
        self.find_reachable_spaces((x, y))
        while(np.sum(self.reachable) < np.sum(self.grid == 1) * (1-(self.wall_chance+.2))):
            count += 1
            if count == sum(self.shape):
                print("FAIL, NO SPACE FOR PLAYER")
                exit()
            elif count % max(self.shape-2)//4 == 0:
                self.create_grid()
            x, y = self.free_idxs[self.rng.integers(len(self.free_idxs))]
            self.find_reachable_spaces((x, y))
        self.x, self.y = x, y

    def step(self, action, agent, draw: Callable) -> tuple[int, Optional[int]]:
        r = -1                       # normal step penalty = -1
        r -= 1 * (action==5)         # bomb penalty = -10
        self.clock.tick(self.fps)
        self.dt = self.clock.get_fps()
        movement_actions = [(0,1), (1,0), (0,-1), (-1,0)]
        direction = agent.direction

        for e in pygame.event.get():
            if e.type == pygame.QUIT: 
                sys.exit(0)
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    sys.exit(0)
                if e.key == pygame.K_SPACE and agent.type == "Player" and agent.bomb_limit != 0:
                    action = 5

        if action < 4:
            direction = action
            if direction != agent.direction: agent.frame=0; agent.direction = direction
            agent.move(*movement_actions[action], self.grid)
        elif action > 4:
            if not agent.get_coords() in [b.pos for b in self.bombs]:
                temp_bomb = agent.plant_bomb(self.grid, self.dt)
                self.bombs.append(temp_bomb)
                self.grid[temp_bomb.pos] = 0        
        else:
            agent.frame = 0
        draw()
        r += 2 * self.update_bombs(draw)        # crate reward = +5
        if agent.type == "PrioritizedSweepingAgent":
            self.exploded_crates[self.grid[tuple([*self.crate_locs.T])] != 2] =1
            return r, self.to_state(agent.get_coords())
        else:
            return r, None    

    def reset(self, agent: Agent) -> tuple[Agent, int]:
        """
        Resets environment for next episode
        ---
        Returns the same agent object as was passed, but again at starting position
        """
        self.grid = self.backup_grid.copy()
        self.bombs, self.explosions = [], []
        self.exploded_crates = np.zeros((self.crate_count),dtype=int)
        agent.x, agent.y = np.array(self.backup_pos)*agent.step
        agent.alive = True
        return agent, self.to_state(agent.get_coords())

    def find_reachable_spaces(self, start: tuple[int, int]) -> None:
        """BFS implementation to find reachable spaces from a given starting position"""
        self.reachable = self.grid.copy()
        self.reachable[start] = 3		# mark starting point

        frontier = set()	# positions to be expanded
        frontier.add(start)

        while frontier:
            new_frontier = set()	# will become next frontier
            for pos in frontier:
                for move in [(0,-1), (0,1), (-1,0), (1,0)]:
                    neighbor = tuple(np.array(pos)+np.array(move))
                    if self.reachable[neighbor] == 0:
                        new_frontier.add(neighbor)
                        self.reachable[neighbor] = 3	# mark reachable position
            frontier = new_frontier
        self.reachable = self.reachable == 3
        self.grid[self.grid==0] = 3
        self.grid[self.reachable] = 0
    
    def render(self, imgs: dict[str, pygame.Surface], tile_size: int, display: pygame.Surface) -> None:

        for i in range(len(self.grid)):
            for j, val_j in enumerate(self.grid[i]):
                display.blit(list(imgs["terrain"].values())[val_j], (i * tile_size, j * tile_size, tile_size, tile_size))

        for b in self.bombs:
            display.blit(imgs["bomb"][str(b.frame+1)], (b.x * tile_size, b.y * tile_size, tile_size, tile_size))

        for x in self.explosions:
            for s in x.sectors:
                display.blit(imgs["explosion"][str(x.frame+1)], (s[0] * tile_size, s[1] * tile_size, tile_size, tile_size))
    
    def update_bombs(self,draw) -> int:
        expl_c = 0              # number of exploded crates
        for b in self.bombs:
            b.update(self.dt)
            expl_c += b.detonate(self.bombs)
            if b.explosion != None:
                self.explosions.append(b.explosion)
        draw()
        for x in self.explosions:
            x.update(self.dt)
            if x.time < 1:
                self.explosions.remove(x)
        return expl_c
        
    def possible_actions(self):
        return([0, 1, 2, 3, 4, 5])
