import numpy as np
from explosion import Explosion

class Bomb:
    frame = 0

    def __init__(self, r, x, y, map, bomber):
        self.range = r
        self.map=map
        self.x = x
        self.y = y
        self.pos = (x,y)
        self.time = 750
        self.bomber = bomber
        if self.bomber.bomb_limit >=0:
            self.bomber.bomb_limit-=1
        self.explosion = None

    def update(self, dt):

        self.time = self.time - dt

        if self.time < 250:
            self.frame = 2
        elif self.time < 500:
            self.frame = 1

    def detonate(self,bombs):
        exploded_boxes = 0
        if self.time < 1:
            bombs.remove(self)
            if self.bomber.bomb_limit >=0:
                self.bomber.bomb_limit += 1
            self.map[self.x][self.y] = 0
            self.explosion = Explosion(self.x, self.y, self.range)
            exploded_boxes = self.explosion.explode(self.map)
            self.bomber.check_death(self.explosion)
            for b in bombs:
                if b.pos in list(set(self.explosion.sectors) & set([b.pos for b in bombs])):
                    b.time = 0    
        return exploded_boxes

