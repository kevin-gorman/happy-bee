import pygame
import random
import os
import time
import neat
import visualize
import pickle

WIDTH = 500
HEIGHT = 800
FLOOR = 700
BEST = 0

pygame.init()

FONT = pygame.font.SysFont("Avenir", 50)

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Happy Bee!")

sky_img = pygame.transform.scale(pygame.image.load(os.path.join("images","sky.png")).convert_alpha(), (500, 700))
ground_img = pygame.transform.scale(pygame.image.load(os.path.join("images","ground.png")).convert_alpha(),(500, 100))
pipe_img = pygame.transform.scale(pygame.image.load(os.path.join("images","pipe.png")).convert_alpha(), (400, 450))
bee_img = pygame.transform.scale(pygame.image.load(os.path.join("images","bee.png")).convert_alpha(), (50, 50))

gen = 0

LAST_HEIGHT = 250







def button_print(text, back_color, w, h, scale = 1):
    font = pygame.font.SysFont("Avenir", int(scale * 70))
    color = (175,175,175)
    button_width = scale * len(text) * 50
    button_height = scale * 100
    dim = [w - 0.5 * button_width, h - 0.5 * button_height, button_width, button_height]
    pygame.draw.rect(WINDOW, back_color, dim)

    label = font.render(text, 1, color)
    WINDOW.blit(label, (w - 0.5 * label.get_width(), h - 0.2 * button_height))
    pygame.display.update()
    return dim

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

def draw_window_train(win, bees, ground, pipes, score, gen, on_stop):
    win.blit(sky_img, (0,0))
    for pipe in pipes:
        pipe.draw(win)

    for bee in bees:
        bee.draw(win)
    ground.draw(win)
    score_label = FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIDTH - score_label.get_width() - 15, 10))
    gen_label = FONT.render("Gen: " + str(gen),1,(255,255,255))
    win.blit(gen_label, (WIDTH - gen_label.get_width() - 15, 50))
    pygame.display.update()
    if on_stop:
        button_print("STOP", (100,100,100), 75, 40, 0.5)
    else:
        button_print("STOP", (255,47,154), 75, 40, 0.5)

def draw_window(win, bees, ground, pipes, score, on_stop):
    win.blit(sky_img, (0,0))
    for pipe in pipes:
        pipe.draw(win)

    for bee in bees:
        bee.draw(win)
    ground.draw(win)
    score_label = FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIDTH - score_label.get_width() - 15, 10))
    pygame.display.update()
    if on_stop:
        button_print("STOP", (100,100,100), 75, 40, 0.5)
    else:
        button_print("STOP", (255,47,154), 75, 40, 0.5)

class Bee:
    """
    Bee object for Happy Bee
    """
    MAX_ROTATION = 25
    ROT_VEL = 20

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
        self.vel = -10 
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
            vert_displacement -= 1

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

class Pipe():
    """
    represents a pair of pipes
    """
    GAP = 200
    VEL = 6

    def __init__(self, x):
        """
        initialize pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.LOWER_PIPE = pygame.transform.flip(pipe_img, False, True)
        self.UPPER_PIPE = pipe_img

        self.passed = False

        self.set_height()

    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        global LAST_HEIGHT
        self.height = LAST_HEIGHT + random.randrange(-250, 250)
        if self.height < 75:
            self.height = random.randrange(75, 125)
        if self.height > 425:
            self.height = random.randrange(375, 425)
        LAST_HEIGHT = self.height
        #self.height = random.randrange(75, 425)
        self.top = self.height - self.UPPER_PIPE.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        move pipe based on vel
        :return: None
        """
        self.x -= self.VEL

    def draw(self, win):
        """
        draw both the top and bottom of the pipe
        :param win: pygame window/surface
        :return: None
        """
        # draw top
        win.blit(self.UPPER_PIPE, (self.x, self.top))
        # draw bottom
        win.blit(self.LOWER_PIPE, (self.x, self.bottom))


    def collide(self, bee, win):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        bee_mask = bee.get_mask()
        upper_mask = pygame.mask.from_surface(self.UPPER_PIPE)
        lower_mask = pygame.mask.from_surface(self.LOWER_PIPE)
        upper_offset = (self.x - bee.x, self.top - round(bee.y))
        lower_offset = (self.x - bee.x, self.bottom - round(bee.y))

        upper_overlap = bee_mask.overlap(upper_mask, upper_offset)
        lower_overlap = bee_mask.overlap(lower_mask, lower_offset)

        if upper_overlap or lower_overlap:
            return True

        return False

class Ground:
    """
    The ground of the game. Moves sideways
    """
    VEL = 6

    def __init__(self, y, img):
        """
        Initialize the object
        :param y: int
        :return: None
        """
        self.y = y
        self.x1 = 0
        self.x2 = WIDTH
        self.img = img

    def move(self):
        """
        move floor so it looks like its scrolling
        :return: None
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + WIDTH< 0:
            self.x1 = self.x2 + WIDTH

        if self.x2 + WIDTH < 0:
            self.x2 = self.x1 + WIDTH

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))

def play():
    bees = [Bee(230,350, bee_img)]
    ground = Ground(700, ground_img)
    pipes = [Pipe(700)]
    clock = pygame.time.Clock()
    score = 0

    stop_button = button_print("STOP", (255,47,154), 75, 40, 0.5)
    on_stop = False
    while(1):
        pygame.time.wait(10)
        clock.tick(20)
        ground.move()
        for bee in bees:
            bee.move()

            pipes_to_remove = []
            add_pipe = False
            for pipe in pipes:
                pipe.move()
                # check for collision
                if pipe.collide(bee, WINDOW):
                    bees.pop(bees.index(bee))
                    break


                if pipe.x + pipe.UPPER_PIPE.get_width() < 0:
                    pipes_to_remove.append(pipe)

                if not pipe.passed and (pipe.x + pipe.UPPER_PIPE.get_width()/2 - 50) < bee.x:
                    pipe.passed = True
                    add_pipe = True
            if add_pipe:
                score += 1
                # can add this line to give more reward for passing through a pipe (not required)
                pipes.append(Pipe(WIDTH - 150))
            
            if (bee.y > 650):
                bees.pop(bees.index(bee))
                break
                
        if (len(bees) == 0):
            break
        
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                break
            if event.type == pygame.KEYDOWN:
                if pygame.K_SPACE:
                    bees[0].flap()
            if stop_button[0] < mouse[0] < stop_button[0] + stop_button[2] and \
                stop_button[1] < mouse[1] < stop_button[1] + stop_button[3]:
                on_stop = True
            else:		
                on_stop = False
            if pygame.mouse.get_pressed()[0]:
                if stop_button[0] < mouse[0] < stop_button[0] + stop_button[2] and \
                    stop_button[1] < mouse[1] < stop_button[1] + stop_button[3]:
                        return;

        draw_window(WINDOW, bees, ground, pipes, score, on_stop)



def eval_genomes(genomes, config):
    """
    take a genome and run the bees in the simulation
    until they are all dead, then evaluate their 
    fitness based on how far they got
    """
    global gen, WINDOW, BEST
    gen += 1

    bees = [] # a list of bees for the current generation
    neural_nets = [] # a list of each bee's neural net
    genomes_dynamic = [] # a changing list of the genomes


    for genome_id, genome in genomes:
        genome.fitness = 0 
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        neural_nets.append(net)
        bees.append(Bee(230,350, bee_img))
        genomes_dynamic.append(genome)


    ground = Ground(700, ground_img)
    pipes = [Pipe(500)]
    clock = pygame.time.Clock()
    score = 0

    stop_button = button_print("STOP", (255,47,154), 75, 40, 0.5)
    on_stop = False
    while(1):
        
        clock.tick(20)
        ground.move()

        pipe_num = 0 # Which set of pipes the bees should look at 
        if len(pipes) > 1 and bees[0].x > pipes[0].x + pipes[0].UPPER_PIPE.get_width()/2 - 50: 
            pipe_num = 1  # If the first pipe is passed, the bees should look at the second

        for i, bee in enumerate(bees):
            genomes_dynamic[i].fitness += 0.1
            action = neural_nets[i].activate((bee.y, bee.y - pipes[pipe_num].height, bee.y - pipes[pipe_num].bottom))

            if action[0] > 0.75:  # used sigmoid, so try .75 as threashold for flap or not
                bee.flap()
            bee.move()

            pipes_to_remove = []
            add_pipe = False

            if (bee.y > 650 or bee.y < 50):
                if score > 20 and score > BEST:
                    BEST = score
                    pickle.dump(neural_nets[i],open("best.pickle", "wb"))
                genomes_dynamic.pop(i)
                neural_nets.pop(i)
                bees.pop(i)
                continue

            for pipe in pipes:
                # check for collision
                if pipe.collide(bee, WINDOW):
                    if score > 20 and score > BEST:
                        BEST = score
                        pickle.dump(neural_nets[i],open("best.pickle", "wb"))
                    genomes_dynamic.pop(i)
                    neural_nets.pop(i)
                    bees.pop(i)
                    break

        if (len(bees) == 0):
            break

        for pipe in pipes:
            pipe.move()
            if pipe.x + pipe.UPPER_PIPE.get_width() - 150 < 0:
                pipes_to_remove.append(pipe)

            if not pipe.passed and (pipe.x + pipe.UPPER_PIPE.get_width()/2 - 50) < bees[0].x:
                pipe.passed = True
                add_pipe = True

        for pipe in pipes_to_remove:
            pipes.remove(pipe)

        if add_pipe:
            score += 1
            # can add this line to give more reward for passing through a pipe (not required)
            pipes.append(Pipe(WIDTH - 150))
        
            for genome in genomes_dynamic:
                genome.fitness += 5
        
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                break
            if stop_button[0] < mouse[0] < stop_button[0] + stop_button[2] and \
                stop_button[1] < mouse[1] < stop_button[1] + stop_button[3]:
                on_stop = True
            else:		
                on_stop = False
            if pygame.mouse.get_pressed()[0]:
                if stop_button[0] < mouse[0] < stop_button[0] + stop_button[2] and \
                    stop_button[1] < mouse[1] < stop_button[1] + stop_button[3]:
                        if len(genomes_dynamic) > 0:
                            genomes_dynamic[0].fitness = 1001
                        return;

        draw_window_train(WINDOW, bees, ground, pipes, score, gen, on_stop)

def watch(pickle_name):
    file = open(pickle_name, 'rb')
    net = pickle.load(file)
    file.close()

    bee = Bee(230,350, bee_img)
    ground = Ground(700, ground_img)
    pipes = [Pipe(700)]
    clock = pygame.time.Clock()
    score = 0
    run = True

    stop_button = button_print("STOP", (255,47,154), 75, 40, 0.5)
    on_stop = False
    while(run):

        pipe_num = 0 # Which set of pipes the bees should look at 
        if len(pipes) > 1 and bee.x > pipes[0].x + pipes[0].UPPER_PIPE.get_width()/2 + 25: 
            pipe_num = 1  # If the first pipe is passed, the bees should look at the second
        
        pygame.draw.line(WINDOW,(255, 0, 0),(bee.x + 40,bee.y + 25),
            (pipes[pipe_num].x + pipes[0].UPPER_PIPE.get_width()/2, pipes[pipe_num].height), 2)
        pygame.draw.line(WINDOW,(255, 0, 0),(bee.x + 40,bee.y + 25),
            (pipes[pipe_num].x + pipes[0].UPPER_PIPE.get_width()/2, pipes[pipe_num].bottom), 2)
        pygame.display.update()

        action = net.activate((bee.y, bee.y - pipes[pipe_num].height, bee.y - pipes[pipe_num].bottom))

        if action[0] > 0.75:  # used sigmoid, so try .75 as threashold for flap or not
            bee.flap()
        bee.move()

        clock.tick(20)
        ground.move()

        pipes_to_remove = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            # check for collision
            if pipe.collide(bee, WINDOW):
                run = False
                break


            if pipe.x + pipe.UPPER_PIPE.get_width() - 150 < 0:
                pipes_to_remove.append(pipe)

            if not pipe.passed and (pipe.x + pipe.UPPER_PIPE.get_width()/2 - 50) < bee.x:
                pipe.passed = True
                add_pipe = True

        for pipe in pipes_to_remove:
            pipes.remove(pipe)

        if add_pipe:
            score += 1
            # can add this line to give more reward for passing through a pipe (not required)
            pipes.append(Pipe(WIDTH - 150))
        
        if (bee.y > 650 or bee.y < 50):
            break

        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                break
            if stop_button[0] < mouse[0] < stop_button[0] + stop_button[2] and \
                stop_button[1] < mouse[1] < stop_button[1] + stop_button[3]:
                on_stop = True
            else:		
                on_stop = False
            if pygame.mouse.get_pressed()[0]:
                if stop_button[0] < mouse[0] < stop_button[0] + stop_button[2] and \
                    stop_button[1] < mouse[1] < stop_button[1] + stop_button[3]:
                        return;

        draw_window(WINDOW, [bee], ground, pipes, score, on_stop)



def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))



play_button = button_print("PLAY", (255,47,154), WIDTH/2, HEIGHT/2 - 50, 0.5)
train_button = button_print("TRAIN", (155,75,160), WIDTH/2, HEIGHT/2 + 25, 0.5)
watch_button = button_print("WATCH", (0,121,231), WIDTH/2, HEIGHT/2 + 100, 0.5)

on_play = False
on_train = False
on_watch = False
while(1):
    
    WINDOW.blit(sky_img, (0,0))
    WINDOW.blit(ground_img, (0,700))
    hb_label = FONT.render("HAPPY BEE!",1,(255,173,47))
    WINDOW.blit(hb_label, (WIDTH/2 - 100, HEIGHT/4))


    mouse = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if play_button[0] < mouse[0] < play_button[0] + play_button[2] and \
            play_button[1] < mouse[1] < play_button[1] + play_button[3]:
            play_button = button_print("PLAY", (100,100,100),  WIDTH/2, HEIGHT/2 - 50, 0.5)
            on_play = True
        else:		
            play_button = button_print("PLAY", (255,47,154),  WIDTH/2, HEIGHT/2 - 50, 0.5)
            on_play = False
        if train_button[0] < mouse[0] < train_button[0] + train_button[2] and \
            train_button[1] < mouse[1] < train_button[1] + train_button[3]:
            train_button = button_print("TRAIN", (100,100,100),  WIDTH/2, HEIGHT/2 + 25, 0.5)
            on_train = True
        else:		
            train_button = button_print("TRAIN", (155,75,160),  WIDTH/2, HEIGHT/2 + 25, 0.5)
            on_train = False
        if watch_button[0] < mouse[0] < watch_button[0] + watch_button[2] and \
            watch_button[1] < mouse[1] < watch_button[1] + watch_button[3]:
            watch_button = button_print("WATCH", (100,100,100),  WIDTH/2, HEIGHT/2 + 100, 0.5)
            on_watch = True
        else:		
            watch_button = button_print("WATCH", (0,121,231),  WIDTH/2, HEIGHT/2 + 100, 0.5)
            on_watch = False
        if pygame.mouse.get_pressed()[0]:
            if play_button[0] < mouse[0] < play_button[0] + play_button[2] and \
                play_button[1] < mouse[1] < play_button[1] + play_button[3]:
                    play()
                    break;
            elif train_button[0] < mouse[0] < train_button[0] + train_button[2] and \
                train_button[1] < mouse[1] < train_button[1] + train_button[3]:
                    run('happy-bee-config.ini')
                    break;
            elif watch_button[0] < mouse[0] < watch_button[0] + watch_button[2] and \
                watch_button[1] < mouse[1] < watch_button[1] + watch_button[3]:
                    watch('best.pickle')
                    break;
    else:
        if on_play:
            play_button = button_print("PLAY", (100,100,100), WIDTH/2, HEIGHT/2 - 50, 0.5)
        else:
            play_button = button_print("PLAY", (255,47,154),  WIDTH/2, HEIGHT/2 - 50, 0.5)
        if on_train:
            train_button = button_print("TRAIN", (100,100,100), WIDTH/2, HEIGHT/2 + 25, 0.5)
        else:
            train_button = button_print("TRAIN", (155,75,160),  WIDTH/2, HEIGHT/2 + 25, 0.5)
        if on_watch:
            watch_button = button_print("WATCH", (100,100,100), WIDTH/2, HEIGHT/2 + 100, 0.5)
        else:
            watch_button = button_print("WATCH", (0,121,231),  WIDTH/2, HEIGHT/2 + 100, 0.5)
    pygame.display.update()

'''
if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'happy-bee-config.ini')
    run(config_path)
'''