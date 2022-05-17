import pygame
import math
import numpy as np
from itertools import groupby
from queue import PriorityQueue

from bomb import Bomb

class Agent:
    direction = 0
    frame = 0
    movement = False
    animation = []
    bomb_limit = -1

    def __init__(self,pos,range,step=3):
        self.step = step
        self.x,self.y = np.array(pos)*self.step
        self.range=range
        self.life = True

    def move(self, dx, dy, grid):
        tempx = self.x//self.step if dx != -1 else math.ceil(self.x / self.step)
        tempy = self.y//self.step if dy != 1 else math.ceil(self.y / self.step)

        if dx == 0:
            self.x=round((self.x/self.step))*self.step
            if grid[int(self.x/self.step)][tempy-dy] != 0:
                return
            if grid[tempx][tempy-dy] == 0:
                self.y -= dy

        elif dy == 0:
            self.y=round((self.y/self.step))*self.step
            if grid[tempx+dx][int(self.y/self.step)] != 0:
                return
            if grid[tempx+dx][tempy] == 0:
                self.x += dx
            
    def act(self):
        keys = pygame.key.get_pressed()
        moves = [pygame.K_UP,pygame.K_RIGHT,pygame.K_DOWN,pygame.K_LEFT]
        direction = self.direction
        action = 6
        movement = False
        for ind,k in enumerate(moves):
            if keys[k]:
                direction = ind
                if direction != self.direction: self.frame=0; self.direction = direction
                if action == 6: action = ind; movement = True
            if action != 6:  
                if movement:
                    if self.frame == 2:
                        self.frame = 0
                    else:
                        self.frame += 1
                    return action
                else:
                    self.frame = 0
        return action

        
    def get_coords(self):
        return (int(self.x/self.step),int(self.y/self.step))

    def plant_bomb(self, map):
        return Bomb(self.range, round(self.x/self.step), round(self.y/self.step), map, self)

    def check_death(self, exp):
        for e in exp:
            if (int(self.x/self.step), int(self.y/self.step)) in e.sectors:
                self.life = False
                break

    def load_animations(self, imgs):
        self.animation=[[imgs[j] for j in list(i)] for _, i in groupby(imgs, lambda a: a[1])]
        print(self.animation)

class PrioritizedSweepingAgent:
    direction = 0
    frame = 0
    movement = False
    animation = []
    bomb_limit = -1

    def __init__(self, n_states: int, n_actions: int, alpha: float, gamma: float,
                 pos: tuple[int, int], b_range: int, step: int = 3, 
                 max_queue_size: int = 200, priority_cutoff: float = 0.01) -> None:
        self.n_states = n_states
        self.n_actions = n_actions
        self.alpha = alpha
        self.gamma = gamma
        self.range = b_range
        self.step = step
        self.x, self.y = np.array(pos)*step
        self.queue = PriorityQueue(maxsize=max_queue_size)
        self.priority_cutoff = priority_cutoff
        self.Q = np.zeros((n_states, n_actions))
        self.N = np.zeros((n_states, n_actions, n_states))
        self.model = np.zeros((n_states, n_actions, 2), dtype = int)
        self.life = True

    def move(self, dx, dy, grid):
        tempx = self.x//self.step if dx != -1 else math.ceil(self.x / self.step)
        tempy = self.y//self.step if dy != 1 else math.ceil(self.y / self.step)

        if dx == 0:
            self.x=round((self.x/self.step))*self.step
            if grid[int(self.x/self.step)][tempy-dy] != 0:
                return
            if grid[tempx][tempy-dy] == 0:
                self.y -= dy

        elif dy == 0:
            self.y=round((self.y/self.step))*self.step
            if grid[tempx+dx][int(self.y/self.step)] != 0:
                return
            if grid[tempx+dx][tempy] == 0:
                self.x += dx

    def select_action(self, s: int, eps: float) -> int:
        """Epsilon-greedy action selection"""
        return np.random.choice(np.where(self.Q[s] == np.max(self.Q[s]))[0]) if np.random.rand() > eps else np.random.choice(self.n_actions)

    def plant_bomb(self, map):
        return Bomb(self.range, round(self.x/self.step), round(self.y/self.step), map, self)
        
    def update(self, s: int, a: int, r: int, sp: int, done: bool, n_planning_updates: int) -> None:
        """Main update function of Prioritized Sweeping agent"""
        self.N[s,a,sp] += 1             # update transition count
        self.model[s,a] = r, sp         # update model
        
        p = self._calc_p(s, a, r, sp)       # calculate priority
        if p > self.priority_cutoff:        # state-action pair has a sufficiently high priority
            if self.queue.full():
                self.queue.queue.pop(-1)    # make space in queue
            self.queue.put((-p, (s, a)))    # put state-action pair in queue at appropriate position
        
        if done:    # if agent has reached goal, model updating is still required
            return  # but planning is not

        for _ in range(n_planning_updates):
            if self.queue.empty():
                break
            self._planning(s, a)
            
    def _planning(self, s: int, a: int) -> None:
        """Performs one planning iteration with Prioritized Sweeping method"""
        _, (s, a) = self.queue.get()    # get the state-action pair with highest priority from the queue
        r, sp = self.model[s,a]         # retrieve reward and next state from memory
        self._QL_update(s, a, r, sp)    # learning
        for (ss, aa) in zip(*np.where(self.N[:,:,s] > 0)):  # all states that can lead to current state
            rr, _ = self.model[ss,aa]                       # retrieve reward from memory
            p = self._calc_p(ss, aa, rr, s)                 # calculate priority
            if p > self.priority_cutoff:                    # state-action pair has a sufficiently high priority
                if self.queue.full():
                    self.queue.queue.pop(-1)                # make space in queue
                self.queue.put((-p, (ss, aa)))              # put state-action pair in queue at appropriate position
    
    def _QL_update(self, s: int, a: int, r: int, sp: int) -> None:
        """Simple Q-Learning update rule to update Q-array in place"""
        self.Q[s,a] += self.alpha * (r + self.gamma * max(self.Q[sp]) - self.Q[s,a])
    
    def _calc_p(self, s: int, a: int, r: int, sp: int) -> float:
        """Calculate the priority of a given transition"""
        return abs(r + self.gamma * max(self.Q[sp]) - self.Q[s,a])

    def load_animations(self, imgs):
        self.animation=[[imgs[j] for j in list(i)] for _, i in groupby(imgs, lambda a: a[1])]
        print(self.animation)
    
    def get_coords(self):
        return (int(self.x/self.step),int(self.y/self.step))
    
    def check_death(self, exp):
        for e in exp:
            if (int(self.x/self.step), int(self.y/self.step)) in e.sectors:
                self.life = False
                break