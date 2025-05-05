import time
import pygame
import math
import random

import robot
import obstacle

running = True
display_x, display_y = 1600, 1000
cell_size = 50

screen = pygame.display.set_mode((display_x, display_y))
robot = robot.Robot(100, 100)

def new_course():
    course = []
    for x in range(9):     # Number of columns
        gap_size = random.randint(100, 200)
        y_val = random.randint(0, display_y-gap_size)

        # Top portion of column
        course.append(obstacle.Obstacle(
            (x+1)*150, 0, random.randint(10, 50), y_val))
        # Bottom portion of column
        course.append(obstacle.Obstacle(
            (x+1)*150, y_val+gap_size,
            random.randint(10, 50), display_y-(y_val+gap_size)))

    return course

exp_obs = new_course()  # Experimental obstacles: Those that never change
ctrl_obs = new_course() # Control obstacles: Those that change every time

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
        for o in ctrl_obs:
            if o.collides(a):
                collided = True

    if not collided:
        robot.apply_advances()
    else:
        robot.collide()
        robot.force_pos(100, 100)
        ctrl_obs = new_course()

    for o in ctrl_obs:
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
