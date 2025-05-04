
class Obstacle:

    def __init__(self, x, y, sx, sy, colour="red"):
        self.__left = x
        self.__top = y
        self.__right = x+sx
        self.__bottom = y+sy
        
        self.__sx = sx
        self.__sy = sy
        self.colour = colour

    def collides(self, point):
        return ((self.__left <= point[0] <= self.__right)
                and (self.__top <= point[1] <= self.__bottom))

    def dims(self):
        return (self.__left, self.__top, self.__sx, self.__sy)
    
