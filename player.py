import pygame
import math
import numpy as np
from itertools import groupby

from bomb import Bomb

class Player:
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
        tempx = int(self.x/self.step) if dx != -1 else math.ceil(self.x / self.step)
        tempy = int(self.y/self.step) if dy != 1 else math.ceil(self.y / self.step)

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

        if self.frame == 2:
            self.frame %= 2
        else:
            self.frame += 1
            
    def act(self):
        keys = pygame.key.get_pressed()
        moves = [pygame.K_UP,pygame.K_RIGHT,pygame.K_DOWN,pygame.K_LEFT]
        direction = self.direction
        action = 6
        for ind,k in enumerate(moves):
            if keys[k]:
                self.direction = ind
                if direction != self.direction: self.frame=0
                if action == 6: action = ind
            direction = self.direction
            if action != 6:
                return action
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
