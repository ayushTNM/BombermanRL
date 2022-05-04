import numpy as np

class Explosion:

    bomber = None

    def __init__(self, x, y, r,countdown=300):
        self.sourceX = x
        self.sourceY = y
        self.range = r
        self.countdown = countdown
        self.time = self.countdown
        self.frame = 0
        self.sectors = []

    def explode(self, map, bombs, b):

        self.bomber = b.bomber
        self.sectors.extend(b.sectors)
        bombs.remove(b)
        self.bomb_chain(bombs, map)

    def bomb_chain(self, bombs, map):

        # for s in self.sectors:
            for b in bombs:
                if [b.x,b.y] in self.sectors.tolist():
                    map[b.x,b.y] = 0
                    b.bomber.bomb_limit+=1
                    self.explode(map,bombs,b)
                # if x.posX == s[0] and x.posY == s[1]:

                #     map[x.posX][x.posY] = 0
                #     x.bomber.bomb_limit += 1
                #     self.explode(map, bombs, x)

    def clear_sectors(self, map):
        self.sectors = np.array(self.sectors)
        # for i in self.sectors:
        print(self.sectors)
        print(map[np.array(self.sectors)])
        print(self.sectors[:,0],self.sectors[:,1])
        map[self.sectors[:,0],self.sectors[:,1]] = 0

    def update(self, dt):

        self.time = self.time - dt

        if self.time < self.countdown/3:
            self.frame = 2
        elif self.time < self.countdown*(2/3):
            self.frame = 1
