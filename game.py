import pygame
import sys
# import glob
import time
from player import Player
from enemy import Enemy
from algorithm import Algorithm
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
        self.player = None
        self.grid_size = grid_size
        self.alg = Algorithm.PLAYER
        self.path = True
        self.tile_size = tile_size

        pygame.font.init()
        self.font = pygame.font.SysFont('Bebas', 100)
        self.display = pygame.display.set_mode(self.grid_size*self.tile_size)
        pygame.display.set_caption('Bomberman')
        self.clock = pygame.time.Clock()

        self.loadedImgs = {}
        for img in self.images:
            if (folder:=img.split("\\")[-2]) not in self.loadedImgs.keys():
                self.loadedImgs.update({folder:{}})
            loadedImg = pygame.image.load(img)
            scaledImg = pygame.transform.scale(loadedImg, (tile_size, tile_size))
            self.loadedImgs[folder].update({img.split('\\')[-1].split('.')[-2]:scaledImg})

        # print(self.loadedImgs)

    def set_alg(self,_,c):
        self.alg = c
        print(self.alg)

    def set_path(self,_,c):
        self.path = c

    def create_grid(self):
        self.grid = np.zeros(tuple(self.grid_size),dtype=int)
        self.grid[:,[0,-1]] = self.grid[[0,-1]] = 1             #set edges to walls
        self.grid[1:self.grid.shape[0]-1,1:self.grid.shape[1]-1] = np.random.rand(*(self.grid_size-2)) < self.wall_chance
        self.free_idxs = list(zip(*np.where(self.grid==0)))
        

    def run(self):
        self.create_grid()
        (x,y) = self.free_idxs[np.random.randint(len(self.free_idxs))]
        self.player = Player((x,y),-1)
        self.bombs,self.explosions = [],[]

        if self.alg is Algorithm.PLAYER:
            self.player.load_animations(self.loadedImgs["player"])
        elif self.alg is not Algorithm.NONE:
            en0 = Enemy(1, 1, self.alg)
            en0.load_animations('', self.loadedImgs["enemy"])
            self.player.life = False
        else:
            self.player.life = False
        self.main()

    def draw(self):
        
        self.display.fill(BACKGROUND)

        for i in range(len(self.grid)):
            for j,valj in enumerate(self.grid[i]):
                self.display.blit(list(self.loadedImgs["terrain"].values())[valj], (i * self.tile_size, j * self.tile_size, self.tile_size, self.tile_size))

        for b in self.bombs:
            self.display.blit(self.loadedImgs["bomb"][str(b.frame+1)], (b.x * self.tile_size, b.y * self.tile_size, self.tile_size, self.tile_size))

        for x in self.explosions:
            for s in x.sectors:
                self.display.blit(self.loadedImgs["explosion"][str(x.frame+1)], (s[0] * self.tile_size, s[1] * self.tile_size, self.tile_size, self.tile_size))
        if self.player.life:
            self.display.blit(self.player.animation[self.player.direction][self.player.frame],
                (self.player.x * (self.tile_size / self.player.step), self.player.y * (self.tile_size / self.player.step), self.tile_size, self.tile_size))


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
                
        #         if self.player.life:
        #             pscreenpos = (np.array([self.player.x,self.player.y]) * (self.tile_size / self.player.step)).astype(int)
        #             ppos = list(map(slice,*np.array([pscreenpos,pscreenpos+self.tile_size])))
        #             player = pygame.surfarray.array3d(self.player.animation[self.player.direction][self.player.frame])
        #             mask=np.any(player!=0,axis=-1)
        #             surface[tuple(ppos)][mask] = player[mask]
        pygame.display.update()


    def generate_map(self):
        print("in")
        self.gridSearch(self.player.get_coords())
        # print(self.player.get_coords())
        count = 0
        while(np.sum(self.reachable) < np.sum(self.grid == 1)*(1-(self.wall_chance+.2))):
            count+=1
            # print(count,np.prod(self.grid_size-2))
            if count == max(self.grid_size-2)//2:
                print("FAIL, NO SPACE FOR PLAYER")
                exit()
            elif count % max(self.grid_size-2)//4 == 0:
                self.create_grid()
            (x,y) = self.free_idxs[np.random.randint(len(self.free_idxs))]
            self.player = Player((x,y),self.player.range)
            self.gridSearch(self.player.get_coords())
        print("out")
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if not self.reachable[i,j] and not self.grid[i,j] in [1,2]:
                    self.grid[i,j]=3
                if self.grid[i,j] != 0 or (coords:=self.player.get_coords()) == (i,j) or not self.reachable[i,j] or \
                    sum(abs(np.array(coords)-np.array([i,j])))-1 < 2:
                    continue
                if np.random.uniform() < self.box_chance:
                    self.grid[i,j] = 2

        return


    def main(self):
        self.generate_map()
        while self.player.life and 2 in self.grid:
            dt = self.clock.tick(15)
            # for en in enemy_list:
            #     en.make_move(grid, bombs, explosions, ene_blocks)
            self.player.act(self.grid)

            self.draw()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    sys.exit(0)
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_SPACE:
                        if self.player.bomb_limit == 0:
                            continue
                        if not self.player.get_coords() in [b.pos for b in self.bombs]:
                            temp_bomb = self.player.plant_bomb(self.grid)
                            self.bombs.append(temp_bomb)
                            self.grid[temp_bomb.pos] = 0
                            if self.player.bomb_limit >=0:
                                self.player.bomb_limit -= 1

            self.update_bombs(dt)
            # print("here",self.grid)
        self.game_over()

    def DFS(self,row,col):
        # print("in")
        if self.grid[row,col] in [1,2]:
            return self.reachable

        # print(player)
        if (row,col) != self.player.get_coords():
            self.reachable[row,col] = True

        if (col > 0 and not self.reachable[row][col - 1]):
            self.DFS(row, col - 1)
        if (row > 0 and not self.reachable[row - 1][col]):
            self.DFS(row - 1, col)
        if (col < self.grid.shape[1] - 1 and not self.reachable[row][col + 1]):
            self.DFS(row, col + 1)
        if (row < self.grid.shape[0] - 1 and not self.reachable[row + 1][col]):
            self.DFS(row + 1, col)

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

    def update_bombs(self,dt):
        for b in self.bombs:
            b.update(dt)
            b.detonate(self.bombs)
            if b.explosion != None:
                self.explosions.append(b.explosion)
        self.player.check_death(self.explosions)
        for x in self.explosions:
            x.update(dt)
            if x.time < 1:
                self.explosions.remove(x)


    def game_over(self):

        dt = self.clock.tick(15)
        self.update_bombs(dt)
        _,counts = np.unique(self.grid, return_counts=True)
        # winner = ""
        if counts[2] == 0:
            self.draw()
            textsurface = self.font.render("Win", False, (0, 0, 0))
            font_w = textsurface.get_width()
            font_h = textsurface.get_height()
            self.display.blit(textsurface, (self.display.get_width() // 2 - font_w//2,  self.display.get_height() // 2 - font_h//2))
            pygame.display.update()
            time.sleep(2)
            # break
        else:
            self.draw()
            textsurface = self.font.render("Lose", False, (0, 0, 0))
            font_w = textsurface.get_width()
            font_h = textsurface.get_height()
            self.display.blit(textsurface, (self.display.get_width() // 2 - font_w//2, self.display.get_height() // 2 - font_h//2))
            pygame.display.update()
            time.sleep(2)
            # break
        self.bombs,self.explosions = [],[]
