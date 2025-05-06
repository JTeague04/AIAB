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
robot = robot.Robot(50, 50, width=25, sensor_count = 4)

def new_course():
    course = []
    for x in range(9):     # Number of columns
        gap_size = random.randint(100, 200)
        y_val = random.randint(0, display_y-gap_size)

        # Top portion of column
        course.append(obstacle.Obstacle(
            (x+1)*150, 0, random.randint(40, 80), y_val))
        # Bottom portion of column
        course.append(obstacle.Obstacle(
            (x+1)*150, y_val+gap_size,
            random.randint(40, 80), display_y-(y_val+gap_size)))

    return course

# Experimental obstacles: Those that never change
exp_obs = new_course()  
course = exp_obs

def raycast(agent, s_int = 10, max_dist = 600): # search_interval should be < min bar size.
    global course
    sensor_count = agent.sensor_count()
    dists = [0 for _ in range(sensor_count)]
    
    pos = (agent.getx(), agent.gety())
    rot = agent.rel_rot()
    rps = 2*math.pi / sensor_count # Rotation Per Sensor

    for i in range(sensor_count):
        s_rot = i*rps +rot # Search rotation
        dist = -s_int

        searching = True
        while searching:

            # Expand search distance
            dist += s_int 
            search_pos = (dist*math.cos(s_rot) +pos[0], dist*math.sin(s_rot) +pos[1])
            
            for o in course:
                if (o.collides(search_pos)
                        and searching
                        and dist <= max_dist
                        or not (0 <= search_pos[0] <= display_x)
                        or not (0 <= search_pos[1] <= display_y)):
                    
                    searching = False
                    pygame.draw.rect(screen, "blue",
                                     (search_pos[0]-5, search_pos[1]-5, 10, 10))
                    
        dists[i] = dist/max_dist

    return dists

def fitness(robot):
    # Reward x-progress
    fitness = ((robot.getx()-50)/ display_x)

    # Reward velocity
    fitness += math.sqrt((robot.getx() -robot.pos_marker[0]) **2
                         + (robot.gety() -robot.pos_marker[1]) **2) / 100

    # Reward staying alive (initially)
    fitness += math.log2(time.time() -robot.time_marker) /10
    
    robot.pos_marker = [robot.getx(), robot.gety()]
    robot.time_marker = time.time()
    
    return fitness

while running:

    states = []
    actions = []
    rewards = []
    end_sim = False

    for i in range(2000):
        if (not running) or end_sim: continue

        screen.fill("black")

        state = raycast(robot, max_dist = 300)
        state.append(robot.rel_rot() / (2*math.pi))
        state.append(robot.getx() /display_x)
        state.append(robot.gety() /display_y)
        
        states.append(state)
        
        action = robot.act(state)
        action = [(random.random() -.5) *.5 +a for a in action]

        actions.append(action)

        robot.set_lspeed(action[0] *.1)
        robot.set_rspeed(-action[1] *.1)

        if pygame.key.get_pressed()[pygame.K_q]: robot.l_accel(.01)
        if pygame.key.get_pressed()[pygame.K_a]: robot.l_accel(-.01)
        
        if pygame.key.get_pressed()[pygame.K_e]: robot.r_accel(.01)
        if pygame.key.get_pressed()[pygame.K_d]: robot.r_accel(-.01)

        collided = False
        for a in robot.next_advances(approximation = 5):
            if collided: continue
            for o in course:
                if (o.collides(a)
                        or not (0 <= a[0] <= display_x)
                        or not (0 <= a[1] <= display_y)):
                    collided = True

        if (not collided
                and 0 <= robot.getx() <= display_x
                and 0 <= robot.gety() <= display_y):
            robot.apply_advances()
            rw = fitness(robot)
        else:
            robot.collide()
            end_sim = True
            rw = -abs(fitness(robot))

        rewards.append(rw)

        for o in course:
            pygame.draw.rect(screen, o.colour, o.dims())

        pygame.draw.line(screen, "white",
                         robot.lwheel_pos(), robot.rwheel_pos(), 5)
        
        pygame.draw.rect(screen, "green",
                         robot.lwheel_pos()+[5, 5])
        pygame.draw.rect(screen, "red",
                         robot.rwheel_pos()+[5, 5])

        raycast(robot)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    robot.train_step(states, actions, rewards)
    robot.force_pos(50, 50)
    #course = new_course()
    print(max(rewards))

pygame.quit()
