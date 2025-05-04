import math

class Robot:

    def __init__(self, x, y, sensor_count=16, width=50):
        w2 = width /2
        self.__lwheel = [x-w2, y]
        self.__rwheel = [x+w2, y]
        self.__width = width
        
        self.__sensor_count = sensor_count

    def getx(self):
        return (self.__lwheel[0] +self.__rwheel[0])/2

    def lwheel_pos(self):
        return self.__lwheel
    def rwheel_pos(self):
        return self.__rwheel

    # Movement per wheel
    def l_advance(self, amount):
        rot = math.atan2(self.__lwheel[1]-self.__rwheel[1], self.__lwheel[0]-self.__rwheel[0])
        rot += amount
        
        self.__lwheel[0] = self.__width * math.cos(rot) +self.__rwheel[0]
        self.__lwheel[1] = self.__width * math.sin(rot) +self.__rwheel[1]
        
    def r_advance(self, amount):
        rot = math.atan2(self.__rwheel[1]-self.__lwheel[1], self.__rwheel[0]-self.__lwheel[0])
        rot += amount
        
        self.__rwheel[0] = self.__width *math.cos(rot) +self.__lwheel[0]
        self.__rwheel[1] = self.__width *math.sin(rot) +self.__lwheel[1]





        

