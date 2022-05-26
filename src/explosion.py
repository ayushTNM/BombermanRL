# dependencies
import numpy as np      # arrays, math

class Explosion:

    bomber = None

    def __init__(self, x: int, y: int, r: int, time: int):
        self.sourceX = x
        self.sourceY = y
        self.pos = (x, y)
        self.range = r
        self.time = time
        self.timer: int = time
        self.frame: int = 0
        self.sectors = set()

    def explode(self, map: np.ndarray) -> int:
        self.find_sectors(map)
        s = np.array(list(self.sectors))
        m: list[int] = map[s[:,0], s[:,1]]
        map[s[:,0], s[:,1]] = 0 
        return sum(m == 2)

    def find_sectors(self, map: np.ndarray) -> None:
        self.sectors.add(self.pos)
        for move in np.array([(0,-1), (0,1), (-1,0), (1,0)]):
            neighbor = self.pos
            steps = 0
            while map[neighbor] == 0 and (steps < self.range):
                steps += 1
                neighbor = tuple(np.array(move)+np.array(neighbor))
                if map[neighbor] != 1:
                    self.sectors.add(neighbor)

    def update(self, dt: int) -> None:
        self.time = self.time - dt
        if self.time < self.timer/1.5: self.frame = 2
        elif self.time < self.timer/2: self.frame = 1
