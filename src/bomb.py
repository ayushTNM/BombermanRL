# python standard library
from __future__ import annotations  # type hinting
from typing import Any              # type hinting
# dependencies
import numpy as np                  # arrays, math
# local imports
from explosion import Explosion     # detonating bombs

class Bomb:
    frame = 0

    def __init__(self, r: int, x: int, y: int, map: np.ndarray, bomber: Any, time: int):
        """
        Instantiates a new Bomb at given position
        ---
        Note that :param bomber: should be of type Agent,
        but due to circular import constraints this class cannot be imported
        """
        self.range = r
        self.map = map
        self.x = x
        self.y = y
        self.pos = (x,y)
        self.time = time
        self.timer = time
        self.bomber = bomber
        if self.bomber.bomb_limit >= 0:
            self.bomber.bomb_limit -= 1
        self.explosion = None

    def update(self, dt: int):

        self.time = self.time - dt

        if self.time < self.timer/3: self.frame = 2
        elif self.time < self.timer/1.5: self.frame = 1

    def detonate(self, bombs: set[Bomb]):
        n_exploded_crates = 0
        if self.time < 1 or self.bomber.type == "PrioritizedSweepingAgent":
            bombs.remove(self)
            if self.bomber.bomb_limit >=0:
                self.bomber.bomb_limit += 1
            self.map[self.x][self.y] = 0
            self.explosion = Explosion(self.x, self.y, self.range, self.timer/10+1)
            n_exploded_crates: int = self.explosion.explode(self.map)
            self.bomber.check_death(self.explosion)
            for b in bombs:
                if b.pos in list(set(self.explosion.sectors) & set([b.pos for b in bombs])):
                    b.time = 0    
        return n_exploded_crates
