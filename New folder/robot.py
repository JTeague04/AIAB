import torch
import torch.nn as nn
import torch.optim as optim

import math
import time

class Robot:
    def __init__(self, x, y, sensor_count=16, width=50, drag=1.1, max_speed=1):
        
        w2 = width /2
        self.__lwheel = Wheel(x+w2, y, drag, max_speed)
        self.__rwheel = Wheel(x-w2, y, drag, max_speed)

        self.__default_x = x
        self.__default_y = y
        
        self.__width = width
        self.__sensor_count = sensor_count

    def sensor_count(self):
        return self.__sensor_count

    def lwheel_pos(self):
        return self.__lwheel.pos
    def rwheel_pos(self):
        return self.__rwheel.pos

    def getx(self):
        return (self.__lwheel.pos[0] +self.__rwheel.pos[0])/2
    def gety(self):
        return (self.__lwheel.pos[1] +self.__rwheel.pos[1])/2
    
    def reset(self):
        w2 = self.__width /2
        self.__lwheel.pos = [self.__default_x+w2, self.__default_y] # facing down
        self.__rwheel.pos = [self.__default_x-w2, self.__default_y]
        self.__lwheel.speed = 0
        self.__rwheel.speed = 0
    
    def collide(self):
        self.__lwheel.speed = 0
        self.__rwheel.speed = 0

    # Returns the rotation of the left wheel relative to the right one.
    def angle(self):
        rot = math.atan2(self.__lwheel.pos[1]-self.__rwheel.pos[1],
                         self.__lwheel.pos[0]-self.__rwheel.pos[0])
        return rot

    def norm_angle(self):
        return self.angle() / (2*math.pi)
    
    def next_advances(self, approximation=2):
        # Returns the positions, assuming no collision, of robot left/right/centre.
        points = []

        # left wheel
        rot = math.atan2(self.__lwheel.pos[1]-self.__rwheel.pos[1],
                         self.__lwheel.pos[0]-self.__rwheel.pos[0])
        rot += self.__lwheel.speed
        points.append([self.__width * math.cos(rot) +self.__rwheel.pos[0],
                       self.__width * math.sin(rot) +self.__rwheel.pos[1]])

        # right wheel
        rot = math.atan2(self.__rwheel.pos[1]-self.__lwheel.pos[1],
                         self.__rwheel.pos[0]-self.__lwheel.pos[0])
        rot -= self.__rwheel.speed
        points.append([self.__width * math.cos(rot) +self.__lwheel.pos[0],
                       self.__width * math.sin(rot) +self.__lwheel.pos[1]])

        difference = ((self.__rwheel.pos[0] -self.__lwheel.pos[0]) /(approximation+1),
                      (self.__rwheel.pos[1] -self.__lwheel.pos[1]) /(approximation+1))

        # centrals
        for a in range(approximation):
            points.append(((a+1)*difference[0] +points[0][0],
                           (a+1)*difference[1] +points[0][1]))
        return points

        
    def l_accel(self, amount):
        self.__lwheel.accel(amount)
    def r_accel(self, amount):
        self.__rwheel.accel(amount)

    def set_lspeed(self, amount):
        self.__lwheel.speed = amount
    def set_rspeed(self, amount):
        self.__rwheel.speed = amount

    def norm_wheelspeeds(self):
        return [self.__lwheel.norm_speed(), self.__rwheel.norm_speed()]

    def apply_advances(self):
        self.__lwheel.apply_drag()
        self.__rwheel.apply_drag()
        
        # Left wheel
        rot = math.atan2(self.__lwheel.pos[1]-self.__rwheel.pos[1],
                         self.__lwheel.pos[0]-self.__rwheel.pos[0])
        rot += self.__lwheel.speed
        
        self.__lwheel.pos[0] = self.__width * math.cos(rot) +self.__rwheel.pos[0]
        self.__lwheel.pos[1] = self.__width * math.sin(rot) +self.__rwheel.pos[1]

        # Right wheel
        rot = math.atan2(self.__rwheel.pos[1]-self.__lwheel.pos[1],
                         self.__rwheel.pos[0]-self.__lwheel.pos[0])
        rot -= self.__rwheel.speed
        
        self.__rwheel.pos[0] = self.__width * math.cos(rot) +self.__lwheel.pos[0]
        self.__rwheel.pos[1] = self.__width * math.sin(rot) +self.__lwheel.pos[1]


# Inventing the wheel
class Wheel:
    def __init__(self, x, y, drag, max_speed):
        self.pos = [x, y]
        self.speed = 0
        self.__accel = False
        
        self.__max_speed = max_speed
        self.__drag = drag

    def set_speed(self, amount):
        self.speed = amount
        self.__movechecks()

    def accel(self, amount):
        self.speed += amount
        self.__movechecks()

    def __movechecks(self):
        self.__accel = True
        if self.speed > self.__max_speed: self.speed = self.__max_speed
        if self.speed <-self.__max_speed: self.speed =-self.__max_speed

    def apply_drag(self):
        if not self.__accel:
            self.speed /= self.__drag
        self.__accel = False

    def norm_speed(self):
        return self.speed / self.__max_speed
