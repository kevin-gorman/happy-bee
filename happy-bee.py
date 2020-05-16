import pygame
import random
import os
import time
import neat
#import visualize
import pickle

WIDTH = 550
HEIGHT = 800
FLOOR = 700

pygame.init()

FONT = pygame.font.SysFont("Avenir", 50)

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Happy Bee!")

sky_img = pygame.transform.scale(pygame.image.load(os.path.join("images","sky.png")).convert_alpha(), (550, 700))
ground_img = pygame.transform.scale2x(pygame.image.load(os.path.join("images","ground.png")).convert_alpha())
pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("images","pipe.png")).convert_alpha())
#bee_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("images","bee" + str(x) + ".png"))) for x in range(1,4)]
bee_img = pygame.transform.scale(pygame.image.load(os.path.join("images","bee.png")).convert_alpha(), (50, 50))
#bee_img = pygame.image.load(os.path.join("images","bee2.png"))

gen = 0

def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds):
    win.blit(sky_img, (0,0))
    for bee in bees:
        bee.draw(win)
    pygame.display.update()

class Bee:
    """
    Bee object for Happy Bee
    """
    MAX_ROTATION = 25
    ROT_VEL = 10

    def __init__(self, x, y, img):
        """
        Initialize the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.x = x
        self.y = y
        self.tilt = 0  # degrees to tilt
        self.tick_count = 0 # time since last flap
        self.vel = 0 # downward velocity (positive is downward)
        self.img = img

    def flap(self):
        """
        flap the bee upward
        :return: None
        """
        self.vel = -12
        self.tick_count = 0

    def move(self):
        """
        move the bee
        :return: None
        """
        self.tick_count += 1

        vert_displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculate displacement

        # terminal velocity
        if vert_displacement >= 16:
            vert_displacement = (vert_displacement/abs(vert_displacement)) * 16

        elif vert_displacement < 0:
            vert_displacement -= 2

        self.y = self.y + vert_displacement

        #if vert_displacement < 0 or self.y < self.height + 50:  # tilt up
        if vert_displacement < 0: # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def get_mask(self):
        """
        get the mask for the bee
        :return: None
        """
        return pygame.mask.from_surface(self.img)

    def draw(self, window):
        """
        draw the bee
        :param window: pygame surface to draw the bee on
        :return: None
        """

        # tilt the bird
        blitRotateCenter(window, self.img, (self.x, self.y), self.tilt)

bees = [Bee(130,350, bee_img)]
run = 1
while(run):
    for bee in bees:
        bee.move()
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            quit()
            break
        if event.type == pygame.KEYDOWN:
            if pygame.K_SPACE:
                bee.flap()
    draw_window(WINDOW, bees)


        
