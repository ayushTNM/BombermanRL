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
        self.time = 3000
        self.bomber = bomber
        self.explosion = None

    def update(self, dt):

        self.time = self.time - dt

        if self.time < 1000:
            self.frame = 2
        elif self.time < 2000:
            self.frame = 1

    def detonate(self,bombs):
        if self.time < 1:
            bombs.remove(self)
            if self.bomber.bomb_limit >=0:
                self.bomber.bomb_limit += 1
            self.map[self.x][self.y] = 0
            self.explosion = Explosion(self.x, self.y, self.range)
            self.explosion.explode(self.map)
            for b in bombs:
                if b.pos in list(set(self.explosion.sectors) & set([b.pos for b in bombs])):
                    b.time = 0
            # self.data["explosions"].update({tuple(exp_temp.sectors): exp_temp})
    
