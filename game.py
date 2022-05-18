import pygame
import sys
# import glob
from environment import Environment
import time
from agent import Player, PrioritizedSweepingAgent
# from enemy import Enemy
# from algorithm import Algorithm
import numpy as np

BACKGROUND = (107, 142, 35)

grass_img = None
block_img = None
box_img = None
bomb1_img = None
bomb2_img = None
bomb3_img = None
explosion1_img = None
explosion2_img = None
explosion3_img = None


terrain_images = []
bomb_images = []
explosion_images = []

# font = pygame.font.SysFont('Bebas', 30)
# TEXT_LOSE = font.render('GAME OVER', False, (0, 0, 0))
# TEXT_WIN = font.render('WIN', False, (0, 0, 0))

class game:
    def __init__(self,grid_size, box_chance, wall_chance, tile_size,images):

        # print(grid)
        self.images=images
        self.box_chance = box_chance if 0<=box_chance<=1 else box_chance/100
        self.wall_chance = wall_chance if 0<=wall_chance<=1 else wall_chance/100
        self.agent = None
        self.grid_size = grid_size
        self.alg = "Player"
        self.path = True
        self.tile_size = tile_size

        pygame.font.init()
        self.font = pygame.font.SysFont('Bebas', 100)
        self.display = pygame.display.set_mode(self.grid_size*self.tile_size)
        pygame.display.set_caption('Bomberman')
        self.clock = pygame.time.Clock()

        self.loadedImgs = {}
        for img in self.images:
            imgName=img.replace("\\","/").split("/")
            if (folder:=imgName[-2]) not in self.loadedImgs.keys():
                self.loadedImgs.update({folder:{}})
            loadedImg = pygame.image.load(img)
            scaledImg = pygame.transform.scale(loadedImg, (tile_size, tile_size))
            self.loadedImgs[folder].update({imgName[-1].split('.')[-2]:scaledImg})
        
        self.env = Environment(*grid_size,wall_chance,box_chance)
        # print(self.loadedImgs)

    def set_alg(self,_,c):
        self.alg = c

    def set_path(self,_,c):
        self.path = c

    # def create_grid(self):
    #     self.grid = np.zeros(tuple(self.grid_size),dtype=int)
    #     self.grid[:,[0,-1]] = self.grid[[0,-1]] = 1             #set edges to walls
    #     self.grid[1:self.grid.shape[0]-1,1:self.grid.shape[1]-1] = np.random.rand(*(self.grid_size-2)) < self.wall_chance
    #     self.free_idxs = list(zip(*np.where(self.grid==0)))
        

    # def run(self):
    #     self.create_grid()
    #     (x,y) = self.free_idxs[np.random.randint(len(self.free_idxs))]

    #     if self.alg is Algorithm.PLAYER:
    #         self.agent = Player((x,y),-1)
    #         self.agent.load_animations(self.loadedImgs["player"])
    #     elif self.alg is not Algorithm.NONE:
    #         self.agent = Enemy(1, 1, self.alg)
    #         self.agent.load_animations(self.loadedImgs["agent"])
    #     self.main()

    def draw(self):
        
        self.display.fill(BACKGROUND)

        self.env.render(self.loadedImgs,self.tile_size,self.display)

        if self.agent.life:
            self.display.blit(self.agent.animation[self.agent.direction][self.agent.frame],
                (self.agent.x * (self.tile_size / self.agent.step), self.agent.y * (self.tile_size / self.agent.step), self.tile_size, self.tile_size))


        # surface = pygame.surfarray.pixels3d(self.display)
        # for i,vali in enumerate(self.grid):
        #     for j,valj in enumerate(vali):
        #         screenpos=np.array([i,j])*self.tile_size
        #         pos = list(map(slice,*np.array([screenpos,screenpos+self.tile_size])))
                
        #         surface[tuple(pos)] = pygame.surfarray.array3d(list(self.loadedImgs["terrain"].values())[valj])
        #         if (bpos:=(i,j)) in self.bombs:
        #             bomb=pygame.surfarray.array3d(self.loadedImgs["bomb"][str(self.bombs[bpos].frame+1)])
        #             mask=np.any(bomb != 0,axis=-1)
        #             surface[tuple(pos)][mask] = bomb[mask]

        #         if len(self.explosions) > 0:
        #             (sect,expl) = np.array(list(self.explosions.items()),dtype=object).T
        #             if f"({i}, {j})" in str(sect):
        #                 for indS, valS in enumerate(sect):
        #                     if (i,j) in valS:
        #                         explos= pygame.surfarray.array3d(self.loadedImgs["explosion"][str(expl[indS].frame+1)])
        #                         mask=np.any(explos!=0,axis=-1)
        #                         surface[tuple(pos)][mask] = explos[mask]
                
        #         if self.agent.life:
        #             pscreenpos = (np.array([self.agent.x,self.agent.y]) * (self.tile_size / self.agent.step)).astype(int)
        #             ppos = list(map(slice,*np.array([pscreenpos,pscreenpos+self.tile_size])))
        #             player = pygame.surfarray.array3d(self.agent.animation[self.agent.direction][self.agent.frame])
        #             mask=np.any(player!=0,axis=-1)
        #             surface[tuple(ppos)][mask] = player[mask]
        pygame.display.update()


    # def generate_map(self):
    #     print("in")
        # self.gridSearch(self.agent.get_coords())
        # # print(self.agent.get_coords())
        # count = 0
        # while(np.sum(self.reachable) < np.sum(self.grid == 1)*(1-(self.wall_chance+.2))):
        #     count+=1
        #     # print(count,np.prod(self.grid_size-2))
        #     if count == max(self.grid_size-2)//2:
        #         print("FAIL, NO SPACE FOR PLAYER")
        #         exit()
        #     elif count % max(self.grid_size-2)//4 == 0:
        #         self.create_grid()
        #     (x,y) = self.free_idxs[np.random.randint(len(self.free_idxs))]
        #     self.agent = Player((x,y),self.agent.range)
        #     self.gridSearch(self.agent.get_coords())
        # print("out")
        # for i in range(len(self.grid)):
        #     for j in range(len(self.grid[i])):
        #         if not self.reachable[i,j] and not self.grid[i,j] in [1,2]:
        #             self.grid[i,j]=3
        #         if self.grid[i,j] != 0 or (coords:=self.agent.get_coords()) == (i,j) or not self.reachable[i,j] or \
        #             sum(abs(np.array(coords)-np.array([i,j])))-1 < 2:
        #             continue
        #         if np.random.uniform() < self.box_chance:
        #             self.grid[i,j] = 2
        # return


    def main(self):
        iterations = 1
        episodes = 100
        for _ in range(iterations):
            self.env.generate()
            if self.alg == "Player":
                self.agent = Player((self.env.x,self.env.y),-1)
                self.agent.load_animations(self.loadedImgs["player"])
            elif self.alg is not None:
                self.agent = PrioritizedSweepingAgent(self.env.n_states,6,0.01,0.99,(self.env.x,self.env.y))
                self.agent.load_animations(self.loadedImgs["agent"])
            # print(self.agent.type)

            for _ in range(episodes):
                self.agent,s = self.env.reset(self.agent)
                while self.agent.life and 2 in self.env.grid:
                    if self.agent.type == "Player":
                        self.clock.tick(15)
                    else:
                        self.clock.tick()
                    dt = self.clock.get_fps()
                    # print(dt)

                    a = self.agent.select_action(s,0.1)

                    for e in pygame.event.get():
                        if e.type == pygame.QUIT: 
                            sys.exit(0)
                        elif e.type == pygame.KEYDOWN:
                            if e.key == pygame.K_ESCAPE:
                                sys.exit(0)
                            if e.key == pygame.K_SPACE and self.agent.type == "Player":
                                a = 5

                    self.draw()
                    reward, next_state = self.env.step(a,self.agent,dt)
                    if self.agent.type == "PrioritizedSweepingAgent":
                        self.agent.update(s,a,reward,next_state,0,10)
                    s = next_state

                self.game_over()
                if self.agent.type ==  "Player":
                    break
            else:
                continue
            break

    def DFS(self,row,col):
        # print("in")
        if self.grid[row,col] in [1,2]:
            return self.reachable

        # print(player)
        if (row,col) != self.agent.get_coords():
            self.reachable[row,col] = True

        if (col > 0 and not self.reachable[row][col - 1]):
            self.DFS(row, col - 1)
        if (row > 0 and not self.reachable[row - 1][col]):
            self.DFS(row - 1, col)
        if (col < self.grid.shape[1] - 1 and not self.reachable[row][col + 1]):
            self.DFS(row, col + 1)
        if (row < self.grid.shape[0] - 1 and not self.reachable[row + 1][col]):
            self.DFS(row + 1, col)

    # def gridSearch(self,start):
    #     self.reachable = self.grid.copy()
    #     self.reachable[start] = 3		# color starting point

    #     frontier = set()	# positions to be expanded
    #     frontier.add(start)

    #     while frontier:
    #         new_frontier = set()	# will become next frontier
    #         for pos in frontier:
    #             for move in [(0,-1), (0,1), (-1,0), (1,0)]:
    #                 neighbour = tuple(np.array(pos)+np.array(move))
    #                 if self.reachable[neighbour] == 0:
    #                     new_frontier.add(neighbour)
    #                     self.reachable[neighbour] = 3	# color reachable position
    #         frontier = new_frontier
    #     self.reachable = self.reachable==3



    def game_over(self):

        if  self.agent.type == "Player":
            self.clock.tick(15)
        else:
            self.clock.tick(60)
        dt = self.clock.get_fps()
        self.env.update_bombs(dt)
        _,counts = np.unique(self.env.grid, return_counts=True)
        # winner = ""
        if len(counts) == 2:
            self.draw()
            textsurface = self.font.render("Win", False, (0, 0, 0))
            font_w = textsurface.get_width()
            font_h = textsurface.get_height()
            self.display.blit(textsurface, (self.display.get_width() // 2 - font_w//2,  self.display.get_height() // 2 - font_h//2))
            pygame.display.update()
            if self.agent.type == {"Player"}:
                time.sleep(2)
            else:
                time.sleep(.25)
            # break
        else:
            self.draw()
            textsurface = self.font.render("Lose", False, (0, 0, 0))
            font_w = textsurface.get_width()
            font_h = textsurface.get_height()
            self.display.blit(textsurface, (self.display.get_width() // 2 - font_w//2, self.display.get_height() // 2 - font_h//2))
            pygame.display.update()
            if self.agent.type == "Player":
                time.sleep(2)
            else:
                time.sleep(.25)
            # break
