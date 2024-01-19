import math
import os
import pygame
import random
import pickle

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 150
PADDLE_HEIGHT = 10

# open neural network
with open('neural_network.pkl', 'rb') as network_file:
    neural_network = pickle.load(network_file)

# create window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

def main():
    pong_x_pos = SCREEN_WIDTH / 2
    pong_y_pos = SCREEN_HEIGHT / 2
    pong_x_vel = 0
    pong_y_vel = -0.7 #0.5    
    pong_width = 20
    hits = 0

    # create display objects
    # paddle 1 = ai paddle
    paddle1 = pygame.Rect(300, 10, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle2 = pygame.Rect(300, 575, PADDLE_WIDTH, PADDLE_HEIGHT) # xpos, ypos, width, height
    pong = pygame.Rect(pong_x_pos, pong_y_pos, pong_width, pong_width) # xpos, ypos, width, height

    run = True

    while run:
        paddles_remove = []

        # refresh screeen
        screen.fill((0,0,0))

        pygame.draw.rect(screen, (255, 0, 0), paddle1)
        pygame.draw.rect(screen, (255, 0, 0), paddle2)
        pygame.draw.ellipse(screen, (255, 0, 0), pong)

        # pong collision detection
        if pong.y == PADDLE_HEIGHT + 10:
            
            if (pong.x + pong_width) >= paddle1.x and pong.x <= paddle1.x + PADDLE_WIDTH:
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
            pong_y_vel = -0.7
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

        # get distance of pong from ai paddle
        x_dis = abs(pong.x - paddle1.x)
        y_dis = abs(pong.y - paddle1.y)
        distance = math.sqrt(pow(x_dis, 2) + pow(y_dis, 2))

        # add user controls
        key = pygame.key.get_pressed()
        if key[pygame.K_a] == True and paddle2.x > 0:
            paddle2.move_ip(-1, 0)
        elif key[pygame.K_d] == True and paddle2.x < (SCREEN_WIDTH - PADDLE_WIDTH):
            paddle2.move_ip(1, 0)

        # move ai paddle
        output = neural_network.activate((pong.x, pong.y, distance))
        max_output = output.index(max(output))

        if max_output == 0 and paddle1.x > 0:
            paddle1.move_ip(-1, 0)
        elif max_output == 1 and (paddle1.x + PADDLE_WIDTH) <= SCREEN_WIDTH:
            paddle1.move_ip(1, 0)


        # end game if user quits or generation is empty
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                run = False
            
        # update display
        pygame.display.update()

    pygame.quit()




if __name__ == "__main__":
    main()