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
    Life = True
    def __init__(self,pos,b_range,step,bomb_limit,death):
        self.bomb_limit = bomb_limit
        self.step = step
        self.x,self.y = np.array(pos)*self.step
        self.range=b_range
        self.death = death
    
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

    def get_coords(self):
        return (round(self.x/self.step),round(self.y/self.step))

    def check_death(self, exp):
        if self.death and self.life is not False:
            # for e in exp:
                if (int(self.x/self.step), int(self.y/self.step)) in exp.sectors:
                    self.life = False
                    # break

    def load_animations(self, imgs):
        self.animation=[[imgs[j] for j in list(i)] for _, i in groupby(imgs, lambda a: a[1])]
        print(self.animation)


class Player(Agent):

    def __init__(self,pos,b_range=-1,step=3,bomb_limit=-1,death=True):
        self.type = type(self).__name__
        super().__init__(pos,b_range,step,bomb_limit,death)

    def plant_bomb(self, map):
        return Bomb(self.range, round(self.x/self.step), round(self.y/self.step), map, self)
            
    def select_action(self,s,eps):
        keys = pygame.key.get_pressed()
        moves = [pygame.K_UP,pygame.K_RIGHT,pygame.K_DOWN,pygame.K_LEFT]
        direction = self.direction
        action = 4
        movement=False
        for ind,k in enumerate(moves):
            if keys[k]:
                action = direction = ind
                movement=True
                if direction != self.direction: self.frame=0; self.direction = direction
        if movement:
            if self.frame == 2:
                self.frame = 0
            else:
                self.frame += 1
        else:
            self.frame=0
        return action

class PrioritizedSweepingAgent(Agent):

    def __init__(self, n_states: int, n_actions: int, alpha: float, gamma: float,
                 pos: tuple[int, int], b_range: int =-1, step: int = 1, bomb_limit: int= 1,death: bool=True,
                 max_queue_size: int = 200, priority_cutoff: float = 0.01) -> None:
        self.type = type(self).__name__
        self.n_states = n_states
        self.n_actions = n_actions
        self.alpha = alpha
        self.gamma = gamma
        self.queue = PriorityQueue(maxsize=max_queue_size)
        self.priority_cutoff = priority_cutoff
        self.Q = np.zeros((n_states, n_actions))
        self.N = np.zeros((n_states, n_actions, n_states))
        self.model = np.zeros((n_states, n_actions, 2), dtype = int)
        super().__init__(pos,b_range,step,bomb_limit,death)

    def plant_bomb(self, map):
        return Bomb(self.range, round(self.x/self.step), round(self.y/self.step), map, self)

    def select_action(self, s: int, eps: float) -> int:
        """Epsilon-greedy action selection"""
        if self.bomb_limit == 0:
            actions = self.n_actions-1
        else:
            actions = self.n_actions
        return np.random.choice(np.where(self.Q[s] == np.max(self.Q[s]))[0]) if np.random.rand() > eps else np.random.choice(actions)
        
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