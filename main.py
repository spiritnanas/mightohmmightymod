# Display Image & text on I2C driven ssd1306 OLED display 
from machine import Pin, I2C, SPI
from ssd1306 import SSD1306_I2C
from time import sleep
import utime
from math import floor
import sdcard
import os
import _thread
from micropython import mem_info

sleep(1)

#sLock = _thread.allocate_lock()

counts = 0 #geiger counts registered 
cumUsv = 0 #Cumulative micro servets
mainMenuReset = False
downButton = False
upButton = False
centerButton = False
leftButton = False
navCursor = 1

#Init SD Card
spi=SPI(1,baudrate=9600,sck=Pin(10),mosi=Pin(11),miso=Pin(12)) #12=MISO,11=MOSI,10=SCK
try:
    sd=sdcard.SDCard(spi,Pin(13)) #13 is chip select (cs) pin
    vfs=os.VfsFat(sd)
    os.mount(sd,'/sd')
    print(os.listdir('/sd'))

except:
        print("SD Card Not Installed")
    



#Hardware Interupts
def countCpm(p):                                        #Triggered by interupt pin, counts per minute from geiger counter
    global counts
    counts += 1

def mainMenu(p):
    global mainMenuReset
    mainMenuReset = True
    
def down(p):
    global downButton
    downButton = True

def up(p):
    global upButton
    upButton = True
    
def center(p):
    global centerButton
    centerButton = True
    
def left(p):
    global leftButton
    leftButton = True
    
interuptPin0 = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
interuptPin0.irq(trigger=interuptPin0.IRQ_FALLING, handler=countCpm)

#reset
interuptPin4 = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
interuptPin4.irq(trigger=interuptPin0.IRQ_RISING, handler=mainMenu)

 #down
interuptPin6 = machine.Pin(7, machine.Pin.IN, machine.Pin.PULL_UP)
interuptPin6.irq(trigger=interuptPin0.IRQ_RISING, handler=down)

 #up
interuptPin8 = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_UP)
interuptPin8.irq(trigger=interuptPin0.IRQ_RISING, handler=up)


interuptPin19 = machine.Pin(19, machine.Pin.IN, machine.Pin.PULL_UP)#Center
interuptPin19.irq(trigger=interuptPin0.IRQ_RISING, handler=center)

#left
interuptPin7 = machine.Pin(8, machine.Pin.IN, machine.Pin.PULL_UP)#Center
interuptPin7.irq(trigger=interuptPin0.IRQ_RISING, handler=left)

#Display setup
WIDTH  = 128                                            # oled display width
HEIGHT = 64                                             # oled display height
i2c = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)       # Init I2C using pins GP8 & GP9 (default I2C0 pins)
print("I2C Address      : "+hex(i2c.scan()[0]).upper()) # Display device address
print("I2C Configuration: "+str(i2c))                   # Display I2C config
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)                  # Init oled display
oled.fill(0)                                            # Clear the oled display in case it has junk on it.


def getTimeStamp():
    rtc = machine.RTC()
    tStamp = rtc.datetime()
    timeString="%04d-%02d-%02d_%02d-%02d-%02d"%(tStamp[0:3] + tStamp[4:7])
    return timeString

def collectData(period):
    global counts
    global cumUsv
    global mainMenuReset
    global centerButton
    counts = 0
    x = 0
    while (x < period * 2): 
        sleep(period / (period * 2))
        x += 1
        if mainMenuReset == True:
            mainMenuReset = False
            return False
    cpm = counts * (60/period)
    usvh = cpm * .0057
    cumUsv += (usvh / ((60 * 60) / period))
    return [period,cpm,str(counts),usvh,getTimeStamp(),cumUsv]
        

def sdCardOutput(fileName,lineToWrite):
    try:
        file = open(fileName,"a")
        file.write(lineToWrite)
        file.close()
    except:
        print("SD Card Not Installed")

def initCsvHeader(fileName, csvHeader):
    #Creates CSV file header.
    sdCardOutput(fileName, csvHeader)

def dataLine(cDO):
    #Formats the data line for enttry into csv (ex. 5, 0.0, '0', 0.0, '2022-05-23_22-57-56', 0.0,)
    return("{},{},{},{},{},{},".format(cDO[0],cDO[1],cDO[2],cDO[3],cDO[4],cDO[5]))

class dataCollectionObj:
    def __init__(self, period, logType, infinite, iterations):
        self.period = period
        self.logType = logType
        self.infinite = infinite
        self.iterations = iterations
        
    def dataLoggingDisplayOut(self,runningAvg,data,period,itterations = 1,curItteration = 1):
        oled.fill(0)
        if itterations != 1:
            curX = floor(((curItteration/itterations)) * 128)
            oled.fill_rect(0, 0, curX, 8, 1)
        else:
            oled.fill_rect(0, 4, 128, 12, 1)
            oled.text("Cont. Metering",4, 6,0)

        oled.text("{:.3f} uSv/h".format(data[3]),0,16)
        oled.text("{:.3f} Cum. uSv".format(data[5]),0,24)
        oled.text("{:.3f} Last 4 Avg uSv/h".format(runningAvg),0,34)
        oled.text("Reset x2 to exit.",0,56)
        #oled.text("Menu",0,56)
        oled.show()

    def logTimed(self):
        global mainMenuReset
        #Clears the display and informs the user that the data collection has started
        oled.fill(0)
        oled.text("Data collection",5,16)
        oled.text("started!",5,26)
        oled.text("Please wait " + str(self.period) + "s",5,36)
        oled.show()
        #Create CSV file with header
        header = "avgPeriod,cpm,counts,usvh,timestamp,cumUsvSinceStart,\n"
        fileOut = "/sd/radCollect_" + getTimeStamp() + ".csv"
        initCsvHeader(fileOut, header)
        x = 0
        runningAvg = [0,0,0,0]
        runningAvgCounter = 0
        #Iterations is a property of the dataCollectionObj that defines how many itterations
        #a data logging session should run for.
        while x < self.iterations:
            x += 1
            #mainMenuReset is set by an interupt.
            if mainMenuReset == True:
                break
            #Checks to see if the class propery infinite is True. If it is, this while loop will run till broken,
            #collecting data infinitly. 
            if self.infinite:
                x = 1        
            data = collectData(self.period)
            #This checks to see if the mainMenuReset has been trigged mid collection cycle, this is to provide faster
            #UI response when buttons are pressed to reset. 
            if data == False:
                break
            
            #Calculates a running average by keeping track of and averaging the last four values. 
            runningAvg[runningAvgCounter] = data[3]
            runningAvgCounter += 1
            if runningAvgCounter > 2:
                runningAvgCounter = -1
            runningAvgRes = 0
            for y in range(0, len(runningAvg)):
                runningAvgRes += runningAvg[y]
            runningAvgRes = runningAvgRes/len(runningAvg)
            print(runningAvgRes)
            #Puts the result of the latest data collection period on the screen
            self.dataLoggingDisplayOut(runningAvgRes,data,self.period)            
            #Converts the data to CSV format
            data = str(data)
            data = data[1:(len(data)-1)] + ",\n"
            print(data)
            #Writes the data to the SD Card.
            sdCardOutput(fileOut,str(data))
            
        while(mainMenuReset == False):
           continue 
        
        return "resetDisplay"

class dataGraphObj:

    def __init__(self, period, logType, infinite, iterations):
        self.period = period
        self.logType = logType
        self.infinite = infinite
        self.iterations = iterations
        
    def graphDisplayOut(self,data,period,graphCoords):
        oled.fill(0)
        oled.fill_rect(0, 0, 128, 12, 1)
        oled.text("Graph|",0, 2,0)
        oled.text("{:.3f}uSvh".format(data[3]),50,2,0)
        for x in graphCoords:
            oled.fill_rect(x[0],x[1],x[2],x[3],1)
            #oled.fill_rect(x[0]-6,x[1],x[2]-6,x[3],0)
        #oled.fill_rect(128-4,64-40, 128, 64, 1)
        
        
        oled.show()

    def graphData(self):
        global mainMenuReset
        #Clears the display and informs the user that the data collection has started
        oled.fill(0)
        oled.text("Data collection",5,16)
        oled.text("started!",5,26)
        oled.text("Please wait " + str(self.period) + "s",5,36)
        oled.show()
        x = 0
        
        screenSizeX = 128
        screenSizeY = 64
        screenDivisions = 32
        divisionSize = int(floor(screenSizeX / screenDivisions))
        
        graphCoords = []
        
        while True:
            #mainMenuReset is set by an interupt.
            if mainMenuReset == True:
                break       
            data = collectData(self.period)
            #This checks to see if the mainMenuReset has been trigged mid collection cycle, this is to provide faster
            #UI response when buttons are pressed to reset. 
            if data == False:
                break
            
            if len(graphCoords) >= screenDivisions:
                try:
                    graphCoords.pop(0)
                except:
                    print("List is empty!")
                graphCoords.append([screenSizeX - divisionSize, screenSizeY - int(data[2]),divisionSize,screenSizeY])
            else:
                graphCoords.append([screenSizeX - divisionSize, screenSizeY - int(data[2]),divisionSize,screenSizeY])
            for x in range(0,len(graphCoords)-1):
                graphCoords[x][0] = graphCoords[x][0] - divisionSize
                #graphCoords[x][2] = graphCoords[x][2] - divisionSize
            
            print(graphCoords)
            
            #Puts the result of the latest data collection period on the screen
            self.graphDisplayOut(data,self.period,graphCoords)            
            #Converts the data to CSV format
            data = str(data)
            data = data[1:(len(data)-1)] + ",\n"
            print(data)
        
        while(mainMenuReset == False):
           continue 
        return "resetDisplay"    
    
#UI Classes
    
class uiObject:
    def __init__(self, uiType, sizeX, sizeY, name,):
        #uiObject is intended to be an abstract class. 
        self.uiType = uiType
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.name = name
        
class button(uiObject):
        #button objects are intended to be UI elements that can be interacted with. 
    def __init__(self, buttonType, pressed,uiType, sizeX, sizeY, name):
        self.buttonType = buttonType
        self.pressed = pressed
        
        uiObject.__init__(self,uiType, sizeX, sizeY, name)

class navFrame(uiObject):
        #navFrames contain collections of navPanes. navPanes are the individual menus, navFrames group them together
        #into menues that can be scrolled through. 
    def __init__(self,uiType, sizeX, sizeY, name, menu):
        self.name = name
        self.menu = menu
        
        uiObject.__init__(self,uiType, sizeX, sizeY, name)
        
    def mainMenuResetRender(self):
        #This function is designed to be used with the reset interupt and will return the user to
        #the menu after having clicking on an object in the menu upon clicking the reset button. 
        global mainMenuReset
        mainMenuReset = False
        oled.fill(0)
        renderMainMenu(self.menu,-1, 1)
    def render(self):
        #This contains the logic to render the navFrames on screen. 
        global upButton
        global downButton
        global mainMenuReset
        global centerButton
        global leftButton
        
        #Zeros out the screen to remove previously drawn frame
        oled.fill(0)
        #navPane buttons are stored in an array. This navCursor defines which one is currently highlighted. 
        lnavCursor = 1
        #resets buttons to false state. This is because the interupts used to navigate this menu change the values of
        #the global variables used for navigation, so when this is called again to render new information, it does not
        #count as another button "press".
        centerButton = False
        leftButton = False
        while centerButton != False:
            continue
        renderMainMenu(self.menu,1)
        self.menu[1].highlighted = True
        self.menu[1].drawObj()
        self.menu[1].highlighted = False
        
        while (True):
            sleep(.05)
            if (upButton == True) and (lnavCursor > 1):
                lnavCursor -= 1
                self.menu[lnavCursor].up(self.menu, lnavCursor)
                
                
            elif (downButton == True) and (lnavCursor < (len(self.menu) -1)):
                lnavCursor += 1
                self.menu[lnavCursor].down(self.menu, lnavCursor)
                
                
            elif (centerButton == True):
                centerButton = False
                if(isinstance(self.menu[lnavCursor].link, navFrame) and self.menu[lnavCursor].link.uiType == "navFrame"):
                    self.menu[lnavCursor].link.render()
                elif(isinstance(self.menu[lnavCursor].link,dataCollectionObj)):
                    if self.menu[lnavCursor].link.logTimed() == "resetDisplay":
                        self.mainMenuResetRender()
                elif(isinstance(self.menu[lnavCursor].link,dataGraphObj)):
                    if self.menu[lnavCursor].link.graphData() == "resetDisplay":
                        self.mainMenuResetRender()
                        
                
            elif(centerButton == True):
                centerButton = False
            
            elif(leftButton == True and self.name != "Main Menu"):
                break
            
            if(leftButton == True):
                lnavCursor = 1
                renderMainMenu(self.menu,1)
                self.menu[1].highlighted = True
                self.menu[1].drawObj()
                self.menu[1].highlighted = False
                leftButton = False

            oled.show()

            
        
class navPane(uiObject):
    #navPanes are the individual menu objects. These can be highlighted/selected or not. 
    def __init__(self, highlighted,uiType, sizeX, sizeY, name, contentText, locX, link = False, backLink = False):
        self.highlighted = highlighted
        self.contentText = contentText
        self.locX = locX
        self.link = link
        uiObject.__init__(self,uiType, sizeX, sizeY, name)
    
    #Draws the navPane with the given parameters.
    def drawObj(self):
        if(self.highlighted == True):
            oled.fill_rect(0, self.locX, self.sizeX, self.sizeY, 1)
            oled.text(self.contentText,4, self.locX + 2,0)
        else:
            oled.rect(0, self.locX, self.sizeX, self.sizeY, 1)
            oled.text(self.contentText,4, self.locX + 2)
            
    def up(self, menu, lnavCursor):
        #If the global upButton variable is True this calls "renderMenu"
        global upButton
        self.renderMenu("up",menu, lnavCursor)
        upButton = False
        menu[lnavCursor].highlighted = True
        menu[lnavCursor+1].highlighted = False
        menu[lnavCursor].drawObj()
        menu[lnavCursor].highlighted = False
    def down(self, menu, lnavCursor):
        global downButton
        self.renderMenu("down",menu, lnavCursor)
        downButton = False
        menu[lnavCursor].highlighted = True
        menu[lnavCursor-1].highlighted = False
        menu[lnavCursor].drawObj()
        menu[lnavCursor].highlighted = False
        
    def renderMenu(self,direction,menu, lnavCursor):
        #Render menu calls renderMainMenu.
        if direction == "up":
            renderMainMenu(menu,lnavCursor)
        if direction == "down":
            renderMainMenu(menu,lnavCursor)
       



def renderMainMenu(menu,toSkip,curCursor = -1):
    #This function clears the display, then if the menu objects get evaluated for rendering.
    #It checks to see if the 
    #If the curCursor is not provided (ie. the value is -1) it is skipped. 
    oled.fill(0)
    for x in range(0, len(menu)):
        if ((menu[x].uiType == "MenuOption") and x != toSkip):
            menu[x].drawObj()
            if curCursor != -1:
                menu[curCursor].highlighted = True
                menu[curCursor].drawObj()
                menu[curCursor].highlighted = False

                
    oled.show()
    






def main():
    #UI Objects
    
    #TimedMeterMenuObjects
    logFiveSec = dataCollectionObj(5, "timedLog", False, 3)
    logTenSec = dataCollectionObj(10, "timedLog", False, 3)
    logSixtySec = dataCollectionObj(30, "timedLog", False, 3)
    logFiveMin = dataCollectionObj(300, "timedLog", False, 3)
    
    #ConstantMeteringObjects
    logCont = dataCollectionObj(5, "contLog", True, 10)
    
    graphData = dataGraphObj(1, "contLog", True, 10)
    
    #TimedMeterMenu
    timedMenu = navPane(highlighted = True,uiType = "MenuOption",sizeX = 128, sizeY = 12, name = "Timed Metering", contentText = "Timed Metering", locX = 4)
    fiveSecAvg = navPane(highlighted = False,uiType = "MenuOption",sizeX = 128, sizeY = 12, name = "5 Sec Avg", contentText = "5 Sec Avg", locX = 15, link = logFiveSec)
    tenSecAvg = navPane(highlighted = False,uiType = "MenuOption",sizeX = 128, sizeY = 12, name = "10 Sec Avg", contentText = "10 Sec Avg", locX = 26, link = logTenSec)
    thirtySecAvg = navPane(highlighted = False,uiType = "MenuOption",sizeX = 128, sizeY = 12, name = "30 Sec Avg", contentText = "30 Sec Avg", locX = 37, link = logSixtySec)
    minAvg = navPane(highlighted = False,uiType = "MenuOption",sizeX = 128, sizeY = 12, name = "5 Min Avg", contentText = "5 Min Avg", locX = 48, link = logFiveMin)

    timedUiArr = [timedMenu,fiveSecAvg,tenSecAvg,thirtySecAvg,minAvg]
    timedMenu = navFrame("navFrame", 128, 64, "Timed Menu", timedUiArr)

    #MAIN MENU
    mainMenu = navPane(True,"MenuOption",128,12,"Main Menu", "Main Menu", 4)
    constantMeteringMenuOption = navPane(False,"MenuOption",128,12,"constantMeteringMenuOption", "Const. Metering", 15, logCont)
    timedMeterOptions = navPane(False,"MenuOption",128,12,"timedMeterOptions", "Timed Metering", 26, timedMenu)
    graphData = navPane(False,"MenuOption",128,12,"placeholder", "Graph",37, link = graphData)
    setup = navPane(False,"MenuOption",128,12,"SetupMenu", "Setup - TBD",48)


    uiArr = [mainMenu, constantMeteringMenuOption, timedMeterOptions, graphData, setup]
    mainMenu = navFrame("navFrame", 128, 64, "Main Menu", uiArr)
    #renderMainMenu(uiArr)
    

    mainMenu.render()
    #navArray(uiArr)
    #navArray(timedUiArr)
    
   

main()


