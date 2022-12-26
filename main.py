from cmu_graphics import *
import random as rand
import copy
from PIL import Image
from collections import deque
import sys
 

sys.setrecursionlimit(10**6)

from classes import *
from drawings import *
from constants import *

from mapGeneration import *
from pathFinder import *
from helpers import *


def onAppStart(app):
    app.setMaxShapeCount(20000)
    app.stepsPerSecond = 1

    # Game variables
    app.mapView = True
    app.pauseGame = True
    app.gameStarted = False
    app.gameOver = False
    app.gameWon = False
    app.currScreen = 'splashScreen'
    app.playerName = 'Player'
    app.homeButtons = initializeHomeButtons(app)
    app.settingsButtons = initializeSettingsButtons(app)
    app.instructionButtons = initializeInstructionButtons(app)
    app.speedMode = False # Faster resource accumulation for testing. Press t
    
    # Notifications
    app.updatedStatsNotif = None
    app.placementFailedNotif = None
    app.notif = None
    app.notifDisplayTime = 3 # seconds
    app.showExtraInfo = False 
    app.showHexStats = None
    app.notifTimerFired = 0

    # Default Map variables
    app.hexSize = HEXSIZE
    app.mapPercentOfScreen = HEXMAPPERCENTOFSCREEN
    app.mapDensity = MAPDENSITY
    app.iterations = AUTOMATAITERATIONS
    app.hexAreaGrowthRate = 30 # seconds

    # Default resource variables
    print(random, type(random))
    app.resourceAbundance = rand.randrange(40,60)
    app.resources = ['ATP','Protein','Glucose']
    app.maxCellAreaRange = 5
        
    # Default virus variables
    app.virusNum = 1  # No of viruses on board
    app.virusRespawnRate = VIRUSRESPAWNRATE
    app.showVirusStats = False
    app.timerFired = 0

    # Map and game variables to be initialized
    app.hexMap = None
    app.currCellIdx = 0
    app.playerCells = None
    app.organelleOptions = None
    app.currPlacingOrganelle = None

    app.meitosisCell = None
    app.meitosisView = False
    app.showMeitosisCostToPoint = None
    app.meitosisProteinReq = 100 # 10 seconds
    app.meitosisATPreq = 30

    app.viruses = None
    app.showVirusResources = []
    app.mapFill = None


def onKeyPress(app,key):
    if key =='r':
        onAppStart(app)
    if app.gameOver: return
    
    if key == 'm':
        app.mapView = True
    elif key == 'c':
        app.mapView = False        
    elif key == 'p':
        app.pauseGame = not app.pauseGame
    elif key == 's':
        app.showExtraInfo = not app.showExtraInfo
        currCell = getCurrCell(app)
        currCell.showStats = app.showExtraInfo
    elif key == 'v':
        app.showVirusStats = not app.showVirusStats
    elif key == 't':
        app.speedMode = not app.speedMode
        if app.speedMode: 
            app.notif = 'S U P E R  S P E E D  M O D E ( O N )'
        else:
            app.notif = 'S U P E R  S P E E D  M O D E ( O F F )' 

    # Implement zoom functionality
    elif key =='=':
        app.mapPercentOfScreen += 0.1
    elif key =='-':
        app.mapPercentOfScreen -= 0.1

    # Cycle through cells with left and right arrow keys
    if app.mapView == False: 
        if key == 'right':
            app.currCellIdx = min(len(app.playerCells)-1,app.currCellIdx+1)
        elif key == 'left':
            app.currCellIdx = max(0,app.currCellIdx-1)


def onStep(app):

    if app.gameOver or not app.gameStarted: 
        return

    app.notifTimerFired += 1
    
    # Notification delay
    if app.notifTimerFired % app.notifDisplayTime == 0: 
        app.updatedStatsNotif = None
        app.placementFailedNotif = None
        app.notif = None

    if app.pauseGame: return

    app.timerFired += 1
    # Add new virus
    if app.timerFired % app.virusRespawnRate == 0:
        app.viruses.extend(initializeViruses(app))

    if app.timerFired % app.hexAreaGrowthRate == 0: 
        for cell in app.playerCells:
            cell.hexRange += 1
            cell.updateAreaOwned(app.hexMap)
            

    # Increment cell resources 
    currCell = getCurrCell(app)
    for cell in app.playerCells: 
        for organelle in cell.organelles: 
            if isinstance(organelle,golgiBody): # Make golgi body reduce time
                continue
            timer = 1 if app.speedMode else organelle.timer
            if app.timerFired % timer == 0:
                cell.incrementResources()    

    if app.mapView: 
        # Kill dead viruses, move viruses.
        updateViruses(app)
    
        # Show hexes that can perform meitosis
        for cell in app.playerCells: 
            if cellCanPerformMeitosis(app,cell):
                cell.hex.meitosis = True

    # else: # Cell view specific timer events 
    #    if cellCanPerformMeitosis(app,cell):

    if playerControllsAllHexes(app):
        app.gameWon = True

        

def onMouseMove(app,mouseX,mouseY):
    # Highlight Home buttons
    if app.currScreen == 'splashScreen':
        for button in app.homeButtons: 
            if button.pointIntersectsButton(mouseX,mouseY):
                button.highlighted = True
            else: 
                button.highlighted = False
            
    if not app.gameStarted: 
        return

    # Show Cost of meitosis
    if app.meitosisView: 
        # Tuple of hex player mouse is on and cost to hex
        meitosisCost = getMeitosisCost(app.meitosisCell.hex,mouseX,mouseY)
        app.showMeitosisCostToPoint = (meitosisCost,(mouseX,mouseY))
    else: 
        app.showMeitosisCostToPoint = None

    if app.mapView: 
        # Show Hexes stats (resources they have)
        if app.showExtraInfo: 
            app.showHexStats = showHexStats(app,mouseX,mouseY)
        else:
            app.showHexStats = None
    else: 
        currCell = getCurrCell(app)

        # Draw Organelle shadow
        if app.currPlacingOrganelle != None: 
            # if currCell.isWithinBounds(mouseX,mouseY):
            app.currPlacingOrganelle.moveOrganelleShadow(mouseX,mouseY)

        # Show organelle specific stats
        if app.showExtraInfo: 
            showOrganelleInfo(app.organelleOptions,currCell,mouseX,mouseY)
        else: 
            hideOrganelleInfo(app.organelleOptions,currCell)


def onMousePress(app,mouseX,mouseY):
    if not app.gameStarted:
        if app.currScreen == 'splashScreen':
            for button in app.homeButtons:
                if button.pointIntersectsButton(mouseX,mouseY):
                    button.performAction(app) # Play button starts game and initializes stuff
                    if button.action == 'play':
                        app.gameStarted = True
                        app.loadingScreen = True
                        initializeMapAndGame(app)

        elif app.currScreen == 'settings':
            for settingsButton in app.settingsButtons: 
                if type(settingsButton) == Button: # Return to home screen button
                    if settingsButton.pointIntersectsButton(mouseX,mouseY):
                        settingsButton.performAction(app)
                else: 
                    settingsButton.performAction(app,mouseX,mouseY)
        elif app.currScreen == 'instructions':
            for instructionButton in app.instructionButtons:
                if instructionButton.pointIntersectsButton(mouseX,mouseY):
                    instructionButton.performAction(app)
                                   
    else:
        if app.mapView:
            app.mapFill = getMapFill(app.hexMap)
            clickedHex = getClickedHex(app.hexMap,mouseX,mouseY)

            # FLOOD FILL REGION CLICKED TEST
            # floodFillTest(app.hexMap,clickedHex)

            if clickedHex.visible == False:
                return

            # Performing meitosis
            if app.meitosisCell != None: 
                performMeitosis(app,clickedHex,mouseX,mouseY) 

            # Trying to do meitosis
            if clickedHex.meitosis:
                for cell in app.playerCells: 
                    if cell.hex == clickedHex: 
                        app.meitosisCell = cell
                        app.meitosisView = True

            # Zoom in player's cell
            if app.meitosisCell == None: 
                for playerCell in app.playerCells:
                    if playerCell.hex.isWithinBounds(mouseX,mouseY):
                        app.currCellIdx = playerCell.idx
                        app.mapView = False
                        return

            app.mapFill = getMapFill(app.hexMap)

            # PATH FINDER TEST
            # # bestPath = findBestPath(app,clickedHex, pickRandomPlayerHex(app))
            # bestPath = findBestPath(app,clickedHex,app.playerCells[0].hex)
            # for hex in app.hexMap:
            #     hex.highlighted = True if hex in bestPath else False

        else: # MADE ACTION IN CELL
            
            currCell = getCurrCell(app)

            # Attempting to place an organelle
            if app.currPlacingOrganelle != None:
                if not currCell.isWithinBounds(mouseX,mouseY): 
                    app.currPlacingOrganelle = None
                    return
                organelle = app.currPlacingOrganelle
                placementCost = organelle.placementCost
                failureReason = placeOrganelle(currCell,app.currPlacingOrganelle)
                if failureReason != None: 
                    app.placementFailedNotif = failureReason
                    app.updatedStatsNotif = None

                # Reduce speed of all other organelles if golgi placed
                if isinstance(app.currPlacingOrganelle,golgiBody):
                    for organelle in currCell.organelles: 
                        organelle.timer = max(1,organelle.timer-app.currPlacingOrganelle.upgradeLevel)

                app.currPlacingOrganelle = None

                # CHANGE RESOURCE LATERRR
                app.updatedStatsNotif = (organelle.x,organelle.y,'ATP',placementCost)
                

            # Picked an organelle to place
            for organelleOption in app.organelleOptions: 
                if organelleOption.isWithinBounds(mouseX,mouseY):
                    app.currPlacingOrganelle = copy.deepcopy(organelleOption)


            for organelle in currCell.organelles: 
                if organelle.clicked and isinstance(organelle,Nucleus): 
                    organelle.performClickedAction(app,currCell,mouseX,mouseY)

            # Clicked on organelle in cell
            if currCell.isWithinBounds(mouseX,mouseY):
                for organelle in currCell.organelles: 
                    if organelle.isWithinBounds(mouseX,mouseY):
                        organelle.clicked = not organelle.clicked
                        # organelle.performClickedAction(app)


def redrawAll(app):
    if not app.gameStarted: 
        drawCurrScreen(app)
    else: 
        drawGrayBackground(app)
        # if app.loadingScreen():
        #     drawLoadingScreen(app)
        if app.gameOver: 
            drawGameOverScreen(app)
            return
        if app.gameWon: 
            drawGameWonScreen(app)
            return
        if app.mapView:
            drawHexMap(app)
        else:      
            drawCellView(app)

        drawUi(app) 

def drawHexMap(app):
    for hex in app.hexMap:
        if playerOwnedHex(hex,app.playerCells): 
            hex.playerOwned, hex.visible = True, True
        hex.drawHexagon(app)
    
    if app.showMeitosisCostToPoint != None: 
        cost = app.showMeitosisCostToPoint[0]
        mx, my = app.showMeitosisCostToPoint[1]
        drawMeitosisCost(cost,mx,my)

    # Show hex stats
    if app.showHexStats != None: 
        app.showHexStats.showResources()
        
    # Draw viruses
    for virus in app.viruses: 
        virus.drawVirus()
        if virus in app.showVirusResources: 
            virus.showResources()
    
    if app.notif != None: 
        drawNotif(app)

# Draws current cell player is on
def drawCellView(app):
    currCell = getCurrCell(app)
    currCell.drawCell(app)

    # Draw organelle and shadow
    if app.currPlacingOrganelle != None: 
        app.currPlacingOrganelle.drawOrganelle()

    # Draw stats notifications
    if app.updatedStatsNotif != None:
        x,y,resource,amount = app.updatedStatsNotif
        drawUpdatedStatsNotif(x,y,resource,amount*-1)

    if app.notif != None: 
        drawNotif(app)

    # Draw failed placement notif
    if app.placementFailedNotif != None: 
        drawPlacementFailedNotif(app,app.placementFailedNotif)
 
    if currCell.hex.meitosis: 
        drawMeitosisAlert(app,currCell)



### INITIALIAZING VARIABLES ###
def initializeMapAndGame(app):
    app.hexMap = generateAndProcessMapRegions(app)
    app.playerCells = initializePlayerCells(app)
    app.organelleOptions = initializeOrganelleOptions(app)
    app.viruses = initializeViruses(app)
    app.mapFill = getMapFill(app.hexMap)

def initializePlayerCells(app):
    cellCx, cellCy = app.width//2,app.height//2
    cellWidth, cellHeight = CELLWIDTH,CELLHEIGHT
    playerHex = initializePlayerHex(app.hexMap)
    playerHex.playerOwned = True

    currCellIdx = app.currCellIdx
    currCell = Cell(cellCx,cellCy,cellWidth,cellHeight,playerHex,currCellIdx)

    currCell.updateAreaOwned(app.hexMap)
    currCell.initializeNucleus()

    currCell.initializeResources() # Cell gets resources on tile it lands
    return [currCell]

# Picks random, visible player hex to start on
def initializePlayerHex(hexMap):
    while True: 
        i = 0
        chance = rand.randrange(0,len(hexMap)-1)
        playerHex = hexMap[chance]
        if playerHex.visible == True: 
            return playerHex

def initializeOrganelleOptions(app):
    mitochondriaOption = Mitochondria(app.width - 550,app.height-70)
    ERoption = ER(app.width - 450,app.height-70)
    golgiBodyOption = golgiBody(app.width - 350,app.height-75)
    centrosomeOption = Centrosome(app.width-220,app.height-60)

    return [mitochondriaOption,ERoption,golgiBodyOption,centrosomeOption]

def initializeViruses(app):
    viruses = []
    for i in range(app.virusNum):
        while True: 
            startHex = app.hexMap[rand.randrange(0,len(app.hexMap)-1)]
            if isValidVirusStartHex(app.hexMap,startHex):
                break

        targetHex = pickRandomPlayerHex(app)
        path = findBestPath(app.hexMap,startHex,targetHex)
        path.reverse()
        virus = Virus(startHex.x,startHex.y,path)
        virus.showPath() # Briefly show path virus will take to your cell
        viruses.append(virus)
    return viruses

def initializeHomeButtons(app):
    playButton = Button(app.width/2,app.height/2 - 50,'play')
    settingsButton = Button(app.width/2,app.height/2 + 20,'settings')
    instructionsButton = Button(app.width/2,app.height/2 + 100,'instructions')
    return [playButton,settingsButton,instructionsButton]

def initializeSettingsButtons(app):
    returnButton = Button(app.width/2,app.height - 150,'splashScreen')
    adjustHexSize = settingsButton(app.width/2 + 40,230,'Hex Size')
    adjustResourceAbundance = settingsButton(app.width/2 + 40,270,'Abundance')
    adjustMapDensity = settingsButton(app.width/2 + 40,310,'Map Density')
    adjustMapSmoothness = settingsButton(app.width/2 + 40,350,'Map Smoothness')


    # adjustVirusSpeed = settingsButton(app.width/2 + 40, 500,'Virus Speed')
    adjustVirusRespawnRate = settingsButton(app.width/2 + 40,500,'Respawn Rate')
    returnButton.size = 20
    return [adjustHexSize,returnButton,adjustResourceAbundance,adjustMapDensity,adjustMapSmoothness,adjustVirusRespawnRate]

def initializeInstructionButtons(app):
    returnButton = Button(app.width/2,app.height - 150,'splashScreen')
    return [returnButton]


# OTHER HELPERS
def cellCanPerformMeitosis(app,cell):
    if (cell.stats['Protein'] <= app.meitosisProteinReq
        or cell.stats['ATP'] <= app.meitosisATPreq):
            return False

    # Check if centrosome is present
    centrosomeFound = False
    for organelle in cell.organelles: 
        if isinstance(organelle,Centrosome):
            centrosomeFound = True
    return centrosomeFound

def performMeitosis(app,clickedHex,mouseX,mouseY):
    # Helper for updating meitosis stats
    meitosisCell = app.meitosisCell
    meitosisCell.hex.meitosis = False
    meitosisCost = getMeitosisCost(meitosisCell.hex,mouseX,mouseY)
    meitosisCell.stats['ATP'] -= (app.meitosisATPreq + meitosisCost)
    meitosisCell.stats['Protein'] -= app.meitosisProteinReq

    meitosisCell.hexRange = min(meitosisCell.hexRange+1, app.maxCellAreaRange)
    meitosisCell.updateAreaOwned(app.hexMap)
    
    # Put in HELPERRR. Change initialize funtion to take hex
    cellCx, cellCy = app.width//2,app.height//2
    cellWidth, cellHeight = CELLWIDTH,CELLHEIGHT
    playerHex = clickedHex
    playerHex.playerOwned = True

    app.currCellIdx += len(app.playerCells) - app.currCellIdx
    print("Cell idx",app.currCellIdx)

    currCell = Cell(cellCx,cellCy,cellWidth,cellHeight,playerHex, app.currCellIdx)
    currCell.updateAreaOwned(app.hexMap)
    currCell.initializeNucleus()
    app.playerCells.append(currCell)

    app.meitosisCell = None
    app.meitosisView = False
    app.mapFill = getMapFill(app.hexMap)

def updateViruses(app):
    i = 0
    while i < len(app.viruses):
        virus = app.viruses[i]
        if virus.dead:
            app.viruses.pop(i)
        else:
            # Show stats
            if app.showVirusStats: 
                app.showVirusResources.append(virus)
            else: 
                app.showVirusResources = []

            if virus.infectedPlayer: 
                infectedHex = virus.path[-1]

                # Cell is dead
                if hexDead(infectedHex,virus): 
                    i = 0
                    while i < len(app.playerCells):
                        cell = app.playerCells[i]
                        if cell.hex == infectedHex: 
                            app.playerCells.pop(i)
                        else: 
                            i += 1
                    if len(app.playerCells) == 0: 
                        app.gameOver = True
                else: 
                    damage = getVirusDamage(virus)
                    infectedHex.hexHealthIndex += damage
                virus.dead = True

            elif not virus.moving: 
                time.sleep(1)
                virus.hidePath()
                virus.moving == True
            virus.moveVirus()
            i += 1



def runYoukaryote():
    runApp(SCREENWIDTH, SCREENHEIGHT) 

runYoukaryote()
cmu_graphics.run()



 




