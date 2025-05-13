import random
import obstacle

import math
import pygame

display_x, display_y = 1600, 1000

clock = pygame.time.Clock()

def render_gui(screen, robot, course):
    screen.fill("black")

    for o in course:
        pygame.draw.rect(screen, o.colour, o.dims())
    
    pygame.draw.line(screen, "white",
                     robot.lwheel_pos(), robot.rwheel_pos(), 5)
    
    pygame.draw.rect(screen, "green",
                     robot.lwheel_pos()+[5, 5])
    pygame.draw.rect(screen, "red",
                     robot.rwheel_pos()+[5, 5])

    pygame.display.flip()
    clock.tick(30)

"""
Movement simulation

Will advance the position if possible, returning True if successful,
or collide and return False if the robot moves into an obstacle.
"""

def simulate_movement(robot, course):
    collided = False
    for a in robot.next_advances(approximation=5):
        if collided: continue

        for o in course:
            if (o.collides(a)
                    or not (0 <= a[0] <= display_x) # TODO remove magic numbers
                    or not (0 <= a[1] <= display_y)):
                collided = True

        if (not collided
                and (0 <= robot.getx() <= display_x)
                and (0 <= robot.gety() <= display_y)):    
            robot.apply_advances()
            return True

        robot.collide()
        return False



"""
Raycasting method

It is not perfect, but is an approximation to the nearest s_int.
The maximum distance is purely an optimisation technique.

It returns an array of the distances, clockwise, to obstacles nearby.
"""

def raycast(agent, course, s_int = 10, max_dist = 400): # search_interval should be < min bar size.
    sensor_count = agent.sensor_count()
    dists = [0 for _ in range(sensor_count)]
    
    pos = (agent.getx(), agent.gety())
    rot = agent.angle()
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
                        (dist > max_dist-s_int)
                        or o.collides(search_pos)
                        or not (0 <= search_pos[0] <= display_x)
                        or not (0 <= search_pos[1] <= display_y))):
                    searching = False
                    
        dists[i] = dist/ max_dist
        
        if not (0 <= dists[i] <= 1):
            raise Exception(f"There's an error here!")

    return dists

"""
Course making method

max_x and max_y refer to the positions the obstacles can be placed.
lbuffer is to allow the robot room to move freely initially.

Returns an array of obstacles.
"""

def new_course(lbuffer = 100):
    course = []
    
    for x in range(6):     # Number of columns
        gap_size = random.randint(100, 200)
        y_val = random.randint(0, display_y-gap_size)

        # Top portion of column
        course.append(obstacle.Obstacle(
            lbuffer, 0, random.randint(40, 80), y_val))
        # Bottom portion of column
        course.append(obstacle.Obstacle(
            lbuffer, y_val+gap_size,
            random.randint(40, 80), display_y-(y_val+gap_size)))

        lbuffer += 250

    return course
