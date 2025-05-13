import robot
import obstacle
import methods

import gym
from gym import spaces
import numpy as np
import pygame
from stable_baselines3 import PPO
import math

DIS_X, DIS_Y = 1600, 1000

ROBOT_SENSOR_COUNT = 4
LEARN_AMOUNT = 100_000
MANUAL_CONTROL = False

np.random.seed(0)
robot = robot.Robot(50, 50, sensor_count = ROBOT_SENSOR_COUNT)

def agent_observation(course):
    obs = methods.raycast(robot, course) + robot.norm_wheelspeeds()
    obs.append(robot.norm_angle())
    return obs


class RobotEnvironment(gym.Env):
    def __init__(self):

        self.course = methods.new_course()

        self.observation_space = spaces.Box(low=0, high=1, shape=(ROBOT_SENSOR_COUNT +3, ), dtype=np.float32)
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(2, ), dtype=np.float32)

        self.state = None
        self.step_count = 0

        self.prev_fitness = 0
        self.current_fitness = 0

        self.prev_pos = [50, 50]
        
        self.reset()

    def update_fitness(self):
        self.prev_fitness = self.current_fitness

        # Reward x-distance
        self.current_fitness = robot.getx() / DIS_X

        # Penalise idleness        
        self.current_fitness -= math.log(
            (robot.getx()-self.prev_pos[0]) **2 + (robot.gety()-self.prev_pos[1]) **2
            )


    def reset(self):

        self.step_count = 0
        robot.reset()
        self.prev_pos = [50, 50] # TODO eliminate magic numbers
        self.course = methods.new_course()

        return np.array(agent_observation(self.course), dtype = np.float32)

    def step(self, action):
        self.step_count += 1
        
        robot.set_lspeed(action[0])
        robot.set_rspeed(action[1])

        self.prev_pos = [robot.getx(), robot.gety()]
        collided = not methods.simulate_movement(robot, self.course)
        
        if not collided:
            self.update_fitness()
            reward = self.current_fitness - self.prev_fitness
        else:
            reward = -1
        
        observation = np.array(agent_observation(self.course), dtype = np.float32)
        complete = collided or self.step_count > 10000 # '10000' being the timeout step count
        logs = {}

        return observation, reward, complete, logs

environment = RobotEnvironment()

if not MANUAL_CONTROL:
    model = PPO("MlpPolicy", environment, verbose=1)
    model.learn(total_timesteps = LEARN_AMOUNT)

screen = pygame.display.set_mode((DIS_X, DIS_Y))

observation = environment.reset()
complete = False

running = True
while running:

    if not MANUAL_CONTROL:
        action, states = model.predict(observation, deterministic = True)
        observation, reward, complete, info = environment.step(action)
        #print(environment.current_fitness - environment.prev_fitness)

    else:
        lspeed = 0
        rspeed = 0
        if pygame.key.get_pressed()[pygame.K_q]: lspeed += .1
        if pygame.key.get_pressed()[pygame.K_a]: lspeed -= .1
        if pygame.key.get_pressed()[pygame.K_e]: rspeed += .1
        if pygame.key.get_pressed()[pygame.K_d]: rspeed -= .1
        environment.step([lspeed, rspeed])

    if complete or pygame.key.get_pressed()[pygame.K_ESCAPE]:
        observation = environment.reset()
        complete = False

    methods.render_gui(screen, robot, environment.course)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


pygame.quit()
