import numpy as np

class Bomb:
    frame = 0

    def __init__(self, r, x, y, map, bomber):
        self.range = r
        self.x = x
        self.y = y
        self.pos = np.array([x,y],dtype=int)
        self.time = 3000
        self.bomber = bomber
        self.sectors = []
        self.get_range(map)

    def update(self, dt):

        self.time = self.time - dt

        if self.time < 1000:
            self.frame = 2
        elif self.time < 2000:
            self.frame = 1

    def get_range(self, map):
        # print(self.range)
        self.sectors.append(self.pos)
        for move in np.array([[0,-1], [0,1], [-1,0], [1,0]]):
            pos = self.pos
            steps = 0
            print(map)
            print(pos,map[pos])
            while map[pos[0],pos[1]] == 0 and (steps < self.range or self.range==-1):
                steps += 1
                print(pos)
                pos = move+pos
                print("here",pos)
                if map[pos[0],pos[1]] != 1:
                    self.sectors.append(pos)
        print(self.sectors)
