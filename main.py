import time
import pygame
import math

from perlin_noise import PerlinNoise

import robot

running = True
display_x, display_y = 800, 500

noise = PerlinNoise(octaves=6, seed=0)
screen = pygame.display.set_mode((display_x, display_y))

robot = robot.Robot(100, 100)

while running:

    time.sleep(1/60)

    screen.fill("black")

    if pygame.key.get_pressed()[pygame.K_LEFT]:
        robot.l_accel(.01)
    if pygame.key.get_pressed()[pygame.K_RIGHT]:
        robot.r_accel(.01)
        
    robot.apply_advances()

    pygame.draw.line(screen, "white",
                     robot.lwheel_pos(), robot.rwheel_pos(), 5)
    
    pygame.draw.rect(screen, "green",
                     robot.lwheel_pos()+[5, 5])
    pygame.draw.rect(screen, "red",
                     robot.rwheel_pos()+[5, 5])

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


pygame.quit()
