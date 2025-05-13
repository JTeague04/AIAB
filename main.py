import time
import pygame
import math
import random

import robot
import obstacle

pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 100)

scary_image = pygame.transform.scale(pygame.image.load('rawr.jpg'), (100, 100))

counter = 0
running = True
display_x, display_y = 1600, 1000
cell_size = 50

screen = pygame.display.set_mode((display_x, display_y))
robot = robot.Robot(50, 50, width=25, sensor_count = 4)

def new_course():
    course = []
    for x in range(7):     # Number of columns
        gap_size = random.randint(100, 200)
        y_val = random.randint(0, display_y-gap_size)

        # Top portion of column
        course.append(obstacle.Obstacle(
            (x+1)*200, 0, random.randint(40, 80), y_val))
        # Bottom portion of column
        course.append(obstacle.Obstacle(
            (x+1)*200, y_val+gap_size,
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
            search_pos = [dist*math.cos(s_rot) +pos[0], dist*math.sin(s_rot) +pos[1]]
            
            for o in course:
                if (searching and (
                        (dist > max_dist)
                        or o.collides(search_pos)
                        or not (0 <= search_pos[0] <= display_x)
                        or not (0 <= search_pos[1] <= display_y))):
                    searching = False
                    pygame.draw.rect(screen, "blue",
                                     (search_pos[0]-5, search_pos[1]-5, 10, 10))
                    
        dists[i] = dist/ (max_dist+s_int)
        
        if not (-1 <= dists[i] <= 1):
            raise Exception(f"fuck you {dist} {max_dist+s_int}")

    return dists

def fitness(robot):
    # Reward x-progress
    fitness = 20 *(robot.getx()-75) /display_x

    # Reward distance travelled
    
##    dist = math.sqrt((robot.getx()-robot.pos_marker[0]) **2 +
##                     (robot.gety()-robot.pos_marker[1]) **2)
##
##    logfn = robot.getx() - robot.pos_marker[0]
##    if logfn < 0:
##        fitness -= math.log(abs(logfn))
    
    return fitness

while running:

    states = []
    actions = []
    rewards = []
    end_sim = False
    
    robot.time_marker = time.time()
    counter = 0

    rw = 0
    last_fitness = 0

    while (counter < 5000 or fitness(robot) > 5) and running and not end_sim:
        counter += 1
        
        screen.fill("black")

        state = raycast(robot, max_dist = 300)
        state.append(robot.rel_rot() / (2*math.pi))
        state.append(robot.getx() /display_x)
        state.append(robot.gety() /display_y)
        
        states.append(state)
        
        action = robot.act(state)
        for i, a in enumerate(action):
            if not (-1 <= a <= 1):
                raise Exception(f"fuck you {i} {a}")

        action = [(random.random() -.5)*.1 +a for a in action]

        actions.append(action)

        robot.set_lspeed(action[0] *1)
        robot.set_rspeed(action[1] *1)

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
            temp = last_fitness
            last_fitness = rw
            rw = fitness(robot) -temp
        else:
            robot.collide()
            end_sim = True
            rw = max(-1, -abs(fitness(robot)))

        rewards.append(rw)

        screen.blit(scary_image, (robot.pos_marker[0]-50, robot.pos_marker[1]-50))


        for o in course:
            pygame.draw.rect(screen, o.colour, o.dims())

        pygame.draw.line(screen, "white",
                         robot.lwheel_pos(), robot.rwheel_pos(), 5)
        
        pygame.draw.rect(screen, "green",
                         robot.lwheel_pos()+[5, 5])
        pygame.draw.rect(screen, "red",
                         robot.rwheel_pos()+[5, 5])

        render = font.render(str(round(rw, 2)), False, "white")
        screen.blit(render, (display_x-400, display_y-200))

        render = font.render(f"{counter/50}%", False, "white")
        screen.blit(render, (display_x-400, display_y-300))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    robot.train_step(states, actions, rewards)
    robot.force_pos(50, 50)
    #course = new_course()
    print(max(rewards))

pygame.quit()
