import pygame, neat, os, random
pygame.font.init()  # init font
pygame.init()



def re_size(x):
    size = (int(x[0]*RELATIVE_PERCENT),int(x[1]*RELATIVE_PERCENT))
    return size


def load_and_convert(path):
    img = pygame.image.load(path).convert_alpha()
    return img


STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)

GRAVITY = 1/4
FPS = 1200
RELATIVE_PERCENT=.75
BASE_Y = 900*RELATIVE_PERCENT
SCREEN_SIZE = (WIDTH,HEIGHT) = re_size((576,1024))
SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()

PIPE_IMG = pygame.transform.scale(load_and_convert('Images/pipe.png'),re_size((104,640)))
BG_IMG = pygame.transform.scale(load_and_convert('Images/background-day.png'), SCREEN_SIZE)
BIRD_IMGS = [pygame.transform.scale(pygame.image.load(os.path.join("Images","bird" + str(x) + ".png")),re_size((68,48))) for x in range(1,4)]
BASE_IMG = pygame.transform.scale(load_and_convert('Images/base.png'),re_size((672,224)))

class Bird(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.vel = 0
        self.imgIndex = 0
        self.img = BIRD_IMGS[self.imgIndex]
        self.rect = self.img.get_rect(center = (x,self.y))
    
    def jump(self):
        self.vel = 0
        self.vel -= 11*RELATIVE_PERCENT
        self.y += self.vel

    def draw(self):
        self.vel += GRAVITY
        self.y += self.vel
        self.rotate_n_animate()
        SCREEN.blit(self.img,self.rect)

    def rotate_n_animate(self):
        if not self.vel:
            self.imgIndex = 0
        elif self.vel>0:
            self.imgIndex = 2
        else:
            self.imgIndex = 1
        self.img = BIRD_IMGS[self.imgIndex]
        self.img = pygame.transform.rotozoom(self.img,-self.vel * 3,1)
        self.rect = self.img.get_rect(center = (self.x,self.y))
        

PIPES = [PIPE_IMG,pygame.transform.flip(PIPE_IMG, False, True)]
PIPES_HEIGHT = [value*RELATIVE_PERCENT for value in [400,600,800]]
score = 0

class Pipe(object):
    def __init__(self,x):
        self.x = x
        self.vel = 5*RELATIVE_PERCENT
        self.height = random.randrange(int(400*RELATIVE_PERCENT), int(HEIGHT-200*RELATIVE_PERCENT))
        self.bottomY = self.height + 300*RELATIVE_PERCENT
        self.topY = self.height - PIPE_IMG.get_height()
        self.bottomRect = PIPES[0].get_rect(center = (self.x+PIPE_IMG.get_width()//2,self.bottomY))
        self.topRect = PIPES[1].get_rect(center = (self.x+PIPE_IMG.get_width()//2,self.topY))
        
        
    def draw(self):
        self.move()
        SCREEN.blit(PIPES[0],self.rects()[0])
        SCREEN.blit(PIPES[1],self.rects()[1])

    def move(self):
        self.x -= self.vel
        if self.x+PIPE_IMG.get_width()<0:
            global pipe,score
            pipe = Pipe(WIDTH)
            self.x = WIDTH
            score+=1


    def rects(self):
        self.bottomRect = PIPES[0].get_rect(center = (self.x+PIPE_IMG.get_width()//2,self.bottomY))
        self.topRect = PIPES[1].get_rect(center = (self.x+PIPE_IMG.get_width()//2,self.topY))
        return self.bottomRect,self.topRect
    
    
pipe = Pipe(WIDTH)
gen = 0
birds =  []

def main(genomes,config):
    global gen
    gen+=1

    nets = []
    birds = []
    ge = []

    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(100*RELATIVE_PERCENT,random.randint(0,HEIGHT//2)))
        ge.append(genome)
    
    baseX = 0
    score = 0
    previous_score = score

    canScore = True
    running = True
    
    while running and len(birds)>0:
        SCREEN.blit(BG_IMG,(0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        for x, bird in enumerate(birds):
            ge[x].fitness += 0.1
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipe.topY), abs(bird.y - pipe.bottomY)))
            if output[0] > 0.5:
                bird.jump()
            

        #Drawing objects
        for bird in birds:
            bird.draw()
        pipe.draw()

        #Scoring mechanics
        if bird.x-5<pipe.x<bird.x+5 and canScore:
            score+=1
            canScore = False
        if pipe.x<0:
            canScore=True

        #Collision check
        pipes = [pipe.topRect,pipe.bottomRect]
        for bird in birds:
            if bird.rect.colliderect(pipes[0]) or bird.rect.colliderect(pipes[1]):
                ge[birds.index(bird)].fitness -= 1
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

            if len(birds)>0:
                if not BIRD_IMGS[0].get_height()<bird.rect.bottom<BASE_Y:
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))
        

        if score>previous_score:
            previous_score = score
            for genome in ge:
                genome.fitness += 5

        #Base stuff
        baseX -= 5*RELATIVE_PERCENT
        if baseX<-WIDTH:
            baseX = 0
        SCREEN.blit(BASE_IMG,(baseX,BASE_Y))
        SCREEN.blit(BASE_IMG,(baseX+WIDTH,BASE_Y))

        # score
        score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
        SCREEN.blit(score_label, (WIDTH - score_label.get_width() - 15, 10))

        # generations
        score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
        SCREEN.blit(score_label, (10, 10))

        # alive
        score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
        SCREEN.blit(score_label, (10, 50))
        
        #Updating display
        pygame.display.update()
        clock.tick(FPS)


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
