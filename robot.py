import torch
import torch.nn as nn
import torch.optim as optim

import math

class Robot(nn.Module):
    def __init__(self, x, y, sensor_count=16, width=50, drag=1.1, max_speed=.1):
        super().__init__()
        input_layer_size = sensor_count +1
        self.model = nn.Sequential(
            nn.Linear(input_layer_size, 2*input_layer_size),  # Input layer: 2x outputs as inputs
            nn.ReLU(),
            nn.Linear(2*input_layer_size, 2)    # Output layer: 2 outputs (lwheel rwheel)
            )
        self.optimizer = optim.Adam(self.parameters(), lr=.001)
        
        w2 = width /2
        self.__lwheel = Wheel(x-w2, y, drag, max_speed)
        self.__rwheel = Wheel(x+w2, y, drag, max_speed)
        
        self.__width = width
        self.__sensor_count = sensor_count

    # Called throughout the timeframe
    def act(self, state):
        state = torch.tensor(state, dtype=torch.float32)
        return self.model(state)

    # Used at the end of the timeframe to evaluate performance
    def train_step(self, states, actions, rewards):
        # Combine lists of tensors into single tensors
        states = torch.tensor(states)
        actions = torch.stack(actions)
        # Turn reward list into tensor
        rewards = torch.tensor(rewards)

        # Predicted actions for each state IN ISOLATION.
        p_actions = self.model(states)

        # Loss measured to decline per-state error: Mean-squared error
        loss = ((p_actions - actions) **2).mean(dim=1) * -rewards
        loss = loss.mean()

        # Pytorch magic
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        

    def getx(self):
        return (self.__lwheel.pos[0] +self.__rwheel.pos[0])/2
    def gety(self):
        return (self.__lwheel.pos[1] +self.__rwheel.pos[1])/2
    def sensor_count(self):
        return self.__sensor_count
    
    def force_pos(self, x, y):
        w2 = self.__width /2
        self.__lwheel.pos = [x-w2, y]
        self.__rwheel.pos = [x+w2, y]
        self.__lwheel.speed = 0
        self.__rwheel.speed = 0
    
    def collide(self):
        self.__lwheel.speed = 0
        self.__rwheel.speed = 0

    # Returns the rotation of the left wheel relative to the right one.
    def rel_rot(self):
        rot = math.atan2(self.__lwheel.pos[1]-self.__rwheel.pos[1],
                         self.__lwheel.pos[0]-self.__rwheel.pos[0])
        return rot / (2*math.pi)
    
    def next_advances(self, approximation=1):
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
        self.__lwheel.set_speed(amount)
    def set_rspeed(self, amount):
        self.__rwheel.set_speed(amount)

    def lwheel_pos(self):
        return self.__lwheel.pos
    def rwheel_pos(self):
        return self.__rwheel.pos

    def apply_advances(self):
        self.__lwheel.apply_drag()
        self.__rwheel.apply_drag()
        
        self.l_advance(self.__lwheel.speed)
        self.r_advance(self.__rwheel.speed)

    # Movement per wheel
    def l_advance(self, amount):
        rot = math.atan2(self.__lwheel.pos[1]-self.__rwheel.pos[1],
                         self.__lwheel.pos[0]-self.__rwheel.pos[0])
        rot += amount
        
        self.__lwheel.pos[0] = self.__width * math.cos(rot) +self.__rwheel.pos[0]
        self.__lwheel.pos[1] = self.__width * math.sin(rot) +self.__rwheel.pos[1]
        
    def r_advance(self, amount):
        rot = math.atan2(self.__rwheel.pos[1]-self.__lwheel.pos[1],
                         self.__rwheel.pos[0]-self.__lwheel.pos[0])
        rot -= amount
        
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
