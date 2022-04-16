from cmu_cs3_graphics import *
import math, random, copy
from PIL import Image

from classes import *
from drawings import *
from constants import *

def onAppStart(app):

    # Map variables
    app.mapView = True
    app.hexSize = HEXSIZE
    app.mapPercentOfScreen = HEXMAPPERCENTOFSCREEN


    # What percent of times have resources and how good the resources are
    app.resourceAbundance = random.randint(40,60)
    app.resources = ['ATP','Protein','Glucose']

    # Cellular automata generation
    app.originalHexMap = generateHexMap(app,app.hexSize)
    app.mapDensity = 70
    app.iterations = 8
    app.hexTiles = applyAutomata(app.originalHexMap,app.mapDensity,app.iterations)
    # app.hexTiles = app.originalHexMap

    # Pick random position to place player's first cell
    # app.playerOwnedHexes = set([app.hexTiles[random.randint(0,len(app.hexTiles)-1)][random.randint(0,len(app.hexTiles[0])-1)]])
    app.playerOwnedHexes = [app.hexTiles[5][3]]
   
    # Cell variables
    app.cellRows, app.cellCols = 3,3
    app.cellMargin = 500
    app.cellGridWidth = app.width - (app.cellMargin * 2)
    app.cellGridHeight = app.height - (app.cellMargin*2)

    # app.tileWidth = app.cellGridWidth/ len(app.cellTiles)
    app.tileWidth = TILEWIDTH
    app.tileHeight = app.tileWidth

    app.cellTiles = generateCellTiles(app)

    # Game variables
    app.paused = False

def onMouseMove(app,mouseX,mouseY):
    return
    if app.mapView: 
        highlightHexes(app,mouseX,mouseY)
    else: 
        highlightCells(app,mouseX,mouseY)

def highlightHexes(app,mouseX,mouseY):
    for hexList in app.hexTiles:
        for hex in hexList:
            hex.highlighted = True if hex.isWithinBounds(mouseX,mouseY) else False

def highlightCells(app,mouseX,mouseY):
    for cellTilesList in app.cellTiles:
        for cellTile in cellTilesList:
            # print(cellTile.size)
            cellTile.highlighted = True if cellTile.isWithinBounds(mouseX,mouseY) else False


def onKeyPress(app,key):
    if key == 'm':
        app.mapView = True
    elif key == 'c':
        app.mapView = False
    elif key == 'p':
        app.paused = not app.paused
    # Implement zoom functionality
    elif key =='=':
        app.mapPercentOfScreen += 0.1
    elif key =='-':
        app.mapPercentOfScreen -= 0.1

def onMousePress(app,mouseX,mouseY):
    
    
    if app.mapView: 
        
        # Check position they clicked and zoom in if its their own cell
        for playerHex in app.playerOwnedHexes:
            if playerHex.isWithinBounds(mouseX,mouseY):
                app.mapView = False
                break

        clickedHex = None
        for hexList in app.hexTiles:
            for hex in hexList: 
                if hex.isWithinBounds(mouseX,mouseY):
                    clickedHex = hex
                    break

        print("BEST MANHATTAN DIST",clickedHex.getManhattanDistance(app.playerOwnedHexes[0]))
        bestPath = findBestPath(app,clickedHex, app.playerOwnedHexes[0])
        for hexList in app.hexTiles:
            for hex in hexList:
                hex.highlighted = True if hex in bestPath else False


# A* pathfinding algorithm
# Returns best path in hexagonal grid from starting hex to destination hex
# Learned from: https://en.wikipedia.org/wiki/A*_search_algorithm
def findBestPath(app,startHex,targetHex):
    
    G = 0 # Movement cost from starting point to current tile
    H = startHex.getManhattanDistance(targetHex) # Estimated distance to target point
    F = G + H 
    visited = []

    # Add starting tile  to open list
    openList = [] # Tuple of hex and important information for tile weighting
    return findBestPathHelper(app,startHex,G,F,openList,visited,targetHex)

def findBestPathHelper(app,currHex,currG,currF,openList,visited,targetHex):
    while pathFound(targetHex,visited) == False: 
        visited.append(currHex)
        adjacentHexes = getViableAdjacentHexes(app,currHex,visited)
        for adjHex in adjacentHexes:

            # adjHexG = currG + 1
            adjHexG = currG + calculateHexWeighting(adjHex)
            adjHexH = adjHex.getManhattanDistance(targetHex)
            adjHexF = adjHexG + adjHexH
            # if currF < adjHexF:
            #     # visited.append(adjHex)
            #     openList.append((adjHex,adjHexG,adjHexH,adjHexF))
                # if not hexInTupleList(adjHex,openList):
            openList.append((adjHex,adjHexG,adjHexH,adjHexF))

        # print("OPENLIST",openList)
        # print("VISITED",visited)
        currHexIdx = getBestHexInfo(openList,targetHex) 
        currHex, currG, currH, currF = openList[currHexIdx]
        openList = []

    return visited
 
def calculateHexWeighting(hex): 
    if hex.resource == '':
        return 4
    elif hex.resource == 'ATP':
        return 1
    else: 
        return 2
def hexInTupleList(hex,tupleList):
    for tuple in tupleList: 
        checkHex = tuple[0]
        if hex == checkHex: 
            return True
    return False

# Returns all adjacent hexes that are visible/part of the map
def getAdjacentHexes(hexTiles,currHex):
    adjacentHexes = []
    for hexList in hexTiles:
        for hex in hexList:
            xCoord, yCoord, zCoord = hex.xCoord, hex.yCoord, hex.zCoord
            targXcoord, targYcoord, targZcoord = currHex.xCoord, currHex.yCoord, currHex.zCoord
            # Top left
            if xCoord == targXcoord and yCoord == targYcoord+1 and zCoord == targZcoord-1:
                adjacentHexes.append(hex)
            # Top right
            elif xCoord == targXcoord-1 and yCoord == targYcoord+1 and zCoord == targZcoord:
                adjacentHexes.append(hex)
            # Right
            elif xCoord == targXcoord+1 and yCoord == targYcoord and zCoord == targZcoord-1:
                adjacentHexes.append(hex)
            # left
            elif xCoord == targXcoord-1 and yCoord == targYcoord and zCoord == targZcoord+1:
                adjacentHexes.append(hex)
            # bottom left    
            elif xCoord == targXcoord and yCoord == targYcoord-1 and zCoord == targZcoord+1:
                adjacentHexes.append(hex) 
            # bottom right
            elif xCoord == targXcoord+1 and yCoord == targYcoord-1 and zCoord == targZcoord:
                adjacentHexes.append(hex)  
    return adjacentHexes

def getViableAdjacentHexes(app,currHex,visited):
    viableAdjacentHexes = getAdjacentHexes(app.hexTiles,currHex)
    i = 0
    while i < len(viableAdjacentHexes):
        adjHex = viableAdjacentHexes[i]
        if adjHex.visible == False or adjHex in visited: 
            viableAdjacentHexes.pop(i)
        else: 
            i += 1
    return viableAdjacentHexes
  
def pathFound(targetHex,visited):
    return targetHex in visited

# Gets hex and required info with lowest movement close and closest distance to target
# Returns the tile with the lowest f value
def getBestHexInfo(openList,targetHex):
    bestF = None
    idx = 0
    for i in range(len(openList)): 
        hexInfo = openList[i]
        currHex = hexInfo[0]
        if currHex == targetHex: 
            return i
        currF = hexInfo[3]
        if bestF == None or currF < bestF:
            bestF = currF
            idx = i
    return idx

def onMouseDrag(app,mouseX,mouseY):
    pass


def redrawAll(app):
    if app.mapView:
        drawHexMap(app)
    else:
        drawCellView(app) # Isometric drawing of current player cell
        # drawVirus(app.width/2,app.height/2,20)
        # drawCircle(app.width/2,app.height/2,200)

    drawUi(app) 

def drawHexMap(app):
    drawGrayBackground(app)
    for i in range(len(app.hexTiles)):
        hexList = app.hexTiles[i]
        for j in range(len(hexList)):
            hex = hexList[j]
            if hex in app.playerOwnedHexes: 
                hex.playerOwned, hex.visible = True, True

            hex.drawHexagon(app)


 
# Hexagonal structure learned from
# https://www.youtube.com/watch?v=wZXW_nzJotc&t=460s
# Draws hexagonal map
# Made it work with CMu graphics and used classes
# coordinate system learned from this guide: 
# https://www.redblobgames.com/grids/hexagons/implementation.html

def generateHexMap(app,hexSize):
    hexTiles = []

    gridWidth = app.mapPercentOfScreen * app.width
    gridHeight= app.mapPercentOfScreen * app.height

    xOffset = 1.7 * hexSize
    yOffset = hexSize * 1.5

    # Number of hexagons in x and y direction
    rows = int(gridHeight / yOffset) + 1 
    cols = int(gridWidth / xOffset) + 1
    
    currX = app.width/2.0 - gridWidth/2.0
    currY = app.height/2.0 - gridHeight/2.0

    xCoord, yCoord, zCoord = 0,0,0
    startxCoord = 0
    for row in range(rows):
        rowList = []
        yCoord = row *-1
        if (row % 2 == 1): # Slide over hex starting point in ever other row
            currX += hexSize - (0.15 * hexSize)
            startxCoord += 1
            
        for col in range(cols):
            xCoord = col + startxCoord
            zCoord = getZCoord(xCoord,yCoord)

            hex = Hexagon(currX,currY,hexSize,xCoord,yCoord,zCoord)
            resource, amount, = getResourceAndAmount(app)
            hex.setResources(resource,amount)

            rowList.append(hex)

            currX += xOffset
        hexTiles.append(rowList)
        
        # Reset x to leftmost position
        currX = app.width/2.0 - gridWidth/2.0
        currY += yOffset

    return hexTiles

# Gets the z coordinate of hexagon in axial plane
def getZCoord(xCoord,yCoord):
    return -xCoord-yCoord


# CELLULAR AUTOMATA
# Uses cellular automata on hex tiles
def applyAutomata(originalHexMap,mapDensity,iterations):

    hexNoiseMap = generateHexNoiseMap(originalHexMap,mapDensity)

    # Ceullar automata generation
    for iter in range(iterations): 
        newMap = copy.deepcopy(hexNoiseMap)
        for row in range(len(hexNoiseMap)):
            for col in range(len(hexNoiseMap[row])):
                # 1 is passage, 0 is wall
                # Get neighbors
                visibleNeighbors = getNoOfVisibleNeighbors(hexNoiseMap,row,col)
                currOldCell = hexNoiseMap[row][col]
                currNewCell = newMap[row][col]
                # Rule set from notes:  
                # https://www.cs.cmu.edu/~112/notes/student-tp-guides/Terrain.pdf
                # print(visibleNeighbors)
                if currOldCell.visible:
                    if visibleNeighbors < 3: 
                        currNewCell.visible = False
                    else: 
                        currNewCell.visible = True
                else: 
                    if visibleNeighbors > 5: 
                        currNewCell.visible = True         

        hexNoiseMap = newMap
        
    return hexNoiseMap 

# Generates random noise map based on density
def generateHexNoiseMap(hexMap,density):
    resultHexMap = hexMap
    for hexList in resultHexMap:
        for hex in hexList: 
            rand = random.randint(1,100)
            if rand < density: 
                hex.visible = True
            else: 
                hex.visible = False
    return resultHexMap
    
def getNoOfVisibleNeighbors(hexNoiseMap,row,col):
    visibleNeighbors = 0
    currHex = hexNoiseMap[row][col]

    adjacentHexes = getAdjacentHexes(hexNoiseMap,currHex)
    for adjHex in adjacentHexes: 
        if adjHex.visible == True: 
            visibleNeighbors += 1  
    return visibleNeighbors + (6 - len(adjacentHexes))


def getResourceAndAmount(app):
    abundance = app.resourceAbundance
    resources = app.resources

    chance = random.randint(1,100)
    if chance < abundance: 
        return random.choice(resources), abundance - chance // 10
    else: 
        return 0,0






















def generateCellTiles(app):
    cellTiles = []
    
    # Placing sprites on screen
    # for col in range(app.cellCols):
    #     cellTileList = []
    #     for row in range(app.cellRows):
    #         originX = 1.5 * app.tileWidth
    #         originY = 0.5 * app.tileHeight
    #         isoX = originX + ((row - col) * app.tileWidth/2)
    #         isoY = originY + ((col+row) * app.tileHeight/2)
            
    #         print("POS",row,col)
    #         print("NEW",isoX,isoY)
    #         print('---------')

    #         currCellTile = cellTile(isoX,isoY,app.tileWidth)

    #         if row == app.cellRows//2 and col == app.cellRows//2:
    #             currCellTile.playerOwned = True
    #         cellTileList.append(currCellTile)
    #     cellTiles.append(cellTileList)


    for row in range(app.cellRows):
        cellTileList = []
        for col in range(app.cellCols):

            cartX = col * app.tileWidth/2 + app.cellMargin
            cartY = row * app.tileHeight/2 
            isoX, isoY = cartToIso(app,cartX,cartY)
            # print("POS",row,col)
            # print("OLD",cartX,cartY)
            # print("NEW",isoX,isoY)
            # print('---------')
            
            yOffset = 50
            currCellTile = cellTile(isoX,isoY-yOffset,app.tileWidth)
            if row == app.cellRows//2 and col == app.cellRows//2:
                currCellTile.playerOwned = True


            cellTileList.append(currCellTile)
        cellTiles.append(cellTileList)

    return cellTiles

def isoToCart(app):
    pass
    # isoX = math.floor(isoX/app.tileWidth)
    # isoY = math.floor(isoY/app.tileHeight)

def drawCellView(app):
    for cellTileList in app.cellTiles:
        for tile in cellTileList:
            tile.drawCellTileISO()

            
def cartToIso(app,cartX,cartY):
    isoX = cartX - cartY
    isoY = (cartX + cartY)/2
    return isoX,isoY

# Returns cx and cy of tile in isometric rendering
def getISOCellBounds(app,row,col):
    x = row * app.tileWidth 
    y = col * app.tileHeight
    isoX = (x - y) 
    isoY = (x+y)/2 
    return isoX,isoY



def runYoukaryote():
    runApp(1000, 700) 

runYoukaryote()




 




