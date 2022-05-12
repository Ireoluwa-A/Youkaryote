
from collections import deque
import math, random, copy


from classes import *
from drawings import *
from constants import *
from helpers import *
from pathFinder import *


 ##### TERRAIN GENERATION FUNCTIONS #####
def generateAndProcessMapRegions(app):

    # 1D list of hexagon objects
    # Represents unmodified map
    originalHexMap = initializeHexMap(app)
    
    # Get noise map to apply cellular automata
    hexNoiseMap = generateHexNoiseMap(originalHexMap,app.mapDensity)

    # Cellular automata applied to map
    automataHexMap = applyAutomata(hexNoiseMap,app.iterations)

    # Divide tiles into automata generated regions
    # Regions are a set of hexagons
    # Breadth first search to get regions
    regionType = True
    floorRegions = getRegions(automataHexMap,regionType)

    regionType = False
    wallRegions = getRegions(automataHexMap,regionType)

    ### EDITS TO MAP ###
    # Fill holes 
    for region in wallRegions:
        if len(region) < WALLSIZETHRESHOLD:
            for hex in region: 
                hex.visible = True
    for region in floorRegions: 
        if len(region) < REGIONSIZETHRESHOLD:
            for hex in region: 
                hex.visible = False

    # Final Hex map to use in game
    hexMap = []
    for region in floorRegions: 
        for hex in region: 
            hexMap.append(hex)
    for region in wallRegions: 
        for hex in region: 
            hexMap.append(hex)

    # CONNECT REGIONS
    if len(floorRegions) > 1: 
        print("GETTING MST")
        hexMap = generateMinimumSpanningTrees(hexMap,floorRegions)
    return hexMap


# Hexagonal structure learned from
# https://www.youtube.com/watch?v=wZXW_nzJotc&t=460s
# Draws hexagonal map
# Made it work with CMu graphics and used classes
# coordinate system learned from this guide: 
# https://www.redblobgames.com/grids/hexagons/implementation.html

def initializeHexMap(app):
    hexMap = []
    hexSize = app.hexSize

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
        yCoord = row *-1
        if (row % 2 == 1): # Slide over hex starting point in ever other row
            currX += hexSize - (0.15 * hexSize)
            startxCoord += 1
            
        for col in range(cols):
            xCoord = col + startxCoord
            zCoord = getZCoord(xCoord,yCoord)

            hex = Hexagon(currX,currY,hexSize,xCoord,yCoord,zCoord)

            # Generate resource
            resource, amount, = getResourceAndAmount(app)
            hex.setResources(resource,amount)

            hexMap.append(hex)

            currX += xOffset
        
        # Reset x to leftmost position
        currX = app.width/2.0 - gridWidth/2.0
        currY += yOffset
         
    return hexMap

# Gets the z coordinate of hexagon in axial plane
def getZCoord(xCoord,yCoord):
    return -xCoord-yCoord

def getResourceAndAmount(app):
    abundance = app.resourceAbundance
    resources = app.resources
    chance = random.randint(1,100)
    if chance < abundance: 
        return random.choice(resources), abundance - chance // 10
    else: 
        return 0,0


# CELLULAR AUTOMATA
# Uses cellular automata on hex tiles
def applyAutomata(hexNoiseMap,iterations):
    for _ in range(iterations): 
        newMap = copy.deepcopy(hexNoiseMap)
        for i in range(len(hexNoiseMap)):
            # 1 is passage, 0 is wall
            # Get neighbors
            visibleNeighbors = getNoOfVisibleNeighbors(hexNoiseMap,hexNoiseMap[i])
            # Rule set from notes:  
            # https://www.cs.cmu.edu/~112/notes/student-tp-guides/Terrain.pdf
            if visibleNeighbors < 3: 
                newMap[i].visible = False
            elif visibleNeighbors > 4: 
                newMap[i].visible = True    
        hexNoiseMap = newMap
    return hexNoiseMap 

# Generates random noise map based on density
def generateHexNoiseMap(hexMap,density):
    # resultHexMap = hexMap
    for hex in hexMap:
        rand = random.randint(1,100)
        if rand < density: 
            hex.visible = True
        else: 
            hex.visible = False
    return hexMap
    
def getNoOfVisibleNeighbors(hexMap,currHex):
    visibleNeighbors = 0
    adjacentHexes = getAdjacentHexes(hexMap,currHex)
    for adjHex in adjacentHexes: 
        if adjHex.visible == True: 
            visibleNeighbors += 1  
    return visibleNeighbors - (6 - len(adjacentHexes))


# FLOOD FILL/BFS ALGORITHM FOR REGION DETECTING
# queue approach learned from: https://www.geeksforgeeks.org/queue-in-python/
# Breadth first learned frmo
# https://www.hackerearth.com/practice/algorithms/graphs/breadth-first-search/tutorial/
def getRegions(hexMap,regionType):
    # Regions is a list of sets of hexagons. 
    # Each set corresponding to a region in generated map
    hexMapSet = set(hexMap)
    regions = getRegionsHelper(hexMap,hexMapSet,[],regionType)
    return regions
    
# Recurisvely gets all regions in map, using breadth depth search gethex region
def getRegionsHelper(hexMap,hexMapSet,result,regionType):
    if hexMapSet == set(): 
        return result
    else: 
        hex = hexMapSet.pop()
        if not hex.visible == regionType:
            return getRegionsHelper(hexMap,hexMapSet,result,regionType)
        else: 
            regionNeighbor = set(getHexRegion(hexMap,hex,regionType))
            result.append(copy.deepcopy(regionNeighbor))
            hexMapSet = hexMapSet - regionNeighbor
            return getRegionsHelper(hexMap, hexMapSet, result,regionType)

# Gets all hexes in region
# Breadth first learned frmo
# https://www.hackerearth.com/practice/algorithms/graphs/breadth-first-search/tutorial/
def getHexRegion(hexMap,startHex,hexType):
    regionHexes = []
    hexesSeen = []
    q = deque()
    q.append(startHex)
    hexesSeen.append(startHex)
    while len(q) > 0:
        # Get first hex off queue and add it to list of room hexes
        currHex = q.popleft()
        regionHexes.append(currHex)
        for adjHex in getAdjacentHexes(hexMap,currHex):
            if adjHex.visible == hexType and adjHex not in hexesSeen: 
                q.append(adjHex)
                hexesSeen.append(adjHex)
    return regionHexes





# Makes sure all rooms are connected
# Prims algorithm, but treating regions as nodes in graph
# Algorithm learned from here: https://www.youtube.com/watch?v=cplfcGZmX7I
def generateMinimumSpanningTrees(hexMap,regions):
    visitedRegions = []
    # Get largest region to begin with
    visitedRegions.append(getLargestRegion(regions))
    
    while visitedRegions != regions: 
        
        edgeInfos = []
        # Check all vertices reachable from all regions we've visited
        for visitedRegion in visitedRegions: 
            # Go through neighbors. # In our case, assume that all nodes are reachable
            for adjRegion in regions: 
                # Only add nodes we haven't visited yet
                if adjRegion in visitedRegions or adjRegion == visitedRegion: 
                    continue
                else: 
                    distance = getRegionDistance(visitedRegion,adjRegion)
                    print("distance",distance)
                    edgeInfos.append((visitedRegion,adjRegion,distance))

        # Pick and connect two cheapest nodes 
        # i.e connect least costly edge
        if edgeInfos == []:
            break
        mainRegion,connecteeRegion = getCheapestRegionEdge(edgeInfos)
        connectRegions(hexMap,mainRegion,connecteeRegion)

        # Add cheapest node to visited region
        visitedRegions.append(mainRegion)
        visitedRegions.append(connecteeRegion)

    return hexMap


# Picks two points in region and finds best path between them to connect it
def connectRegions(hexMap,region1,region2):
    region1Hex = getRandomHexInRegion(region1)
    region2Hex = getRandomHexInRegion(region2)

    # region1Hex,region2Hex = getClosestHexes(hexMap,region1,region2)
    # region1Hex.red = True
    # region2Hex.red = True
    mst = findBestPath(hexMap,region1Hex,region2Hex,True)
    for hex in mst:
        hex.visible = True
        # hex.blue = True



def getClosestHexes(hexMap,r1, r2):
    pass

# Random.sample learned from: 
# https://www.geeksforgeeks.org/python-random-sample-function/
def getRandomHexInRegion(region):
    hex = random.sample(region,1)[0]
    return hex

def getCheapestRegionEdge(edgeInfos):
    bestDist = None
    bestRegions = None
    for info in edgeInfos: 
        region1, region2, dist = info
        if bestDist == None or dist < bestDist: 
            bestDist = dist
            bestRegions = (region1,region2)
    return bestRegions


# center of mass approach to estimate distance between two regions
# not perfect as larger regions might actually be closer. 
def getRegionDistance(reg1,reg2):
    x1,y1 = getRegionCOM(reg1)
    x2,y2 = getRegionCOM(reg2)
    return math.dist([x1,y1],[x2,y2])

def getRegionCOM(region):
    leftX = None
    rightX = None
    topY = None
    bottomY = None

    for hex in region: 
        if leftX == None or hex.x < leftX: 
            leftX = hex.x
        if rightX == None or hex.x > rightX:
            rightX = hex.x
        if topY == None or hex.y < topY: 
            topY = hex.y
        if bottomY == None or hex.y > bottomY:
            bottomY = hex.y
    x = (rightX - leftX)/2
    y = (topY - bottomY)/2
    return x,y
    

def getLargestRegion(regions):
    bestSize = None
    bestRegion = None
    for region in regions: 
        if bestSize == None or len(region) > bestSize: 
            bestRegion = region
            bestSize = len(region)
    return bestRegion


