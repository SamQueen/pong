import math
import os
import pygame
import neat
import random
import pickle

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 150
PADDLE_HEIGHT = 10

# create window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def remove_from_array(paddle_arr, indexes):
    indexes.sort(reverse = True)

    for index in indexes:
        if 0 <= index < len(paddle_arr):
            paddle_arr.pop(index)


def eval_genomes(genomes, config):
    paddles = []
    nets = []
    ge = []
    distances = []

    print("starting " + str(len(genomes)))

    # track neural network and genome fitness
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        paddles.append(pygame.Rect(300, 10, PADDLE_WIDTH, PADDLE_HEIGHT))
        genome.fitness = 0
        ge.append(genome)
    
    for genome in genomes:
        distances.append(100)

    pong_x_pos = SCREEN_WIDTH / 2
    pong_y_pos = SCREEN_HEIGHT / 2
    pong_x_vel = 0
    pong_y_vel = -0.7 #0.5    
    pong_width = 20
    hits = 0

    # create display objects
    paddle2 = pygame.Rect(300, 575, PADDLE_WIDTH, PADDLE_HEIGHT) # xpos, ypos, width, height
    pong = pygame.Rect(pong_x_pos, pong_y_pos/2, pong_width, pong_width) # xpos, ypos, width, height

    run = True

    while run:
        paddles_remove = []
        # refresh screeen
        screen.fill((0,0,0))

        for paddle1 in paddles:
            pygame.draw.rect(screen, (255, 0, 0), paddle1)

        pygame.draw.rect(screen, (255, 0, 0), paddle2)
        pygame.draw.ellipse(screen, (255, 0, 0), pong)

        # pong collision detection
        if pong.y == PADDLE_HEIGHT + 10:
            hit = False
            
            for x, paddle1 in enumerate(paddles):
                if (pong.x + pong_width) >= paddle1.x and pong.x <= paddle1.x + PADDLE_WIDTH:
                    hit = True

                    # add fitness
                    ge[x].fitness += 5
                else:
                    # subtract fitness
                    ge[x].fitness -= 1
                    paddles_remove.append(x)

            # remove the chosen paddels
            remove_from_array(paddles, paddles_remove)
            remove_from_array(nets, paddles_remove)
            remove_from_array(distances, paddles_remove)
            remove_from_array(ge, paddles_remove)

            # calc trajectory of pong
            if hit:
                pong_y_vel = pong_y_vel * (-1)

        elif pong.y == 557:   
            if (pong.x + pong_width) >= paddle2.x and pong.x <= paddle2.x + PADDLE_WIDTH:
                hits += 1

                # calc trajectory of pong
                angle = random.uniform(0, 0.8)

                if pong_x_vel > 0:
                    pong_x_vel = angle
                else:
                    pong_x_vel = angle * (-1)
                pong_y_vel = pong_y_vel * (-1)

        elif pong.y < -100 or pong.y > 610:
            # loooser
            pong_x_pos = SCREEN_WIDTH / 2
            pong_y_pos = SCREEN_HEIGHT / 2
            pong_x_vel = 0
            pong_y_vel = 0.7
            hits = 0

        # check if pong hits side of screen
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
        for x, paddle1 in enumerate(paddles):
            x_dis = abs(pong.x - paddle1.x)
            y_dis = abs(pong.y - paddle1.y)
            distance = math.sqrt(pow(x_dis, 2) + pow(y_dis, 2))
            distances[x] = distance

        # move ai paddle
        for x, paddle1 in enumerate(paddles):

            output = nets[x].activate((pong.x, pong.y, distances[x]))
            max_output = output.index(max(output))

            if max_output == 0 and paddle1.x > 0:
                paddle1.move_ip(-1, 0)
            elif max_output == 1 and (paddle1.x + PADDLE_WIDTH) <= SCREEN_WIDTH:
                paddle1.move_ip(1, 0)

            ge[x].fitness += 0.1

        # move paddle2 automatic for training ai
        paddle2_mid = paddle2.x + (PADDLE_WIDTH / 2)
        if pong.x < paddle2_mid:
            paddle2.move_ip(-1, 0)
        elif pong.x > paddle2_mid:
            paddle2.move_ip(1, 0)

        # end game if user quits or generation is empty
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                run = False

        if len(paddles) == 0:
            run = False

        if len(paddles) == 1 and hits > 50:
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

    winner = pop.run(eval_genomes, 1)

    answer = input("Do you want to save this neural network? (Y or N)")

    if answer.upper() == "Y" or answer.upper() == "YES":
        with open('neural_network.pkl', 'wb') as file:
            pickle.dump(winner, file)

            print("Neural network saved to neural_network.pkl")


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)

 