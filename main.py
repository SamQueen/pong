import math
import os
import pygame
import neat

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 150
PADDLE_HEIGHT = 10

# create window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def num_to_range(num, inMin, inMax):
    outMin = 0
    outMax = 0.8
    return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin))


# game loop eval genomes
def main(genomes, config):
    nets = []
    ge = []
    paddles = []
    
    pong_x_pos = SCREEN_WIDTH / 2
    pong_y_pos = SCREEN_HEIGHT / 2
    pong_x_vel = 0
    pong_y_vel = -0.5
    pong_width = 20
    hits = 0

    for genome_id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        pad = pygame.Rect(300, 0, PADDLE_WIDTH, PADDLE_HEIGHT) # xpos, ypos, width, height
        paddles.append(pad)
        g.fitness = 0
        ge.append(g)

    # create display objects
    paddle2 = pygame.Rect(0, 575, PADDLE_WIDTH, PADDLE_HEIGHT) # xpos, ypos, width, height
    pong = pygame.Rect(pong_x_pos, pong_y_pos/2, pong_width, pong_width) # xpos, ypos, width, height


    #run the game
    for x, paddle in enumerate(paddles):
        run = True
        print("newPaddle")
        paddle1 = pygame.Rect(300, 10, PADDLE_WIDTH, PADDLE_HEIGHT) # xpos, ypos, width, height

        while run:
            # refresh screeen
            screen.fill((0,0,0))
            
            pygame.draw.rect(screen, (255, 0, 0), paddle1)
            pygame.draw.rect(screen, (255, 0, 0), paddle2)
            pygame.draw.ellipse(screen, (255, 0, 0), pong)

            # update pong speed depending on hits
            if hits == 5:
                if pong_y_vel < 0:
                    pong_y_vel = 0.8 * (-1)
                else:
                    pong_y_vel = 0.8
            if hits == 10:
                if pong_y_vel < 0:
                    pong_y_vel = 1 * (-1)
                else:
                    pong_y_vel = 1

            # pong collision detection
            if pong.y == PADDLE_HEIGHT + 10:
                
                if (pong.x + pong_width) >= paddle1.x and pong.x <= paddle1.x + PADDLE_WIDTH:
                    hits += 1
                    print("hits " + str(hits)  +" speed " + str(pong_y_vel) )
                    
                    #adjust fitness
                    ge[x].fitness += 5

                    # calc trajectory of pong
                    mid = paddle1.x + (PADDLE_WIDTH / 2)
                    diff = abs(mid - pong.x)
                    angle = num_to_range(diff, 0, PADDLE_WIDTH)
                    if pong_x_vel > 0:
                        pong_x_vel = angle
                    else:
                        pong_x_vel = angle * (-1)
                    pong_y_vel = pong_y_vel * (-1)

            elif pong.y == 557:
                pong_y_vel = pong_y_vel * (-1)
            elif pong.y < -100 or pong.y > 610:
                # loooser
                pong_x_pos = SCREEN_WIDTH / 2
                pong_y_pos = SCREEN_HEIGHT / 2
                pong_x_vel = 0
                pong_y_vel = 0.5
                hits = 0

                # remove from population when you
                ge[x] -= 1 # adjust finess score
                paddles.pop(x)
                nets.pop(x)
                ge.pop(x)
                running = False

            if pong.x <= 0:
                pong_x_vel = pong_x_vel * (-1)
            elif (pong.x + pong_width) >= SCREEN_WIDTH:
                pong_x_vel = pong_x_vel * (-1)

            # update pong position
            pong_y_pos += pong_y_vel
            pong_x_pos += pong_x_vel
            pong.y = pong_y_pos
            pong.x = pong_x_pos

            # get distance of pong from paddle
            x_dis = abs(pong.x - paddle1.x)
            y_dis = abs(pong.y - paddle1.y)
            distance = math.sqrt(pow(x_dis, 2) + pow(y_dis, 2))
            print("disatnce " + str(distance))

            # move ai paddle

            #ge[x].fitness += 1
            #output = net[x].activate((pong.x, pong.y, distance))

            if pong.x < paddle1.x:
                paddle1.move_ip(-1, 0)
            elif pong.x > paddle1.x:
                paddle1.move_ip(1, 0)

            
            
            
            # add controls
            """ key = pygame.key.get_pressed()
            if key[pygame.K_a] == True and paddle1.x > 0:
                paddle1.move_ip(-1, 0)
            elif key[pygame.K_d] == True and paddle1.x < (SCREEN_WIDTH - PADDLE_WIDTH):
                paddle1.move_ip(1, 0) """

            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    run = False

            # update display
            pygame.display.update()

    pygame.quit()

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    
    pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    winner = pop.run(main, 50)
    

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)