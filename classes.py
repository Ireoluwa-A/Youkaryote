from cmu_cs3_graphics import *
from constants import *
import math, random, time

# General tile object (in wider and smaller view)
class Tile(object):
    def __init__(self,cx,cy,size):
        self.x = cx
        self.y = cy
        self.size = size

        self.highlighted = False
        self.playerOwned = False
        self.visible = True

        self.img = ''

    def __eq__(self,other):
        if not isinstance(type(self),type(other)): return False
        return self.x == other.x and self.y == other.y and self.size == other.size

    def __hash__(self):
        return hash(self.x)
    
    # Checks if x,y position given is wthin tile bounds
    def isWithinBounds(self,mouseX,mouseY):
        return (mouseX > (self.x - self.size) and mouseX < (self.x + self.size)
            and mouseY < (self.y + self.size) and mouseY > (self.y - self.size))
    
    def __repr__(self):
        return f'Tile at {self.x},{self.y}'
   

# Hexagonal tiles for wide map view
class Hexagon(Tile):

    def __init__(self,cx,cy,size,xCoord,yCoord,zCoord):
        super().__init__(cx,cy,size)
        self.xCoord = xCoord
        self.yCoord = yCoord
        self.zCoord = zCoord

        self.resource = 'None'
        self.resourceAmount = 0

    # Gets manhattan distance between two hexes
    def getManhattanDistance(self,other):
        return max(abs(self.xCoord - other.xCoord),
                   abs(self.yCoord - other.yCoord),
                   abs(self.zCoord - other.zCoord))


    def __eq__(self,other):
        if not isinstance(type(self),type(other)): return False
        return (self.xCoord == other.xCoord and
                self.yCoord == other.yCoord and
                self.zCoord == other.zCoord)

                

    def __repr__(self):
        return f'(HEXAGON {self.xCoord},{self.yCoord},{self.zCoord})'

    def __hash__(self):
        return hash(self.x)

    def drawHexagon(self,app):
        if self.visible:
            fill, border = (HEXHIGHLIGHTCOLOR, None) if self.highlighted else (HEXCOLOR,HEXOUTLINECOLOR)
            if self.playerOwned: fill=PLAYERHEXCOLOR
            drawRegularPolygon(self.x,self.y,self.size,6,fill=fill,borderWidth=2,border=border,rotateAngle=60)

            # if self.resource != '':
            #     # print("FOUNDD")
            #     drawLabel(self.resource,self.x,self.y,size=10,fill='black')
                # hex.visible = True
            # drawLabel(f'{self.xCoord},{self.yCoord},{self.zCoord}',self.x,self.y)


    # Gives Hex particular resource and amount of said resource we want
    def setResources(self,resource,amount):
        self.resource = resource
        self.resourceAmount = amount


    # Old implementation using lines for each vertex
    # def drawHexagon(self):
    #     drawLine(self.x + self.size * math.sin(math.pi/2), self.y + self.size * math.cos(math.pi/2),self.x + self.size * math.sin(math.pi/6), self.y + self.size * math.cos(math.pi/6),fill=self.color)
    #     drawLine(self.x + self.size * math.sin(math.pi/6), self.y + self.size * math.cos(math.pi/6),self.x + self.size * math.sin(11 * math.pi/6), self.y + self.size * math.cos(11 * math.pi/6),fill=self.color)
    #     drawLine(self.x + self.size * math.sin(11 * math.pi/6), self.y + self.size * math.cos(11 * math.pi/6), self.x + self.size * math.sin(3 * math.pi/2), self.y + self.size * math.cos(3 * math.pi/2),fill=self.color)
    #     drawLine(self.x + self.size * math.sin(3 * math.pi/2), self.y + self.size * math.cos(3 * math.pi/2),self.x + self.size * math.sin(7 * math.pi/6), self.y + self.size * math.cos(7 * math.pi/6),fill=self.color )
    #     drawLine(self.x + self.size * math.sin(7 * math.pi/6), self.y + self.size * math.cos(7 * math.pi/6), self.x + self.size * math.sin(5 * math.pi/6), self.y + self.size * math.cos(5 * math.pi/6),fill=self.color)
    #     drawLine(self.x + self.size * math.sin(5 * math.pi/6), self.y + self.size * math.cos(5 * math.pi/6),self.x + self.size * math.sin(math.pi/2), self.y + self.size * math.cos(math.pi/2),fill=self.color )


class cellTile(Tile):

    def __init__(self,cx,cy,size):
        super().__init__(cx,cy,size)
        self.width = self.size
        self.height = self.width/2

    # for isometric rendering, width = 2*height
    def drawCellTileISO(self):
        width = self.width
        # height = self.size
        height = self.height

        # Draws from top
        # drawRect(self.x,self.y,200,200)
        # drawPolygon(self.x,self.y,self.x+width//2,self.y+height//2,
                    # self.x,self.y+height,self.x-width//2,self.y + height//2,fill=None,border='black')

        # Draws around center
        if self.playerOwned: 
            fill='white'
            border = 'black'
        else: 
            fill='grey'
            border=None

        if self.highlighted: 
            fill='lightgrey'

        drawPolygon(self.x-width//2,self.y,self.x,self.y+height//2,
                self.x + width//2,self.y,self.x,self.y-height//2,fill=fill,border=border)

        # drawCircle(self.x,self.y,10,fill='red')
        # drawLine(self.x,self.y,self.x+self.width/2,self.y,fill='green')
    
        # # Draws around center
        # drawLine(self.x-width//2,self.y,self.x,self.y+height//2)
        # drawLine(self.x,self.y+height//2,self.x + width//2,self.y)
        # drawLine(self.x + width//2,self.y,self.x,self.y-height//2)
        # drawLine(self.x,self.y-height//2,self.x-width//2,self.y)

    def isWithinBounds(self,mouseX,mouseY):
        return (mouseX > (self.x - self.width/2) and mouseX < (self.x + self.width/2)
                and mouseY > (self.y - self.height/2) and mouseY < (self.y + self.height/2))