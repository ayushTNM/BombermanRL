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
    def __init__(self,grid_size, tile_size):

        # print(grid)
        self.player = None
        self.grid_size = grid_size
        self.alg = Algorithm.PLAYER
        self.path = True
        self.tile_size = tile_size
        pygame.font.init()
        self.font = pygame.font.SysFont('Bebas', self.tile_size)
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

        self.terrain_images = [grass_img, block_img, box_img, grass_img,bomb3_img]
        self.bomb_images = [bomb1_img, bomb2_img, bomb3_img]
        self.explosion_images = [explosion1_img, explosion2_img, explosion3_img]

    def set_alg(self,value,c):
        self.alg = c
        print(self.alg)

    def set_path(self,value,c):
        self.path = c
        

    def run(self):

        self.grid = np.zeros(tuple(self.grid_size),dtype=int)
        self.grid[:,[0,-1]] = self.grid[[0,-1]] = 1             #set edges to walls
        self.grid[1:self.grid.shape[0]-1,1:self.grid.shape[1]-1] = np.random.rand(*(self.grid_size-2)) < 0.18
        self.reachable = np.zeros(tuple(self.grid_size),dtype=bool)
        # print(list(zip(*np.where(self.grid==0))))
        self.free_idxs = list(zip(*np.where(self.grid==0)))
        (x,y) = self.free_idxs[np.random.randint(len(self.free_idxs))]
        print(self.grid)
        print(x,y)
        self.player = Player((x*4,y*4),-1)
        # self.enemy_list = []
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
                # print(valj)
                self.display.blit(self.terrain_images[valj], (i * self.tile_size, j * self.tile_size, self.tile_size, self.tile_size))

        for b in self.bombs:
            self.display.blit(self.bomb_images[b.frame], (*(b.pos *self.tile_size), self.tile_size, self.tile_size))

        for expl in self.explosions:
            for sect in expl.sectors:
                self.display.blit(self.explosion_images[expl.frame], (*(np.array(sect) * self.tile_size), self.tile_size, self.tile_size))
       
        if self.player.life:
            self.display.blit(self.player.animation[self.player.direction][self.player.frame],
                (self.player.x * (self.tile_size / 4), self.player.y * (self.tile_size / 4), self.tile_size, self.tile_size))
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
        # print(grid)
        # grid[]
        # self.grid[self.reachable]=0
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if self.grid[i][j] != 0 or self.player.get_coords() == (i,j) or (i,j) not in self.free_idxs:
                    continue
                # elif (i < 3 or i > len(grid) - 4) and (j < 3 or j > len(grid[i]) - 4):
                #     continue
                # if np.random.uniform() < .18:
                #     self.grid[i,j] = 1
                # self.DFS(*self.player.get_coords())
                if np.random.uniform() < .32:
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
