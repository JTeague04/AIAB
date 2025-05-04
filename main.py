import time
import pygame
import math
import random

from perlin_noise import PerlinNoise

import robot
import obstacle

running = True
display_x, display_y = 1600, 1000
cell_size = 50

noise = PerlinNoise(octaves=6, seed=0)
screen = pygame.display.set_mode((display_x, display_y))

robot = robot.Robot(100, 100, max_speed =.2)
obstacles = [obstacle.Obstacle(random.randint(0, display_x),
                      random.randint(0, display_y),
                      random.randint(10, 50), random.randint(10, 50))
             for _ in range(50)]

while running:

    screen.fill("black")

    time.sleep(1/60)

    if pygame.key.get_pressed()[pygame.K_q]: robot.l_accel(.01)
    if pygame.key.get_pressed()[pygame.K_a]: robot.l_accel(-.01)
    
    if pygame.key.get_pressed()[pygame.K_e]: robot.r_accel(.01)
    if pygame.key.get_pressed()[pygame.K_d]: robot.r_accel(-.01)

    collided = False
    for a in robot.next_advances():
        if collided: continue
        for o in obstacles:
            if o.collides(a):
                collided = True

    if not collided:
        robot.apply_advances()
    else:
        robot.collide()

    for o in obstacles:
        pygame.draw.rect(screen, o.colour, o.dims())

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
