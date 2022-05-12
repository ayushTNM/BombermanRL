import numpy as np

class Explosion:

    bomber = None

    def __init__(self, x, y, r):
        self.sourceX = x
        self.sourceY = y
        self.pos = (x,y)
        self.range = r
        self.time = 300
        self.frame = 0
        self.sectors = set()

    def explode(self, map):
        self.get_range(map)
        s = np.array(list(self.sectors))
        map[s[:,0],s[:,1]] = 0 

    def get_range(self, map):
        self.sectors.add(self.pos)
        for move in np.array([(0,-1), (0,1), (-1,0), (1,0)]):
            neighbour = self.pos
            steps = 0
            while map[neighbour] == 0 and (steps < self.range or self.range==-1):
                steps += 1
                neighbour = tuple(np.array(move)+np.array(neighbour))
                if map[neighbour] != 1:
                    self.sectors.add(neighbour)

    def update(self, dt):

        self.time = self.time - dt

        if self.time < 200:
            self.frame = 2
        elif self.time < 100:
            self.frame = 1
