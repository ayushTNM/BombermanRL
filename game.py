import pygame
import sys
import random
import time
from player import Player
from explosion import Explosion
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
    def __init__(self,grid_size, box_chance, wall_chance, tile_size):

        # print(grid)
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


        # if en1_alg is not Algorithm.NONE:
        #     en1 = Enemy(11, 11, en1_alg)
        #     en1.load_animations('1', scale)
        #     enemy_list.append(en1)
        #     ene_blocks.append(en1)

        # if en2_alg is not Algorithm.NONE:
        #     en2 = Enemy(1, 11, en2_alg)
        #     en2.load_animations('2', scale)
        #     enemy_list.append(en2)
        #     ene_blocks.append(en2)

        # if en3_alg is not Algorithm.NONE:
        #     en3 = Enemy(11, 1, en3_alg)
        #     en3.load_animations('3', scale)
        #     enemy_list.append(en3)
            # ene_blocks.append(en3)

        grass_img = pygame.image.load('images/terrain/grass.png')
        grass_img = pygame.transform.scale(grass_img, (tile_size, tile_size))
        grass_not_img = pygame.image.load('images/terrain/grass_not.png')
        grass_not_img = pygame.transform.scale(grass_not_img, (tile_size, tile_size))
        block_img = pygame.image.load('images/terrain/block.png')
        block_img = pygame.transform.scale(block_img, (tile_size, tile_size))
        box_img = pygame.image.load('images/terrain/box.png')
        box_img = pygame.transform.scale(box_img, (tile_size, tile_size))
        bomb1_img = pygame.image.load('images/bomb/1.png')
        bomb1_img = pygame.transform.scale(bomb1_img, (tile_size, tile_size))
        bomb2_img = pygame.image.load('images/bomb/2.png')
        bomb2_img = pygame.transform.scale(bomb2_img, (tile_size, tile_size))
        bomb3_img = pygame.image.load('images/bomb/3.png')
        bomb3_img = pygame.transform.scale(bomb3_img, (tile_size, tile_size))
        explosion1_img = pygame.image.load('images/explosion/1.png')
        explosion1_img = pygame.transform.scale(explosion1_img, (tile_size, tile_size))
        explosion2_img = pygame.image.load('images/explosion/2.png')
        explosion2_img = pygame.transform.scale(explosion2_img, (tile_size, tile_size))
        explosion3_img = pygame.image.load('images/explosion/3.png')
        explosion3_img = pygame.transform.scale(explosion3_img, (tile_size, tile_size))

        self.terrain_images = [grass_img, block_img, box_img, grass_img,grass_not_img]
        self.bomb_images = [bomb1_img, bomb2_img, bomb3_img]
        self.explosion_images = [explosion1_img, explosion2_img, explosion3_img]

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
        self.reachable = np.zeros(tuple(self.grid_size),dtype=bool)
        (x,y) = self.free_idxs[np.random.randint(len(self.free_idxs))]
        self.player = Player((x,y),-1)
        self.ene_blocks = []
        self.bombs = []
        self.explosions = []

        if self.alg is Algorithm.PLAYER:
            self.player.load_animations(self.tile_size)
        elif self.alg is not Algorithm.NONE:
            en0 = Enemy(1, 1, self.alg)
            en0.load_animations('', self.tile_size)
            self.enemy_list.append(en0)
            self.ene_blocks.append(en0)
            self.player.life = False
        else:
            self.player.life = False
        self.main()

    def draw(self):
        self.display.fill(BACKGROUND)
        for i,vali in enumerate(self.grid):
            for j,valj in enumerate(vali):

                self.display.blit(self.terrain_images[valj], (i * self.tile_size, j * self.tile_size, self.tile_size, self.tile_size))

        for b in self.bombs:
            self.display.blit(self.bomb_images[b.frame], (*(b.pos *self.tile_size), self.tile_size, self.tile_size))

        for expl in self.explosions:
            for sect in expl.sectors:
                self.display.blit(self.explosion_images[expl.frame], (*(np.array(sect) * self.tile_size), self.tile_size, self.tile_size))
       
        if self.player.life:
            self.display.blit(self.player.animation[self.player.direction][self.player.frame],
                (self.player.x * (self.tile_size / self.player.step), self.player.y * (self.tile_size / self.player.step), self.tile_size, self.tile_size))
        # for en in enemy_list:
        #     if en.life:
        #         self.display.blit(en.animation[en.direction][en.frame],
        #             (en.posX * (self.tile_size / 4), en.posY * (self.tile_size / 4), self.tile_size, self.tile_size))
        #         if show_path:
        #             if en.algorithm == Algorithm.DFS:
        #                 for sek in en.path:
        #                     pygame.draw.rect(s, (255, 0, 0, 240), [sek[0] * self.tile_size, sek[1] * self.tile_size, self.tile_size, self.tile_size], 1)
        #             else:
        #                 for sek in en.path:
        #                     pygame.draw.rect(s, (255, 0, 255, 240), [sek[0] * self.tile_size, sek[1] * self.tile_size, self.tile_size, self.tile_size], 1)

        pygame.display.update()


    def generate_map(self):
        print("in")
        self.gridSearch(self.player.get_coords())
        print(self.player.get_coords())
        count = 0
        while(np.sum(self.reachable) < np.sum(self.grid == 1)*(1-(self.wall_chance+.2))):
            count+=1
            print(count,np.prod(self.grid_size-2))
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
                    self.grid[i,j]=4
                if self.grid[i,j] != 0 or (coords:=self.player.get_coords()) == (i,j) or not self.reachable[i,j] or \
                    sum(abs(np.array(coords)-np.array([i,j])))-1 < 2:
                    continue
                if np.random.uniform() < self.box_chance:
                    self.grid[i,j] = 2
        
        
        return


    def main(self):
        self.generate_map()
        while self.player.life:
            dt = self.clock.tick(15)
            # for en in enemy_list:
            #     en.make_move(grid, bombs, explosions, ene_blocks)
            keys = pygame.key.get_pressed()
            temp = self.player.direction
            movement = False
            if keys[pygame.K_DOWN]:
                temp = 0
                self.player.move(0, 1, self.grid, self.ene_blocks)
                movement = True
            elif keys[pygame.K_RIGHT]:
                temp = 1
                self.player.move(1, 0, self.grid, self.ene_blocks)
                movement = True
            elif keys[pygame.K_UP]:
                temp = 2
                self.player.move(0, -1, self.grid, self.ene_blocks)
                movement = True
            elif keys[pygame.K_LEFT]:
                temp = 3
                self.player.move(-1, 0, self.grid, self.ene_blocks)
                movement = True
            if temp != self.player.direction:
                self.player.frame = 0
                self.player.direction = temp
            if movement:
                if self.player.frame == 2:
                    self.player.frame = 0
                else:
                    self.player.frame += 1

            self.draw()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    sys.exit(0)
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_SPACE:
                        if self.player.bomb_limit == 0:
                            continue
                        temp_bomb = self.player.plant_bomb(self.grid)
                        self.bombs.append(temp_bomb)
                        self.grid[temp_bomb.x][temp_bomb.y] = 3
                        self.player.bomb_limit -= 1

            self.update_bombs(dt)
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
        self.reachable[start] = 4		# color starting point

        frontier = set()	# positions to be expanded
        frontier.add(start)
        expanded = True

        while expanded:
            expanded = False		# will remain False if no new positions are found
            new_frontier = set()	# will become next frontier
            for pos in frontier:
                for move in [(0,-1), (0,1), (-1,0), (1,0)]:
                    neighbour = tuple(np.array(pos)+np.array(move))
                    # print(move,pos,neighbour)
                    if self.reachable[neighbour] == 0:
                        # print(move,pos,neighbour)
                        new_frontier.add(neighbour)
                        expanded = True
                        self.reachable[neighbour] = 4	# color reachable position
            frontier = new_frontier
            # print(frontier)
        self.reachable = self.reachable==4

    def update_bombs(self,dt):
        for b in self.bombs:
            b.update(dt)
            if b.time < 1:
                b.bomber.bomb_limit += 1
                self.grid[b.x][b.y] = 0
                exp_temp = Explosion(b.x, b.y, b.range)
                exp_temp.explode(self.grid, self.bombs, b)
                exp_temp.clear_sectors(self.grid)
                self.explosions.append(exp_temp)
        # if self.player not in self.enemy_list:
        self.player.check_death(self.explosions)
        # for en in self.enemy_list:
        #     en.check_death(self.explosions)
        for expl in self.explosions:
            expl.update(dt)
            if expl.time < 1:
                self.explosions.remove(expl)


    def game_over(self):

        while True:
            dt = self.clock.tick(15)
            self.update_bombs(dt)
            count = 0
            winner = ""
            # for en in enemy_list:
            #     en.make_move(grid, bombs, explosions, ene_blocks)
            #     if en.life:
            #         count += 1
            #         winner = en.algorithm.name
            if count == 1:
                self.draw()
                textsurface = self.font.render(winner + " wins", False, (0, 0, 0))
                font_w = textsurface.get_width()
                font_h = textsurface.get_height()
                self.display.blit(textsurface, (self.display.get_width() // 2 - font_w//2,  self.display.get_height() // 2 - font_h//2))
                pygame.display.update()
                time.sleep(2)
                break
            if count == 0:
                self.draw()
                textsurface = self.font.render("Draw", False, (0, 0, 0))
                font_w = textsurface.get_width()
                font_h = textsurface.get_height()
                self.display.blit(textsurface, (self.display.get_width() // 2 - font_w//2, self.display.get_height() // 2 - font_h//2))
                pygame.display.update()
                time.sleep(2)
                break
            self.draw()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    sys.exit(0)
        self.explosions.clear()
        # self.enemy_list.clear()
        self.ene_blocks.clear()
