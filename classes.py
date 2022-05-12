from cmu_cs3_graphics import *
from constants import *
from drawings import *

import math, random, time
from helpers import *

# General tile object 
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

        self.resources = ()

        self.playerOwned = False
        self.playerArea = False

        self.hexHealthColor = ['lightGreen','yellow','red']
        self.hexHealthIndex = 0

        self.meitosis = False

        # Test
        self.blue = False
        self.red = False

    def drawHexagon(self,app):
        
        if self.visible:
            borderWidth = 0.2
            opacity = 100
            fill, border = (HEXCOLOR,HEXOUTLINECOLOR)


            if self.playerArea: 
                fill, border = HEXAREACOLOR, None

            if self.highlighted: 
                fill,border =  HEXHIGHLIGHTCOLOR, 'grey'

            # Visually raise high resource tiles
            if self.resources[1] >= 40:
                border='grey'
                # borderWidth = 1.5
                borderWidth = 2

            if self.meitosis: 
                border = 'gold'
                borderWidth = 4

            if self.blue: 
                fill = 'blue'
            if self.red: 
                fill = 'red'
            
            if app.meitosisView: 
                fill='grey' 
                if self.playerArea: 
                    fill='black'
                
                border='black'
                opacity = 40
                drawRegularPolygon(self.x,self.y,self.size,6,fill=None,borderWidth=borderWidth,border=border,rotateAngle=60)


            if self.playerOwned: 
                fill=self.hexHealthColor[self.hexHealthIndex]
                opacity = 100

            drawRegularPolygon(self.x,self.y,self.size,6,fill=fill,borderWidth=borderWidth,border=border,rotateAngle=60,opacity=opacity)

            # drawLabel(f'{self.xCoord},{self.yCoord},{self.zCoord}',self.x,self.y)

        # else: 
        #     # fill, border = (HEXHIGHLIGHTCOLOR, None) if self.highlighted else (MAPBGCOLOR,None)
        #     fill, border = None, None
        #     drawRegularPolygon(self.x,self.y,self.size,6,fill=fill,borderWidth=0.2,border=border,rotateAngle=60)
            
    # Gives Hex particular resource and amount of said resource we want
    def setResources(self,resource,amount):
        self.resources = (resource,amount)

    def showResources(self):
        rectWidth, rectHeight = 80,40
        yOffset = 10
        drawRect(self.x+5,self.y,rectWidth,rectHeight,opacity=80)
        resource,amount = self.resources
        # Resource
        drawLabel(resource,self.x+rectWidth/2,self.y + yOffset,size=15,fill='white')
        # Resource amount
        drawLabel(amount,self.x+rectWidth/2,self.y + yOffset * 3,size=15,fill='white')

    # Gets manhattan distance between two hexes
    def getManhattanDistance(self,other):
        return max(abs(self.xCoord - other.xCoord),
                   abs(self.yCoord - other.yCoord),
                   abs(self.zCoord - other.zCoord))

    def __eq__(self,other):
        if not (type(self) == type(other)): 
            return False
        return (self.xCoord == other.xCoord and
                self.yCoord == other.yCoord and
                self.zCoord == other.zCoord)

    def __repr__(self):
        return f'|HEXAGON {self.xCoord},{self.yCoord},{self.zCoord}|'

    def __hash__(self):
        return hash(self.x)

class Cell(object):
    def __init__(self,cx,cy,width,height,hex,idx):
        self.cx = cx
        self.cy = cy
        self.width = width
        self.height = height
        self.rotateAngle = 10

        self.hex = hex
        self.hexRange = 2
        self.idx = idx
        self.label = f'Cell {self.idx+1}'

        # Returns dictionary of resources with default values 
        # + hex natural values
        self.stats = self.initializeResources()
        self.showStats = False

        self.organelles = []
        self.meitosis = False
        self.dead = False

    def drawCell(self,app):
        drawCellHelper(self.cx,self.cy,self.width,self.height,self.rotateAngle)
        for organelle in self.organelles: 
            organelle.drawOrganelle()

        if self.showStats: 
            drawCellStats(app,self)


    def initializeNucleus(self):
        nucleus = Nucleus(self.cx - 260,self.cy - 185)
        self.organelles.append(nucleus)

    def initializeResources(self):
        resource, amount = self.hex.resources
        stats = dict()
        stats['ATP'] = STARTINGATPVALUE
        stats['Protein'] = STARTINGPROTEINVALUE

        if resource == 'ATP':
            stats['ATP'] += amount
        elif resource == 'Protein':
            stats['Protein'] += amount
        stats.get(resource,STARTINGPROTEINVALUE) + amount
        return stats

    def updateAreaOwned(self,hexMap):
        level = self.hexRange
        return updateAreaOwnedHelper(hexMap,self.hex,level)
        
    def incrementResources(self):
        for organelle in self.organelles: 
            self.stats['ATP'] += organelle.energyOutput
            self.stats['Protein'] += organelle.proteinOutput

    def isWithinBounds(self,mx,my):
        return pointInRotatedElipse(self.cx,self.cy,self.width/2,self.height/2,self.rotateAngle,mx,my)

    def __eq__(self,other):
        if not (type(self) == type(other)): 
            return False
        return (self.hex == other.hex)

    def __repr__(self):
        return self.label

        

class Organelle(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y
        
        # Change organelle size based on specific organelle
        self.size = 40
        self.shadow = False

        self.placed = False
        self.locked = False
        self.clicked = False
        self.showStats = False

        self.placementCost = 10
        self.upgradeLevel = 1

        self.proteinOutput = 0
        self.energyOutput = 0

    def drawOrganelle(self):
        fill = 'grey' if self.shadow else self.color
        drawOval(self.x,self.y,self.size*2,self.size,fill=fill,rotateAngle=10)


            # drawRect(self.x,self.y,self.size,self.size,fill=fill)

    def moveOrganelleShadow(self,mx,my):
        self.x = mx
        self.y = my
        self.shadow = True

    def isWithinBounds(self,mouseX,mouseY):
        return (mouseX > (self.x - self.size) and mouseX < (self.x + self.size)
            and mouseY < (self.y + self.size) and mouseY > (self.y - self.size))

    def __eq__(self,other):
        if not type(self) == type(other): return False
        return (self.x == other.x and self.y == other.y)

    def performClickedAction(self,app):
        print("Hi")

class Nucleus(Organelle):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.timer = 100
        self.width = 250
        self.height = 220

        self.clicked = False
        # self.energyOutput = 10 * self.upgradeLevel

    def isWithinBounds(self,mouseX,mouseY):
        return (mouseX > (self.x + 20) and mouseX < (self.x+self.width)
                and mouseY > (self.y)  and mouseY < (self.y+self.height - 50))

                
    def drawOrganelle(self):
        drawOval(self.x + 120,self.y + 130,220,90,fill='grey',rotateAngle = 5)
        drawImage('images/nucleus.png',self.x,self.y,width=self.width,height=self.height,rotateAngle =5)

        if self.showStats: 
            rectWidth, rectHeight = 150,120
            drawRect(self.x - rectWidth/2,self.y+20,rectWidth,rectHeight,opacity=80)
            
            # Name
            drawLabel('NUCLEUS',self.x,self.y+30,size=15,fill='white',bold=True)
            drawLabel('The brain of the cell',self.x,self.y+45,size=10,fill='white',bold=True)


            drawLabel('Research new organelles',self.x,self.y+60,size=12,fill='white',bold=True)
            drawLabel('Repair Cell membrane',self.x,self.y+80,size=12,fill='white',bold=True)

        if self.clicked: 
            drawNucleusOptions(self)
    
    def performClickedAction(self,app,cell,mx,my):
        rectWidth, rectHeight = 150,120
        # Unlocked centrosome
        left = self.x+self.width - 50
        top = self.y
        rectWidth, rectHeight = 200,100
        # drawRect(left,top,rectWidth,rectHeight,opacity=80,fill='black')

        # drawLabel("Unlock Centroasdfasdsomes",left + rectWidth/2, top+10,fill='white',size=15)
        # drawLabel('50 ATP and 30 protein required',left + rectWidth/2,top + 30,fill='red',size=10)

        # drawLabel("Repair cell wall ",left + rectWidth/2, top+60,fill='white',size=15)
        centrosome = None
        for organelle in app.organelleOptions: 
            if isinstance(organelle, Centrosome):
                centrosome = organelle
                break

        # Clicked to unlock centrosome
        if (mx > left and mx < left + rectWidth and my > top and my < top + 15):
            if (cell.stats['ATP'] >= centrosome.ATPcost and 
                cell.stats['Protein'] >= centrosome.proteinCost): 

                    cell.stats['ATP'] -= centrosome.ATPcost
                    cell.stats['Protein'] -=centrosome.proteinCost
                    centrosome.locked = False
                    app.notif = 'C E N T R O S O M E  U N L O C K E D'

            else: 
                app.placementFailedNotif = 'N O T  E N O U G H  R E S O U R C E S'
            # drawRect(self.x - rectWidth/2,self.y+20,rectWidth,rectHeight,opacity=80)
        
        if (mx > left and mx < left + rectWidth and my > top + 60 and my < top + 90):
            if (cell.stats['ATP'] >= 30 and 
                cell.stats['Protein'] >= 30): 

                    cell.stats['ATP'] -= 30
                    cell.stats['Protein'] -= 30
                    cell.hex.hexHealthIndex = 0 # reset health
                    app.notif = 'C E L L  H E A L T H  R E S T O R E D'
            else: 
                app.placementFailedNotif = 'N O T  E N O U G H  R E S O U R C E S'       
    

class Mitochondria(Organelle):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.color = 'green'

        self.img = 'images/mitochondria3.png'
        self.imgShadow = 'images/mitochondria3 shadow.png'
        self.timer = 5
        self.energyOutput = 10 * self.upgradeLevel

    def drawOrganelle(self):
        if self.shadow: 
            drawOval(self.x + 20,self.y+30,70,30,fill='grey',rotateAngle=10)
            drawImage(self.imgShadow,self.x-15,self.y-15,width=65,height=65,rotateAngle=-30) 
        else: 
            drawOval(self.x + 20,self.y+30,70,30,fill='grey',rotateAngle=10)
            drawImage(self.img,self.x-15,self.y-15,width=65,height=65,rotateAngle=-30)
        
        if self.showStats:
            drawRect(self.x-200,self.y-10,150,120,opacity=80)
            # Name
            drawLabel('MITOCHONDRIA',self.x-130,self.y,size=15,fill='white',bold=True)
            drawLabel('The powerhouse of the cell',self.x-130,self.y+15,size=10,fill='white',bold=True)
            
            if self.placed: 
                # Output + time per outpuyt
                drawLabel('Current ATP Production',self.x-130,self.y+40,size=10,fill='white')
                drawLabel(f'{self.energyOutput} every {self.timer} second(s)',self.x-130,self.y+55,size=12,fill='red' )

                drawLabel('Current upgrade level',self.x-130,self.y+72,size=10,fill='white')
                drawLabel(f'{self.upgradeLevel}',self.x-130,self.y+82,size=12,fill='red')
            else: 
                drawLabel('Produces ATP',self.x-130,self.y+30,size=10,fill='white')
                drawLabel('Powers cell processes',self.x-130,self.y+40,size=10,fill='white')

class ER(Organelle):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.color = 'pink'
        self.timer = 9 # Amount of times organelle generates 
        self.proteinOutput = 10 * self.upgradeLevel  

        self.img = 'images/ER4.png'
        self.imgShadow = 'images/ER4 shadow.png'

    def drawOrganelle(self):
        width,height = 130,100
        if not self.placed: 
            width, height = 80,60
        if self.shadow: 
            drawOval(self.x + 20,self.y+30,70,30,fill='grey',rotateAngle=10)
            drawImage(self.imgShadow,self.x-30,self.y-30,width=130,height=100,rotateAngle=10)
                
        else: 
            drawOval(self.x + 20,self.y+30,70,30,fill='grey',rotateAngle=10)
            drawImage(self.img,self.x-15,self.y-15,width=width,height=height,rotateAngle=10) 

        if self.showStats:
            drawRect(self.x-200,self.y-10,200,100,opacity=80)
            # Name
            drawLabel('Endoplasmic Reticulum',self.x-110,self.y,size=15,fill='white',bold=True)
            drawLabel('Protein production',self.x-110,self.y+15,size=10,fill='white',bold=True)
            
            if self.placed: 
                # Output + time per outpuyt
                drawLabel('Current Protein Production',self.x-110,self.y+40,size=10,fill='white')
                drawLabel(f'{self.proteinOutput} every {self.timer} second(s)',self.x-110,self.y+50,size=10,fill='red')

                drawLabel('Current upgrade level',self.x-110,self.y+70,size=10,fill='white')
                drawLabel(f'{self.upgradeLevel}',self.x-110,self.y+80,size=10,fill='red')
            else: 
                drawLabel('Produces Protein',self.x-110,self.y+30,size=10,fill='white')
                drawLabel('Necessary for meitosis',self.x-110,self.y+40,size=10,fill='white')

class golgiBody(Organelle):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.timer = 10
        self.proteinOutput = 0
        self.energyOutput = 0 


        self.img = 'images/golgibody.png'
        self.imgShadow = 'images/golgibody shadow.png'

    def drawOrganelle(self):
        width,height = 110,80
        if self.shadow: 
            drawOval(self.x + 20,self.y+30,70,30,fill='grey',rotateAngle=0)
            drawImage(self.imgShadow,self.x-30,self.y-30,width=130,height=100,rotateAngle=0)
                
        else: 
            drawOval(self.x + 20,self.y+30,70,30,fill='grey',rotateAngle=10)
            drawImage(self.img,self.x-30,self.y-20,width=width,height=height,rotateAngle=0) 

        if self.showStats:
            drawRect(self.x-200,self.y-10,200,120,opacity=80)
            # Name
            drawLabel('GOLGI BODY',self.x-100,self.y,size=15,fill='white',bold=True)
            drawLabel('The deliverer',self.x-100,self.y+15,size=10,fill='white',bold=True)
            drawLabel('Increases efficiency of other organelles',self.x-100,self.y+40,size=10,fill='white')

class Centrosome(Organelle):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.locked = True
        self.img = 'images/centrosome.png'
        self.imgShadow = 'images/centrosome shadow.png'

        self.ATPcost = 50
        self.proteinCost = 30
        self.timer = 5
        self.energyOutput = 0
        self.proteinOutput = 0

    def drawOrganelle(self):
        width,height = 60,80
        if self.locked or self.shadow: 
            drawOval(self.x + 10,self.y+20,70,30,fill='grey',rotateAngle=0)
            drawImage(self.imgShadow,self.x-30,self.y-30,width=width,height=height,rotateAngle=0)
        
        else:
            drawOval(self.x + 10,self.y+20,70,30,fill='grey',rotateAngle=0)
            drawImage(self.img,self.x-30,self.y-30,width=width,height=height,rotateAngle=0)


        if self.showStats:
            drawRect(self.x-200,self.y-10,200,120,opacity=80)
            drawLabel('CENTROSOME',self.x-110,self.y,size=12,fill='white',bold=True)
            drawLabel('Need at least one placed in order to ',self.x-100,self.y+15,size=12,fill='white')
            drawLabel('perform meitosis',self.x-110,self.y+25,size=12,fill='white')


class Virus(object):
    def __init__(self,x,y,path):
        self.x = x
        self.y = y
        self.currLocation = 0
        self.path = path

        self.virusLevel = 1
        self.virusResources = dict()
        self.dead = False

        # How quickly virus gathers resources from environment
        self.virusStealRate = self.virusLevel/10

        self.infectedPlayer = False
        self.moving = False

    def moveVirus(self):

        self.currLocation += 1
        # We reached playercell
        if self.currLocation >= len(self.path)-1:
            self.infectedPlayer = True
            return

        nextHex = self.path[self.currLocation]
        self.x,self.y = nextHex.x, nextHex.y

        self.updateResources(nextHex)

    def updateResources(self,hex):
        resource, amount = hex.resources
        resourceStolenAmount = math.floor(amount * self.virusStealRate)
        self.virusResources[resource] = int(self.virusResources.get(resource,0) + resourceStolenAmount)

    def drawVirus(self):
        drawImage('images/virus.png',self.x-13,self.y-12,width=30,height=30)

    # Make change size based on amount of resources
    def showResources(self):
        rectWidth, rectHeight = 80,40

        drawRect(self.x+5,self.y,rectWidth,rectHeight * len(self.virusResources )+1,opacity=80)
        yOffset = 10
        for resource in self.virusResources: 
            amount = self.virusResources[resource]
            if amount == 0: continue
            # Resource
            drawLabel(resource,self.x+rectWidth/2,self.y + yOffset,size=15,fill='white')
            # Resource amount
            drawLabel(amount,self.x+rectWidth/2,self.y + yOffset + 20,size=15,fill='white')
            yOffset += 40


    def showPath(self):
        for hex in self.path: 
            hex.highlighted = True

    def hidePath(self):
        for hex in self.path: 
            hex.highlighted = False


          
class Button(object):
    def __init__(self,x,y,action):
        self.x = x
        self.y = y
        self.action = action
        self.size = 40

        self.highlighted = False

    def drawButton(self,*app):
        text = ''
        # text = "    ".join(self.action.upper().split())
  
        if self.action == 'play':
            text = 'P L A Y'
        elif self.action == 'settings':
            text = 'S E T T I N G S'
        elif self.action == 'instructions':
            text = 'I N S T R U C T I O N S'
        elif self.action =='splashScreen':
            text = 'R E T U R N  T O  M A I N  M E N U'

        fill = 'black' if not self.highlighted else 'lightGreen'
        drawLabel(text,self.x,self.y,size=self.size,fill=fill,align='center',font=TEXTFONT)


    def pointIntersectsButton(self,mx,my):
        sizeFactor = 2.7
        if self.action == 'splashScreen':
            sizeFactor = 10
        elif self.action == 'settings':
            sizeFactor = 4.3
        elif self.action == 'instructions':
            sizeFactor = 6

        # by 2.7 to account for size of text on screen
        return (mx > self.x - self.size * sizeFactor and mx < self.x + self.size * sizeFactor
                and my > self.y - self.size and my < self.y + self.size)

    def performAction(self,app):
        # if self.action == 'play': 
        #     app.gameStarted = True
        app.currScreen = self.action
        
    def __repr__(self):
        return f'{self.action} BUTTON'

    def __eq__(self,other):
        if not (type(self) == type(other)): return False
        return self.x == other.x and self.action == other.action


class settingsButton(object):
    def __init__(self,x,y,action):
        self.x = x
        self.y = y
        self.action = action
        self.size = 40

        
    def drawButton(self,app):
        drawLabel(self.action + ':',self.x - 100,self.y,size=20)

        value = 0
        if self.action == 'Hex Size': 
            value = app.hexSize
        elif self.action == 'Abundance':
            value = app.resourceAbundance
        elif self.action == 'Map Density':
            value = app.mapDensity
        elif self.action == 'Map Smoothness':
            value = app.iterations
        elif self.action == 'Respawn Rate':
            value = f'{app.virusRespawnRate}s'

        drawLabel(value,self.x + 20,self.y,size=20)

        drawLabel('-',self.x - 5, self.y + 5, size = 30)
        drawLabel('+',self.x + 50,self.y + 3 ,size = 30)


    def performAction(self,app,mx,my):
        if self.action == 'Hex Size':
            # CLicked on plus 
            if self.intersectsPlus(mx,my):
                app.hexSize = min(app.hexSize + 1, MAXHEXSIZE)
            elif self.intersectsMinus(mx,my):
                app.hexSize = max(app.hexSize - 1, MINHEXSIZE)
        elif self.action == 'Abundance':
            # CLicked on plus 
            if self.intersectsPlus(mx,my):
                app.resourceAbundance = min(app.resourceAbundance + 1, 100)
            elif self.intersectsMinus(mx,my):
                app.resourceAbundance = max(app.resourceAbundance-1, 0)
        
        elif self.action == 'Map Density':
            if self.intersectsPlus(mx,my):
                app.mapDensity = min(app.mapDensity + 1, 100)
            elif self.intersectsMinus(mx,my):
                app.mapDensity = max(app.mapDensity -1, 20)

        elif self.action == 'Map Smoothness':
            if self.intersectsPlus(mx,my):
                app.iterations = min(app.iterations + 1, 12)
            elif self.intersectsMinus(mx,my):
                app.iterations = max(app.iterations-1, 1) 

        elif self.action == 'Respawn Rate':
            if self.intersectsPlus(mx,my):
                app.virusRespawnRate = min(app.virusRespawnRate + 1, 300)
            elif self.intersectsMinus(mx,my):
                app.virusRespawnRate = max(app.virusRespawnRate-1, 30)   

        
    def intersectsPlus(self,mx,my):
        return mx > self.x + 40 and mx < self.x + 55 and my > self.y - 10 and my < self.y + 10
        
    def intersectsMinus(self,mx,my):
        return mx > self.x - 10 and mx < self.x + 5 and my > self.y - 5 and my < self.y + 5

    def __repr__(self):
        return f'Settings button: {self.action}'

