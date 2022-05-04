import pygame
import math
import numpy as np

from bomb import Bomb

class Player:
    direction = 0
    frame = 0
    animation = []
    bomb_limit = 1

    def __init__(self,pos,range,step=3):
        self.step = step
        (self.x,self.y) = np.array(pos)*self.step
        self.range=range
        self.life = True

    def move(self, dx, dy, grid, enemies):
        tempx = int(self.x/self.step) if dx != -1 else math.ceil(self.x / self.step)
        tempy = int(self.y/self.step) if dy != -1 else math.ceil(self.y / self.step)
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
                grid[enemy.pos//self.step] = 2
        print(self.x,self.y)
        if dx == 0:
            # print(self.x)
            self.x=round((self.x/self.step))*self.step
            if grid[int(self.x/self.step)][tempy+dy] != 0:
                return
            if grid[tempx][tempy+dy] == 0:
                self.y += dy
            



        elif dy == 0:
            self.y=round((self.y/self.step))*self.step
            if grid[tempx+dx][int(self.y/self.step)] != 0:
                return
            if grid[tempx+dx][tempy] == 0:
                self.x += dx
            

        
    def get_coords(self):
        return (int(self.x/self.step),int(self.y/self.step))

    def plant_bomb(self, map):
        b = Bomb(self.range, round(self.x/self.step), round(self.y/self.step), map, self)
        return b

    def check_death(self, exp):
        for e in exp:
            if [int(self.x/self.step), int(self.y/self.step)] in e.sectors.tolist():
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
