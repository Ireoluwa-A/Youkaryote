from cmu_cs3_graphics import *
from constants import *
import math, random



def drawUi(app):
    drawPlayPause(app)
    # drawPlayerStats(app)

def drawPlayPause(app):
    if app.paused: 
        fill='red'
        # Pause button
        drawRect(32,app.height-50,5,15,fill=fill) 
        drawRect(40,app.height-50,5,15,fill=fill)
    else: 
        fill='lightGreen'
        # Play button
        drawRegularPolygon(35,app.height-40,10,3,fill=fill,rotateAngle=90)

    # Lines around
    drawLine(40,app.height-40,app.width-40,app.height-40,fill=fill,lineWidth=3)
    drawLine(35,app.height-40,30,100,fill=fill,lineWidth=3) 
 
def drawPlayerStats(app):
    # Player name and level
    drawRect(30,30,150,50,fill='white')

def drawGrayBackground(app):
    drawRect(0,0,app.width,app.height,fill=MAPBGCOLOR)


def drawVirus(x,y,size,):
    # Draws body
    drawCircle(x,y-size,size//2,fill='green')
    drawOval(x,y,size,size+size//2,fill='green')

    # Draws antennaes
    drawLine(x,y-size,x,y-size*2,fill='black')
    # drawArc(x,y,size,size,)

# Arc(centerX, centerY, width, height, startAngle, sweepAngle, fill='black',
#     border=None, borderWidth=2, opacity=100, rotateAngle=0, dashes=False,
#     visible=True)