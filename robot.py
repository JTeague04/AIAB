import math

class Wheel:

    def __init__(self, x, y, drag, max_speed):
        self.pos = [x, y]
        self.speed = 0
        self.__accel = False
        
        self.__max_speed = max_speed
        self.__drag = drag

    def accel(self, amount):
        self.speed += amount
        self.__accel = True
        if self.speed > self.__max_speed: self.speed = self.__max_speed
        if self.speed <-self.__max_speed: self.speed =-self.__max_speed

    def apply_drag(self):
        if not self.__accel:
            self.speed /= self.__drag
        self.__accel = False

class Robot:

    def __init__(self, x, y, sensor_count=16, width=50, drag=1.1, max_speed=.1):
        w2 = width /2
        self.__lwheel = Wheel(x-w2, y, drag, max_speed)
        self.__rwheel = Wheel(x+w2, y, drag, max_speed)
        
        self.__sensor_count = sensor_count
        self.__width = width

    def getx(self):
        return (self.__lwheel.pos[0] +self.__rwheel.pos[0])/2
    
    def force_pos(self, x, y):
        w2 = self.__width /2
        self.__lwheel.pos = [x-w2, y]
        self.__rwheel.pos = [x+w2, y]
    
    def collide(self):
        self.__lwheel.speed = 0
        self.__rwheel.speed = 0
    
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

    def lwheel_pos(self):
        return self.__lwheel.pos
    def rwheel_pos(self):
        return self.__rwheel.pos

    def apply_advances(self):
        self.__lwheel.apply_drag()
        self.__rwheel.apply_drag()
        
        self.__l_advance(self.__lwheel.speed)
        self.__r_advance(self.__rwheel.speed)

    # Movement per wheel
    def __l_advance(self, amount):
        rot = math.atan2(self.__lwheel.pos[1]-self.__rwheel.pos[1],
                         self.__lwheel.pos[0]-self.__rwheel.pos[0])
        rot += amount
        
        self.__lwheel.pos[0] = self.__width * math.cos(rot) +self.__rwheel.pos[0]
        self.__lwheel.pos[1] = self.__width * math.sin(rot) +self.__rwheel.pos[1]
        
    def __r_advance(self, amount):
        rot = math.atan2(self.__rwheel.pos[1]-self.__lwheel.pos[1],
                         self.__rwheel.pos[0]-self.__lwheel.pos[0])
        rot -= amount
        
        self.__rwheel.pos[0] = self.__width * math.cos(rot) +self.__lwheel.pos[0]
        self.__rwheel.pos[1] = self.__width * math.sin(rot) +self.__lwheel.pos[1]




        

