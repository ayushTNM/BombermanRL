import numpy as np
import pygame
import sys
class Environment(object):
    
    def __init__(self,width,height,wall_chance,box_chance = 0,box_count = 0,seed = None):
        # so IDE knows that an Environment instance should have these properties
        self.width=width
        self.wall_chance = wall_chance
        self.box_chance = box_chance
        self.height=height
        self.shape=np.array([self.width,self.height])
        self.box_count = box_count
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        else:
            self.rng = np.random.default_rng()
        self.generate()
        pass

    def to_state(self,location):
        location = tuple(np.array(location)-1)
        return np.ravel_multi_index((*location,*self.exploded_boxes),(*self.shape-2,*[2 for _ in range(self.box_count)]))

    def create_grid(self):
        self.grid = np.zeros(tuple(self.shape),dtype=int)
        self.grid[:,[0,-1]] = self.grid[[0,-1]] = 1             #set edges to walls
        self.grid[1:self.grid.shape[0]-1,1:self.grid.shape[1]-1] = self.rng.random(tuple(np.array(self.shape)-2)) < self.wall_chance
        self.free_idxs = list(zip(*np.where(self.grid==0)))

    def generate_start_location(self):
        count = 0
        free_idxs = list(zip(*np.where(self.grid==0)))
        x,y = free_idxs[self.rng.integers(len(free_idxs))]
        self.gridSearch((x,y))
        while(np.sum(self.reachable) < np.sum(self.grid == 1)*(1-(self.wall_chance+.2))):
            count+=1
            if count == sum(self.shape):
                print("FAIL, NO SPACE FOR PLAYER")
                exit()
            elif count % max(self.shape-2)//4 == 0:
                self.create_grid()
                free_idxs = list(zip(*np.where(self.grid==0)))
            x,y = free_idxs[self.rng.integers(len(free_idxs))]
            self.gridSearch((x,y))
        self.x,self.y = x,y

    def generate(self):
    
        self.create_grid()
        self.generate_start_location()

        mask = (np.arange(self.grid.shape[0])[np.newaxis,:]-self.x)**2 + (np.arange(self.grid.shape[0])[:,np.newaxis]-self.y)**2 >= 2**2
        mask = np.bitwise_and(self.reachable,mask)
        print(mask)
        box_idxs=np.array(list(zip(*np.where(mask.T == True))))
        print(box_idxs)
        # print(box_idxs)
        if self.box_chance == 0:
            self.box_locs = box_idxs[self.rng.choice(len(box_idxs),self.box_count,replace=False)]
        else:
            self.box_locs = box_idxs[self.rng.random(len(box_idxs))< self.wall_chance]
        self.grid[tuple([*self.box_locs.T])] = 2
        # print(boxes)
        # print(self.x,self.y)
        # exit()
        # arr[mask] = 123.
        # for i in range(len(self.grid)):
        #     for j in range(len(self.grid[i])):
        #         if not self.reachable[i,j] and not self.grid[i,j] in [1,2]:
        #             self.grid[i,j]=3
        #         if self.grid[i,j] != 0 or (self.x,self.y) == (i,j) or not self.reachable[i,j] or \
        #             sum(abs(np.array([self.x,self.y])-np.array([i,j])))-1 < 2:
        #             continue
        #         if self.box_chance != 0 and np.random.uniform() < self.box_chance:
        #             self.grid[i,j] = 2
        #             self.box_count+=1
        #         elif np.random.uniform() > len(self.free_idxs)-(self.box_count+1) / len(self.free_idxs):
        #             continue
        #         elif self.box_chance ==0 and b_c > 0:
        #             self.grid[i,j] = 2
        #             b_c-=1

        self.bkppos = (self.x,self.y)
        self.bkpgrid = self.grid.copy()
        self.n_states = self.height * self.width * (2**self.box_count)
    
        
    def reset(self,agent):
        self.bombs,self.explosions = [],[]
        self.grid = self.bkpgrid.copy()
        self.bombs,self.explosions = [],[]
        self.exploded_boxes = np.zeros((self.box_count),dtype=int)
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

        for i in range(len(self.grid)):
            for j,valj in enumerate(self.grid[i]):
                display.blit(list(imgs["terrain"].values())[valj], (i * tile_size, j * tile_size, tile_size, tile_size))

        for b in self.bombs:
            display.blit(imgs["bomb"][str(b.frame+1)], (b.x * tile_size, b.y * tile_size, tile_size, tile_size))

        for x in self.explosions:
            for s in x.sectors:
                display.blit(imgs["explosion"][str(x.frame+1)], (s[0] * tile_size, s[1] * tile_size, tile_size, tile_size))
        
    
    def step(self, action, agent,dt,draw):
        r=-1
        actions = [(0,1),(1,0),(0,-1),(-1,0)]
        direction = agent.direction
        movement = False

        for e in pygame.event.get():
            if e.type == pygame.QUIT: 
                sys.exit(0)
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    sys.exit(0)
                if e.key == pygame.K_SPACE and agent.type == "Player" and agent.life:
                    action = 5

        if action < 4:
            direction = action
            movement = True
            if direction != agent.direction: agent.frame=0; agent.direction = direction
            agent.move(*actions[action],self.grid)
        elif action > 4:
            if agent.bomb_limit == 0:
                return r,self.to_state(agent.get_coords())
            if not agent.get_coords() in [b.pos for b in self.bombs]:
                temp_bomb = agent.plant_bomb(self.grid,dt)
                self.bombs.append(temp_bomb)
                self.grid[temp_bomb.pos] = 0
        if not movement:
            agent.frame = 0
        draw()
        r += self.update_bombs(dt)
        if agent.type == "PrioritizedSweepingAgent":
            # print(self.box_locs)
            self.exploded_boxes[self.grid[tuple([*self.box_locs.T])] != 2] =1
            return r,self.to_state(agent.get_coords())
        else:
            return r,None

    def update_bombs(self,dt) -> int:
        expl_c=0
        for b in self.bombs:
            b.update(dt)
            expl_c += b.detonate(self.bombs)
            if b.explosion != None:
                self.explosions.append(b.explosion)
        for x in self.explosions:
            x.update(dt)
            if x.time < 1:
                self.explosions.remove(x)
        return expl_c
        
    
    def possible_actions(self):
        return([0,1,2,3,4,5])
    
    def state(self):
        pass
    
    def state_size(self):
        pass
    
    def action_size(self):
        return(len(self.possible_actions()))
    
    def done(self):
        pass