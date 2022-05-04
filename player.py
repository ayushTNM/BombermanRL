import pygame
import math
import numpy as np

from bomb import Bomb

class Player:
    direction = 0
    frame = 0
    animation = []
    bomb_limit = 1

    def __init__(self,pos,range):
        (self.x,self.y) = pos
        self.range=range
        self.life = True

    def move(self, dx, dy, grid, enemies):
        tempx = int(self.x/4)
        tempy = int(self.y/4)
        # print(grid)
        # grid=grid.T
        # print(grid)
        # map = grid.copy()

        # for i in range(len(grid)):
        #     map.append([])
        #     for j in range(len(grid[i])):
        #         map[i].append(grid[i][j])

        for enemy in enemies:
            if not enemy.life:
                continue
            else:
                grid[enemy.pos//4] = 2

        if self.x % 4 != 0 and dx == 0:
            if self.x % 4 == 1:
                self.x -= 1
            elif self.x % 4 == 3:
                self.x += 1
            return

        if self.y % 4 != 0 and dy == 0:
            if self.y % 4 == 1:
                self.y -= 1
            elif self.y % 4 == 3:
                self.y += 1
            return

        # right
        if dx == 1:
            if grid[tempx+1][tempy] == 0:
                self.x += 1
        # left
        elif dx == -1:
            tempx = math.ceil(self.x / 4)
            if grid[tempx-1][tempy] == 0:
                
                self.x -= 1
            

        # bottom
        # print(tempx,tempy)
        if dy == 1:
            if grid[tempx][tempy+1] == 0:
                self.y += 1
        # top
        elif dy == -1:
            tempy = math.ceil(self.y / 4)
            if grid[tempx][tempy-1] == 0:
                self.y -= 1

    def get_coords(self):
        return (int(self.x/4),int(self.y/4))

    def plant_bomb(self, map):
        b = Bomb(self.range, round(self.x/4), round(self.y/4), map, self)
        return b

    def check_death(self, exp):
        for e in exp:
            if [int(self.x/4), int(self.y/4)] in e.sectors.tolist():
                self.life = False

    def load_animations(self, scale):
        front = []
        back = []
        left = []
        right = []
        resize_width = scale
        resize_height = scale

        f1 = pygame.image.load('images/hero/pf0.png')
        f2 = pygame.image.load('images/hero/pf1.png')
        f3 = pygame.image.load('images/hero/pf2.png')

        f1 = pygame.transform.scale(f1, (resize_width, resize_height))
        f2 = pygame.transform.scale(f2, (resize_width, resize_height))
        f3 = pygame.transform.scale(f3, (resize_width, resize_height))

        front.append(f1)
        front.append(f2)
        front.append(f3)

        r1 = pygame.image.load('images/hero/pr0.png')
        r2 = pygame.image.load('images/hero/pr1.png')
        r3 = pygame.image.load('images/hero/pr2.png')

        r1 = pygame.transform.scale(r1, (resize_width, resize_height))
        r2 = pygame.transform.scale(r2, (resize_width, resize_height))
        r3 = pygame.transform.scale(r3, (resize_width, resize_height))

        right.append(r1)
        right.append(r2)
        right.append(r3)

        b1 = pygame.image.load('images/hero/pb0.png')
        b2 = pygame.image.load('images/hero/pb1.png')
        b3 = pygame.image.load('images/hero/pb2.png')

        b1 = pygame.transform.scale(b1, (resize_width, resize_height))
        b2 = pygame.transform.scale(b2, (resize_width, resize_height))
        b3 = pygame.transform.scale(b3, (resize_width, resize_height))

        back.append(b1)
        back.append(b2)
        back.append(b3)

        l1 = pygame.image.load('images/hero/pl0.png')
        l2 = pygame.image.load('images/hero/pl1.png')
        l3 = pygame.image.load('images/hero/pl2.png')

        l1 = pygame.transform.scale(l1, (resize_width, resize_height))
        l2 = pygame.transform.scale(l2, (resize_width, resize_height))
        l3 = pygame.transform.scale(l3, (resize_width, resize_height))

        left.append(l1)
        left.append(l2)
        left.append(l3)

        self.animation.append(front)
        self.animation.append(right)
        self.animation.append(back)
        self.animation.append(left)
