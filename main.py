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
    level = 0
    pong_x_pos = SCREEN_WIDTH / 2
    pong_y_pos = SCREEN_HEIGHT / 2
    pong_x_vel = 0
    pong_y_vel = -0.5
    pong_width = 20

    # create display objects
    paddle1 = pygame.Rect(300, 0, PADDLE_WIDTH, PADDLE_HEIGHT) # xpos, ypos, width, height
    paddle2 = pygame.Rect(0, 575, 800, 25) # xpos, ypos, width, height
    pong = pygame.Rect(pong_x_pos, pong_y_pos/2, pong_width, pong_width) # xpos, ypos, width, height

    #run the game
    run = True
    while run:
        # refresh screeen
        screen.fill((0,0,0))

        pygame.draw.rect(screen, (255, 0, 0), paddle1)
        pygame.draw.rect(screen, (255, 0, 0), paddle2)
        pygame.draw.ellipse(screen, (255, 0, 0), pong)

        # pong collision detection
        if pong.y == PADDLE_HEIGHT:
            if (pong.x + pong_width) >= paddle1.x and pong.x <= paddle1.x + PADDLE_WIDTH:
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

        if pong.x <= 0:
            pong_x_vel = pong_x_vel * (-1)
        elif (pong.x + pong_width) >= SCREEN_WIDTH:
            pong_x_vel = pong_x_vel * (-1)

        # update pong position
        pong_y_pos += pong_y_vel
        pong_x_pos += pong_x_vel
        pong.y = pong_y_pos
        pong.x = pong_x_pos

        # add controls
        key = pygame.key.get_pressed()
        if key[pygame.K_a] == True and paddle1.x > 0:
            paddle1.move_ip(-1, 0)
        elif key[pygame.K_d] == True and paddle1.x < (SCREEN_WIDTH - PADDLE_WIDTH):
            paddle1.move_ip(1, 0)

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