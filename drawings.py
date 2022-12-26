from cmu_graphics import *
from constants import *
import math, random

from helpers import *
from PIL import Image, ImageDraw


# Drawing screen before game starts
def drawCurrScreen(app):
    currScreen = app.currScreen
    if currScreen == 'splashScreen':
        drawSplashScreen(app)
    elif currScreen == 'play':
        return
    elif currScreen == 'settings':
        drawSettingsScreen(app)
    elif currScreen == 'instructions':
        drawInstructionsScreen(app)

##### SCREEN DRAWINGS ####

# HOME SPLASH SCREEN DRAWINGS
def drawSplashScreen(app):
    drawSplashBackground(app)
    drawGameTitle(app)
    drawGameButtons(app)
    
def drawSplashBackground(app):
    # Top row
    drawImage('images/dot-grid.png',0,0)
    drawImage('images/dot-grid.png',400,0)
    drawImage('images/dot-grid.png',800,0)
    drawImage('images/dot-grid.png',1200,0)
    # Bottom row
    drawImage('images/dot-grid.png',0,400)
    drawImage('images/dot-grid.png',400,400)
    drawImage('images/dot-grid.png',800,400)
    drawImage('images/dot-grid.png',1200,400)

def drawGameTitle(app):
    yPos = 220
    fontSize = 60
    drawLabel('Y O U',app.width/2 - 200, yPos,size=fontSize,align='center',font=TITLEFONT,fill='red',bold=True)
    drawLabel('K A R Y O T E',app.width/2 + 110, yPos,size=fontSize,align='center',font=TITLEFONT,fill='black',bold=True)

def drawGameButtons(app):
    for button in app.homeButtons: 
        button.drawButton()

# SETTINGS SCREEN DRAWINGS
def drawSettingsScreen(app):
    drawImage('images/virusbackground.jpeg',0,0)
    rectWidth,rectHeight = 700,600
    # Shadow
    drawRect(app.width/2 - rectWidth/2 - 10,app.height/2-rectHeight/2 + 10,rectWidth,rectHeight,fill='black',opacity = 60)
    # white box
    drawRect(app.width/2 - rectWidth/2,app.height/2-rectHeight/2,rectWidth,rectHeight,fill=OFFWHITE)
    drawLabel("M A P  S E T T I N G S", app.width/2, 150,fill='black',size=30,bold=True)
    drawLabel("V I R U S  S E T T I N G S", app.width/2, app.height/2 + 30,fill='black',size=30,bold=True)

    # Draw settings buttons
    for button in app.settingsButtons: 
        button.drawButton(app)


# INSTRUCTIONS SCREEN DRAWINGS
def drawInstructionsScreen(app):
    drawGrayBackground(app)
    left, top = app.width/2, app.height/2 - 200
    drawLabel('S u r v i v e   a n d   C o n q u e r',left,top,size=35,bold=True,fill='white')

    drawLabel('Press s for important statistics and info',left,top+130,size=20,fill='white')
    drawLabel('Press p to toggle pause',left,top+160,size=20,fill='white')
    drawLabel('Press m to go to map view',left,top+190,size=20,fill='white')
    drawLabel('Press c to go to cell view',left,top+220,size=20,fill='white')
    drawLabel('When placing an organelle, click to pick it up and click again to place it',left,top+250,size=20,fill='white')
    drawLabel('Left and right arrow keys in cell view to cycle between cells you own',left,top+280,size=20,fill='white')

    # Draw settings buttons
    for button in app.instructionButtons: 
        button.drawButton(app)


def drawGameOverScreen(app):
    drawLabel('G A M E   O V E R',app.width/2,app.height/2-50,size=40,fill='white',font=TITLEFONT)
    drawLabel('press r to try again',app.width/2,app.height/2,size=15,fill='red',font=TITLEFONT)

def drawGameWonScreen(app):
    drawLabel('Y O U  W I N',app.width/2,app.height/2-50,size=40,fill='white',font=TITLEFONT)
    drawLabel('press r to replay',app.width/2,app.height/2,size=15,fill='green',font=TITLEFONT)

def drawLoadingScreen(app):
    drawLabel('Press s for extra information on your cell and map',app.width/2,app.height/2,fill='white',size=30)




# UI DRAWING FUNCTIONS###
def drawUi(app):
    drawPlayPause(app)
    if not app.mapView:  
        drawPlayerStats(app)
        drawOrganellesContainer(app)
        drawOrganelleOptions(app)
    else: 
        drawProgressBar(app)

def drawPlayPause(app):
    if app.pauseGame: 
        fill=PAUSEBTNCOLOR
        # Pause button
        drawRect(32,app.height-50,5,15,fill=fill) 
        drawRect(40,app.height-50,5,15,fill=fill)
    else: 
        fill=PLAYBTNCOLOR
        # Play button
        drawRegularPolygon(35,app.height-40,10,3,fill=fill,rotateAngle=90)

    # Lines around
    # Bottom line
    drawLine(40,app.height-40,app.width//2 + 100,app.height-40,fill=fill,lineWidth=3)
    # Top line
    drawLine(35,app.height-40,35,200,fill=fill,lineWidth=3) 
 
def drawPlayerStats(app):
    currCell = getCurrCell(app)

    # PLAYER NAME
    rectWidth, rectHeight = 150,50
    rectX,rectY = 30,30

    # Background box
    drawRect(30,30,150,50,fill='white')
    # Cell name
    drawLabel(f"{app.playerName}'s {currCell.label}",rectX + rectWidth//2, rectY + rectHeight//2,size=20,align='center',font='MONOSPACE')

    drawPowerStats(currCell)
    drawProteinStats(currCell)

def drawPowerStats(currCell):
    # Electricity symbol
    drawImage('images/light.png',50,90,width=40,height=40)

    # ATP Level
    drawLabel(currCell.stats['ATP'],120,100,size=15,fill='white',bold=True)
    
def drawProteinStats(currCell):
    drawImage('images/protein.png',50,140,width=40,height=30)
    drawLabel(currCell.stats['Protein'],120,150,size=15,fill='white',bold=True)

def drawOrganellesContainer(app):
    border = 'red' if app.pauseGame else 'lightGreen'
    fill = None
    drawRect(app.width//2 + 100,app.height - 100,500,90,border=border,fill=None)

def drawOrganelleOptions(app):
    for organelleOption in app.organelleOptions:
        organelleOption.drawOrganelle()

def drawProgressBar(app):
    border = 'red' if app.pauseGame else 'lightGreen'
    boxWidth, boxHeight = 320, 50
    drawRect(app.width//2 + 100,app.height - 65,boxWidth,boxHeight,border=border,fill=None)
    
    fill ='red' if app.pauseGame else 'lightGreen'
    # Progress bar
    if app.mapFill <= 0: 
        progWidth = 0.01
    else: 
        progWidth = app.mapFill

    # progWidth = 0.5 * boxWidth
    drawRect(app.width//2 + 100, app.height - 65, progWidth * boxWidth,boxHeight,fill=fill)

    # Percent label
    drawLabel(f"{rounded(progWidth*100)}%",app.width - 440,app.height-40,fill='white',bold=True,size=20)


# DRAW NOTIFICATIONS
def drawUpdatedStatsNotif(x,y,resource,amount):
    fill, sign = ('red','-') if amount < 0 else ('green','+')
    drawLabel(f'{amount}{resource}',x+25,y-15,size=15,fill=fill,bold=True)

def drawMeitosisCost(cost,mx,my):
    drawLabel(f'-{cost} ATP', mx, my-15, bold=True,fill='red',size=10)

def drawPlacementFailedNotif(app,reason):
    rectWidth, rectHeight = app.width,400
    drawRect(0,app.height/2 - rectHeight/2,rectWidth,rectHeight,fill='black',opacity=70)
    drawLabel(reason,app.width/2,app.height/2,size=30,fill='red',font='monospace')

def drawMeitosisAlert(app,cell):
    drawRect(0,0,app.width,app.height,fill=None,borderWidth=5,border = 'gold')

def drawNotif(app):
    rectWidth, rectHeight = app.width,400
    drawRect(0,app.height/2 - rectHeight/2,rectWidth,rectHeight,fill='black',opacity=70)
    drawLabel(app.notif,app.width/2,app.height/2,size=30,fill='red',font='monospace')


# CLASS HELPER DRAWING FUNCTIONS ###
def drawNucleusOptions(nucleus):
    left = nucleus.x+nucleus.width - 50
    top = nucleus.y
    rectWidth, rectHeight = 200,100
    drawRect(left,top,rectWidth,rectHeight,opacity=80,fill='black')
    drawLabel("Unlock Centrosomes",left + rectWidth/2, top+10,fill='white',size=15)
    drawLabel('50 ATP and 30 protein required',left + rectWidth/2,top + 30,fill='red',size=10)
    drawLabel("Repair cell wall ",left + rectWidth/2, top+60,fill='white',size=15)
    drawLabel('30 ATP and 30 protein required',left + rectWidth/2,top + 80,fill='red',size=10)

def drawCellStats(app,cell):
    left, top = cell.cx - 500, cell.cy - 50
    rectWidth, rectHeight = 200,280
    drawRect(left, top,rectWidth,rectHeight,fill='black',opacity=70)

    # Corner lines
    drawLine(left + rectWidth - 25,top, left + rectWidth ,top,fill='white',lineWidth=2)
    drawLine(left + rectWidth,top, left + rectWidth,top + 25,fill='white',lineWidth=2)
    drawLine(left,top + rectHeight - 25, left,top + rectHeight,fill='white',lineWidth=2)
    drawLine(left,top + rectHeight, left + 25,top + rectHeight,fill='white',lineWidth=2)


    drawLabel(f'{cell.label} Stats',left + rectWidth//2, top + 20,size=20,fill='white', bold=True)

    # Cell health
    health, energyProd, proteinProd, proteinFailureRate = getCellStats(cell)
    drawLabel(f"Curr cell health: {health}%",left + rectWidth//2, top + 60, size = 15,fill='white')

    # Mitochondria production rate 
    drawLabel(f"Energy production: {energyProd}",left + rectWidth//2, top + 80, size = 15,fill='white')

    # Protein production rate
    drawLabel(f"Protein production: {proteinProd}",left + rectWidth//2, top + 100, size = 15,fill='white')

    # Protein failure rate: WIP
    drawLabel(f"Protein failure rate (WIP): {proteinFailureRate}",left + rectWidth//2, top + 120, size = 15,fill='white')

    drawLabel("Progress to Mitosis",left + rectWidth/2, top + 170, size=15,fill='white')
    atpLevel = cell.stats['ATP']
    atpFill = 'red' if atpLevel < app.meitosisATPreq else 'green'
    drawLabel(f"{atpLevel}/{app.meitosisATPreq}",left + rectWidth/2, top+ 190, size=15,fill=atpFill)

    proteinLevel = cell.stats['Protein']
    proteinFill = 'red' if atpLevel < app.meitosisProteinReq else 'green'
    drawLabel(f"{proteinLevel}/{app.meitosisProteinReq}",left + rectWidth/2, top+ 210, size=15,fill=proteinFill)

    centrosomeFill = 'green'
    for organelle in app.organelleOptions:
        if organelle.locked:
            centrosomeFill = 'red'
    drawLabel(f"Centrosome",left + rectWidth/2, top+ 230, size=15,fill=centrosomeFill)

def drawCellHelper(cx,cy,width,height,rotateAngle):
    drawCellBottom(cx,cy,width,height,rotateAngle)
    drawCellPlatform(cx,cy,width,height,rotateAngle)

def drawCellPlatform(cx,cy,cellWidth,cellHeight,cellRotateAngle):
    drawOval(cx,cy,cellWidth,cellHeight,rotateAngle=cellRotateAngle,fill=CELLFLOORCOLOR)

def drawCellBottom(cx,cy,cellWidth,cellHeight,cellRotateAngle):
    # Shadow on ground
    drawOval(cx,cy+cellHeight,cellWidth+50,cellHeight-50,rotateAngle=cellRotateAngle,fill=CELLSHADOWCOLOR)
    # Cell bottom
    drawArc(cx,cy,cellWidth,cellHeight*2,90,180,rotateAngle=cellRotateAngle,fill=CELLBOTTOMBASECOLOR)    



def drawVirus(x,y,size,):
    drawImage('protist.png',x,y,width=size,height=size)
 


# OTHER DRAWING HELPER FUNCTIONS ###
def drawGrayBackground(app):
    # drawImage('images/greyBG.jpeg',0,0,width=app.width,height=app.height)
    drawRect(0,0,app.width,app.height,fill=MAPBGCOLOR)

