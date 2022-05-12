import numpy as np

class Environment(object):
    
    def __init__(self,width,height,wall_chance,box_chance):
        # so IDE knows that an Environment instance should have these properties
        self.width=width
        self.wall_chance = wall_chance
        self.box_chance = box_chance
        self.height=height
        self.shape=(self.width,self.height)
        self.exploded_crates = 0
        self.box_count = 0
        self.generate()
        self.n_states = self.height * self.width * self.box_count
        self.bombs,self.explosions = [],[]
        pass

    def to_state(self,location):
        # print((*self.shape,self.box_count))
        return np.ravel_multi_index((*location,self.exploded_crates),(*self.shape,self.box_count))

    def to_index(self,state):
        return np.ravel_index(state,(*self.shape,self.box_count))

    def create_grid(self):
        self.grid = np.zeros(tuple(self.shape),dtype=int)
        self.grid[:,[0,-1]] = self.grid[[0,-1]] = 1             #set edges to walls
        self.grid[1:self.grid.shape[0]-1,1:self.grid.shape[1]-1] = np.random.rand(*(np.array(self.shape)-2)) < self.wall_chance
        self.free_idxs = list(zip(*np.where(self.grid==0)))

    def generate_start_location(self):
        count = 0
        free_idxs = list(zip(*np.where(self.grid==0)))
        x,y = free_idxs[np.random.randint(len(free_idxs))]
        self.gridSearch((x,y))
        while(np.sum(self.reachable) < np.sum(self.grid == 1)*(1-(self.wall_chance+.2))):
            count+=1
            if count == max(self.shape-2)//2:
                print("FAIL, NO SPACE FOR PLAYER")
                exit()
            elif count % max(self.shape-2)//4 == 0:
                self.create_grid()
            x,y = free_idxs[np.random.randint(len(free_idxs))]
            self.gridSearch((x,y))
        self.x,self.y = x,y

    def generate(self):
        self.create_grid()           #set edges to walls
        self.generate_start_location()
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if not self.reachable[i,j] and not self.grid[i,j] in [1,2]:
                    self.grid[i,j]=3
                if self.grid[i,j] != 0 or (self.x,self.y) == (i,j) or not self.reachable[i,j] or \
                    sum(abs(np.array([self.x,self.y])-np.array([i,j])))-1 < 2:
                    continue
                if np.random.uniform() < self.box_chance:
                    self.grid[i,j] = 2
                    self.box_count+=1
        self.bkpgrid = self.grid.copy()
        
    def reset(self):
        self.grid = self.bkpgrid.copy()
        self.exploded_crates = 0
        self.bombs,self.explosions = [],[]
        return self.bkppos

    def gridSearch(self,start):
        self.reachable = self.grid.copy()
        self.reachable[start] = 3		# color starting point

        frontier = set()	# positions to be expanded
        frontier.add(start)

        while frontier:
            new_frontier = set()	# will become next frontier
            for pos in frontier:
                for move in [(0,-1), (0,1), (-1,0), (1,0)]:
                    neighbour = tuple(np.array(pos)+np.array(move))
                    if self.reachable[neighbour] == 0:
                        new_frontier.add(neighbour)
                        self.reachable[neighbour] = 3	# color reachable position
            frontier = new_frontier
        self.reachable = self.reachable==3
    
    def render(self,imgs,tile_size,display):
        # print(self.grid)
        for i in range(len(self.grid)):
            for j,valj in enumerate(self.grid[i]):
                display.blit(list(imgs["terrain"].values())[valj], (i * tile_size, j * tile_size, tile_size, tile_size))

        for b in self.bombs:
            display.blit(imgs["bomb"][str(b.frame+1)], (b.x * tile_size, b.y * tile_size, tile_size, tile_size))

        for x in self.explosions:
            for s in x.sectors:
                display.blit(imgs["explosion"][str(x.frame+1)], (s[0] * tile_size, s[1] * tile_size, tile_size, tile_size))
    
    def step(self, action, agent):
        actions = [(0,1),(1,0),(0,-1),(-1,0)]
        if action < 4:
            agent.move(*actions[action],self.grid)
        elif action < 5:
            temp_bomb = agent.plant_bomb(self.grid)
            self.bombs.append(temp_bomb)
            self.grid[temp_bomb.pos] = 0
            if agent.bomb_limit >=0:
                agent.bomb_limit -= 1
        if agent.frame == 0:
            self.to_state(agent.get_coords())

    def update_bombs(self,agent,dt):
        for b in self.bombs:
            b.update(dt)
            b.detonate(self.bombs)
            if b.explosion != None:
                self.explosions.append(b.explosion)
        agent.check_death(self.explosions)
        for x in self.explosions:
            x.update(dt)
            if x.time < 1:
                self.explosions.remove(x)
        
    
    def possible_actions(self):
        pass
    
    def state(self):
        pass
    
    def state_size(self):
        pass
    
    def action_size(self):
        pass
    
    def done(self):
        pass