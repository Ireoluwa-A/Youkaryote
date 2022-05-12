
from cmu_cs3_graphics import *
import math, random, copy

from classes import *
from constants import *
from helpers import getAdjacentHexes


### PATH FINDING FUNCTIONS ###

# A* pathfinding algorithm

# Returns best path in hexagonal grid from starting hex to destination hex
# Learned from: https://en.wikipedia.org/wiki/A*_search_algorithm
# Made work with hexagonal coordinates
# MAKE MORE EFFICIENT USING DICTIONARIES INSTEADS OF TUPLES
# Connecting variable for when doing minimum spanning tree
def findBestPath(hexMap,startHex,targetHex,connecting=False):
    
    G = 0 # Movement cost from starting point to current tile
    H = startHex.getManhattanDistance(targetHex) # Estimated distance to target point
    F = G + H 
    visited = []
    parentNode = None
    # Add starting tile  to open list
    openList = [(startHex,G,H,F,parentNode)] # Tuple of hex and important information for tile weighting
    return findBestPathHelper(hexMap,openList,visited,targetHex,startHex,connecting)

def findBestPathHelper(hexMap,openList,visited,targetHex,startHex,connecting):
    while openList != []:

        currHexIdx = getBestHexInfo(openList,targetHex) 
        currHex, currG, currH, currF, currHexParent = openList[currHexIdx]

        openList.pop(currHexIdx)
        visited.append((currHex,currG,currH,currF,currHexParent))

        if currHex == targetHex:
            break

        adjacentHexes = getAdjacentHexes(hexMap,currHex)
        for adjHex in adjacentHexes:
            # Only ignore invisible hexes if we're finding best path and not connecting two paths
            if adjHex.visible == False and connecting == False: 
                continue
            
            # adjHexG = currG + calculateHexWeighting(adjHex)   
            if hexInTupleList(adjHex,openList):
                adjHexIdx = getHexIdxFromTupleList(adjHex,openList)
                adjHex, adjG, adjH, adjF, adjParent = openList[adjHexIdx]
                if adjG < currG: 
                    # New path is better so remove neighbor
                    removeFromTupleList(adjHex,openList)
            elif hexInTupleList(adjHex,visited):
                adjHexIdx = getHexIdxFromTupleList(adjHex,visited)
                adjHex, adjG, adjH, adjF, adjParent = visited[adjHexIdx]
                if adjG < currG: 
                    # New path is better so remove neighbor
                    removeFromTupleList(adjHex,openList)

            if not hexInTupleList(adjHex,openList) and not hexInTupleList(adjHex,openList):
                # adjG = currG + 1
                adjG = currG + calculateHexWeighting(adjHex)
                adjH = adjHex.getManhattanDistance(targetHex)
                adjF = adjG + adjH

                adjParent = currHex
                
                # Add it to open with parent set to n
                openList.append((adjHex,adjG,adjH,adjF,adjParent))
    
    return reconstructFinalPath(targetHex,visited,startHex)

# Reconstructs final path by going through parent nodes starting from final found node
def reconstructFinalPath(targetHex,visited,startHex):
    lastHexInfo = None
    for node in visited: 
        if node[0] == targetHex: 
            lastHexInfo = node
    return reconstructFinalPathHelper(startHex,lastHexInfo,visited)

# Recursively gets final path
def reconstructFinalPathHelper(startHex,currHexInfo,visited):
    if currHexInfo[0] == startHex: 
        return [startHex]
    else:
        currHex = currHexInfo[0]
        nextHex = currHexInfo[-1]
        nextHexInfoIdx = getHexIdxFromTupleList(nextHex,visited)
        nextHexInfo = visited[nextHexInfoIdx]
        return [currHex] + reconstructFinalPathHelper(startHex,nextHexInfo,visited)

##### HELPER FUNCTIONS ####
# Order of info: Hex, G, H, F, Parent
def getHexIdxFromTupleList(hex,L):
    for i in range(len(L)):
        info = L[i] 
        if info[0] == hex: 
            return i

def removeFromTupleList(hex,L):
    i = 0
    while i < len(L): 
        if L[i][0] == hex: 
            L.pop(i)
        else: 
            i += 1

def calculateHexWeighting(hex): 
    resource,amount = hex.resources
    if resource == 0:
        return 4
    elif resource == 'ATP' or resource == 'Glucose':
        if amount > 2: 
            return 1
        else: 
            return 2
    else: 
        return 3

def hexInTupleList(hex,tupleList):
    for tuple in tupleList: 
        checkHex = tuple[0]
        if hex == checkHex: 
            return True
    return False

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

def getViableAdjacentHexes(app,currHex,visited):
    viableAdjacentHexes = getAdjacentHexes(app.hexMap,currHex)
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



