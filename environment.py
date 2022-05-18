import numpy as np

class Environment(object):
    
    def __init__(self,width,height,wall_chance,box_chance):
        # so IDE knows that an Environment instance should have these properties
        self.width=width
        self.wall_chance = wall_chance
        self.box_chance = box_chance
        self.height=height
        self.shape=np.array([self.width,self.height])
        self.exploded_boxes = 0
        self.box_count = 0
        self.generate()
        pass

    def to_state(self,location):
        # print((*self.shape,self.box_count))
        print(location)
        return np.ravel_multi_index((*location,self.exploded_boxes),(*self.shape,(self.box_count+1)))

    def to_index(self,state):
        return np.unravel_index(state,(*self.shape,(self.box_count+1)))

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
            if count == max(self.shape-2):
                print("FAIL, NO SPACE FOR PLAYER")
                exit()
            elif count % max(self.shape-2)//4 == 0:
                self.create_grid()
                free_idxs = list(zip(*np.where(self.grid==0)))
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
        self.bkppos = (self.x,self.y)
        self.bkpgrid = self.grid.copy()
        self.n_states = self.height * self.width * (self.box_count+1)
        self.bombs,self.explosions = [],[]
        
    def reset(self,agent):
        self.grid = self.bkpgrid.copy()
        self.exploded_boxes = 0
        self.bombs,self.explosions = [],[]
        agent.x,agent.y = np.array(self.bkppos)*agent.step
        agent.life = True
        return agent, self.to_state(agent.get_coords())

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
    
    def step(self, action, agent,dt):
        r = -1
        actions = [(0,1),(1,0),(0,-1),(-1,0)]
        if action < 4:
            agent.move(*actions[action],self.grid)
        elif action > 4:
            if agent.life == False:
                r-=100
                return r, self.to_state(agent.get_coords())
            if agent.bomb_limit == 0:
                return r, self.to_state(agent.get_coords())
            if not agent.get_coords() in [b.pos for b in self.bombs]:
                agent.bomb_limit -=1
                temp_bomb = agent.plant_bomb(self.grid)
                self.bombs.append(temp_bomb)
                self.grid[temp_bomb.pos] = 0
        r += self.update_bombs(dt)
        return r, self.to_state(agent.get_coords())
        # print((agent.x/agent.step,agent.y/agent.step), agent.get_coords())
        # if (agent.x/agent.step,agent.y/agent.step) == agent.get_coords():
        #     print(self.to_state(agent.get_coords()))

    def update_bombs(self,dt) -> int:
        expl_b=0
        for b in self.bombs:
            b.update(dt)
            expl_b = b.detonate(self.bombs)
            self.exploded_boxes += expl_b
            if b.explosion != None:
                self.explosions.append(b.explosion)
        for x in self.explosions:
            x.update(dt)
            if x.time < 1:
                self.explosions.remove(x)
        return expl_b
        
    
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