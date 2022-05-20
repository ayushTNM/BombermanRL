import pygame
from environment import Environment
import time
from agent import Player, PrioritizedSweepingAgent,Random
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
        self.grid_size = grid_size
        self.render = True
        self.images=images
        self.box_chance = box_chance if 0<=box_chance<=1 else box_chance/100
        self.wall_chance = wall_chance if 0<=wall_chance<=1 else wall_chance/100
        self.agent = None
        self.grid_size = grid_size
        self.alg = "Player"
        self.tile_size = tile_size
        self.wait_bg = False

        pygame.font.init()
        self.font = pygame.font.SysFont('Bebas', 100)
        self.display = pygame.display.set_mode(self.grid_size*self.tile_size)
        pygame.display.set_caption('Bomberman')
        self.clock = pygame.time.Clock()

        self.winSurface = self.font.render("Win", False, (0, 0, 0))
        self.loseSurface = self.font.render("Lose", False, (0, 0, 0))
        self.waitSurface = self.font.render("Please Wait", False, (0, 0, 0))

        self.loadedImgs = {}
        for img in self.images:
            imgName=img.replace("\\","/").split("/")
            if (folder:=imgName[-2]) not in self.loadedImgs.keys():
                self.loadedImgs.update({folder:{}})
            loadedImg = pygame.image.load(img)
            scaledImg = pygame.transform.scale(loadedImg, (tile_size, tile_size))
            self.loadedImgs[folder].update({imgName[-1].split('.')[-2]:scaledImg})
        
        # print(self.loadedImgs)

    def set_alg(self,_,c):
        self.alg = c

    def set_render(self,_,c):
        self.render = c

    def draw(self):
        
        if self.render or self.alg == "Player" or self.wait_bg:
            self.display.fill(BACKGROUND)
            self.env.render(self.loadedImgs,self.tile_size,self.display)

            if self.agent.life:
                # print(self.agent.direction,self.agent.frame)
                self.display.blit(self.agent.animation[self.agent.direction][self.agent.frame],
                    (self.agent.x * (self.tile_size / self.agent.step), self.agent.y * (self.tile_size / self.agent.step), self.tile_size, self.tile_size))
            if self.wait_bg:
                font_w = self.waitSurface.get_width()
                font_h = self.waitSurface.get_height()
                self.display.blit(self.waitSurface, (self.display.get_width() // 2 - font_w//2,  self.display.get_height() // 2 - font_h//2))
                self.wait_bg = False

            pygame.display.update()

    def main(self):
        iterations = 1
        episodes = 1000

        Lr = 1
        Gamma = 0.99
        Epsilon = 0.1
        n_planning_updates=10

        for box_count in np.arange(1,8):
            self.wait_bg = 1-self.render
            
            if self.alg == "Player":
                self.env = Environment(*self.grid_size,self.wall_chance,self.box_chance)
            elif self.alg == "PrioritizedSweepingAgent":
                self.env = Environment(*self.grid_size,self.wall_chance,box_count=box_count,seed=42)
            else:
                self.env = Environment(*self.grid_size,self.wall_chance,box_count=box_count)

            data = {"Player":[Player, 15, [(self.env.x,self.env.y)], self.loadedImgs["player"]],
                    "PrioritizedSweepingAgent":[PrioritizedSweepingAgent, 0, 
                    [self.env.n_states,self.env.action_size(),Lr,Gamma,(self.env.x,self.env.y)], 
                    self.loadedImgs["agent"]],
                    None:[Random, 0, [(self.env.x,self.env.y)], self.loadedImgs["agent"]]}

            agent,fps,args,imgs = data[self.alg]

            best_c_r = float('-inf')
            actions=None
            for _ in range(iterations):
                self.agent = agent(*args)
                self.agent.load_animations(imgs)

                for ep in range(episodes):
                    n_a=0
                    c_r = 0
                    best_actions = []
                    self.agent,s = self.env.reset(self.agent)
                    self.draw()
                    while self.agent.life and 2 in self.env.grid:
                    
                        self.clock.tick(fps)
                        dt = self.clock.get_fps()

                        a = self.agent.select_action(s,Epsilon)
                        best_actions.append(a)
                        n_a+=1
                        
                        reward,next_state = self.env.step(a,self.agent,dt,self.draw)
                        if self.agent.type == "PrioritizedSweepingAgent":
                            done = len(np.unique(self.env.grid, return_counts=True)[1]) == 2
                            self.agent.update(s,a,reward,next_state,done,n_planning_updates)
                        s = next_state
                        c_r+=reward

                    if c_r > best_c_r and self.agent.type == "PrioritizedSweepingAgent":
                        best_c_r = c_r
                        actions = best_actions

                    if self.agent.type ==  "Player":
                        self.game_over(fps)
                        break
                    elif self.agent.type == "PrioritizedSweepingAgent":
                        while True:
                            if done:
                                break
                            self.env.step(4,self.agent,dt,self.draw)
                        print("episode: ",ep, n_a,"reward:", c_r)
                else:
                    print("Done")
                    continue
                break
            else:
                if actions != None:
                    self.render_best(actions,best_c_r)
                continue
            break

    def render_best(self,actions,r):
        bkprender = self.render
        self.render = True
        self.env.reset(self.agent)
        self.draw()
        time.sleep(1)
        print("least steps:",len(actions),"bombs:",sum(np.array(actions)==5),"r:",r)
        while len(actions)>0:
            self.clock.tick(15)
            dt = self.clock.get_fps()
            self.env.step(actions[0],self.agent,dt,self.draw)
            actions.pop(0)
            self.draw()
        self.game_over(15)
        self.render =bkprender


    def game_over(self,fps):
        self.clock.tick(fps)
        dt = self.clock.get_fps()
        self.env.update_bombs(dt)
        _,counts = np.unique(self.env.grid, return_counts=True)
        # winner = ""
        self.draw()
        if len(counts) == 2:
            font_w = self.winSurface.get_width()
            font_h = self.winSurface.get_height()
            self.display.blit(self.winSurface, (self.display.get_width() // 2 - font_w//2,  self.display.get_height() // 2 - font_h//2))
            pygame.display.update()
            time.sleep(2)
            # break
        else:
            font_w = self.loseSurface.get_width()
            font_h = self.loseSurface.get_height()
            self.display.blit(self.loseSurface, (self.display.get_width() // 2 - font_w//2, self.display.get_height() // 2 - font_h//2))
            pygame.display.update()
            time.sleep(2)
            # break
        self.draw()
