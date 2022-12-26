import math, copy
import random as rand

from constants import *
from drawings import *
from classes import * 

# MAIN HELPER FUNCTIONS #

# Returns all adjacent hexes that are visible/part of the map
def getAdjacentHexes(hexTiles,currHex):
    adjacentHexes = []
    for hex in hexTiles:
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


# Stronger viruses do more damage
def getVirusDamage(virus):
    extraDmg = 0
    resourceAmount = 0
    if len(virus.virusResources) > 1: 
        for resource in virus.virusResources:
            resourceAmount += virus.virusResources[resource]
    if resourceAmount >= 50: extraDmg = 1
    return virus.virusLevel + extraDmg


# Shows extra stats for organelles
def showOrganelleInfo(organelleOptions,cell,mx,my):
    for organelle in cell.organelles: 
        if organelle.isWithinBounds(mx,my): 
            organelle.showStats = True
        else: 
            organelle.showStats = False
  
    for organelleOpt in organelleOptions: 
        if organelleOpt.isWithinBounds(mx,my):
            organelleOpt.showStats = True
        else: 
            organelleOpt.showStats = False
    
def hideOrganelleInfo(organelleOptions,cell):
    for organelle in cell.organelles: 
        organelle.showStats = False
    for organelleOpt in organelleOptions: 
        organelleOpt.showStats = False

def placeOrganelle(cell,organelle):
    placementCost = organelle.placementCost 
    if cell.stats['ATP'] < (placementCost): 
        return 'N O T  E N O U G H  A T P'
    if organelle.locked: 
        return 'N O T  Y E T  U N L O C K E D'
    
    organelleCount = 0
    for organelle2 in cell.organelles: 
        print(type(organelle2))
        if type(organelle) == type(organelle2):
            organelleCount += 1
    if organelleCount >= 2:
        return 'O R G A N E L L E  L I M I T  R E A C H E D' 

    # add organelle to cell
    organelle.shadow = False
    organelle.placed = True
    cell.organelles.append(organelle)
    
    updateResourceStats('ATP',cell,placementCost*-1)
    print("ORGANELLE PLACED",cell)
    return None



def updateResourceStats(resource,cell,placementCost):
    cell.stats[resource] += (placementCost) # Is a negative number

# Shows stats of hex
def showHexStats(app,mouseX,mouseY):
    for hex in app.hexMap:
        if not hex.visible: continue
        if hex.isWithinBounds(mouseX,mouseY):
            return hex
 
# Gets curr cell the player is on
def getCurrCell(app):
    return app.playerCells[app.currCellIdx]

# Picks random player Hex for virus to target
def pickRandomPlayerHex(app):
    if len(app.playerCells)-1 == 0: 
        idx = 0
    else:
        idx = rand.randrange(0,len(app.playerCells)-1)
    return app.playerCells[idx].hex

# Checks if hex is owned by player
def playerOwnedHex(hex,playerCells):
    for cell in playerCells:
        if cell.hex == hex: 
            return True
    return False

def highlightHexes(app,mouseX,mouseY):
    for hex in app.hexMap:
        hex.highlighted = True if hex.isWithinBounds(mouseX,mouseY) else False


# Gets area to be shaded based on level 
# recursively shades around adjacent hexes, and the adjacent hexes of adjacent hexes...
# similar to freddy fractal :)
def updateAreaOwnedHelper(hexMap,hex,level):
    for adjHex in getAdjacentHexes(hexMap,hex):
        if adjHex.visible == False: continue
        adjHex.playerArea = True

    if level == 0: return

    for adjHex in getAdjacentHexes(hexMap,hex):
        updateAreaOwnedHelper(hexMap,adjHex,level-1)


# Checks if point (px,py) is in rotated elipse
# Formula learned here: 
#https://stackoverflow.com/questions/7946187/point-and-ellipse-rotated-position-test-algorithm
def pointInRotatedElipse(cx,cy,a,b,phi,px,py):
    # Change angle to other side for calculation
    phi = math.radians(360 - phi)
    left = ( ( (math.cos(phi) * (px-cx)) + (math.sin(phi) * (py-cy)) ) ** 2) / a**2
    right = ( ( (math.sin(phi) * (px-cx)) + (math.cos(phi) * (py-cy)) ) **2 )/ b**2
    return left + right <= 1

def playerControllsAllHexes(app):
    return app.mapFill == 1

# Gets current percent of map player owns
def getMapFill(hexMap):
    allHexes = 0
    areaCount = 0
    for hex in hexMap: 
        if hex.visible: 
            allHexes += 1
        if hex.playerArea:
            areaCount += 1
    fraction = areaCount/allHexes
    print("fraction",fraction)
    return fraction

def getClickedHex(hexMap,mx,my):
    for hex in hexMap:
        if hex.isWithinBounds(mx,my):
            return hex

def getMeitosisCost(meitosisHex,mx,my):
    dist = math.dist([meitosisHex.x,meitosisHex.y],[mx,my])
    return int(dist // 10 + 10)

# Returns health, energy prod, protein prod and failure rate of current cell
# Overall cell stats
def getCellStats(cell): 
    # Cell health
    health = 0
    hexColor = cell.hex.hexHealthColor[cell.hex.hexHealthIndex]
    if hexColor == 'lightGreen':
        health = 100
    elif hexColor == 'yellow':
        health = 50
    elif hexColor == 'red':
        health = 25

    # Energy prod
    energyProd = 0
    proteinProd = 0
    for organelle in cell.organelles: 
        proteinProd += organelle.proteinOutput
        energyProd += organelle.energyOutput
    return health,energyProd,proteinProd,10

def hexDead(infectedHex,virus):
    return infectedHex.hexHealthIndex + virus.virusLevel > (len(infectedHex.hexHealthColor)-1)


def isValidVirusStartHex(hexMap,startHex):
    if startHex.visible == False: return False

    playerHex = None
    for hex in hexMap: 
        if hex.playerOwned:
            playerHex = hex
    if playerHex.getManhattanDistance(startHex) < VIRUSSPAWNDISTANCETOPLAYER: 
        print("TOO CLOSE")
        return False

    return True
# def floodFillTest(hexMap,clickedHex):
#     clickedRegion = getHexRegion(app.hexMap,clickedHex,False)
#     for hex in hexMap: 
#         if hex in clickedRegion:
#             hex.highlighted = True
#         else: 
#             hex.highlighted = False
