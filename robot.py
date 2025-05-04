import math

class Wheel:

    def __init__(self, x, y, drag, max_speed):
        self.pos = [x, y]
        self.speed = 0
        self.__accel = False
        
        self.max_speed = max_speed
        self.drag = drag

    def accel(self, amount):
        self.speed += amount
        self.__accel = True
        if self.speed > self.max_speed: self.speed = self.max_speed

    def apply_drag(self):
        if not self.__accel:
            self.speed /= self.drag
        self.__accel = False

class Robot:

    def __init__(self, x, y, sensor_count=16, width=50, drag=1.1, max_speed=.1):
        self.__width = width
        w2 = width /2
        
        self.__lwheel = Wheel(x-w2, y, drag, max_speed)
        self.__rwheel = Wheel(x+w2, y, drag, max_speed)
        
        self.__sensor_count = sensor_count

    def getx(self):
        return (self.__lwheel.pos[0] +self.__rwheel.pos[0])/2

    def l_accel(self, amount):
        self.__lwheel.accel(amount)
    def r_accel(self, amount):
        self.__rwheel.accel(amount)

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
        
        self.__rwheel.pos[0] = self.__width *math.cos(rot) +self.__lwheel.pos[0]
        self.__rwheel.pos[1] = self.__width *math.sin(rot) +self.__lwheel.pos[1]




        

