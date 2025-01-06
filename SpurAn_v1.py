#################################################################
## Crossing Spurious Analysis Script
##
## Can read a csv file with spur levels of a harmonic mixer
## then iterate through all harmonics associated with the
## RF range and fixed LO.  Then plots the spurs that fall within
## the designated IF range.
##
## REF: https://www.microwaves101.com/encyclopedias/mixer-spur-chart
##
## Hovering over the spur lines will display the harmonic
## combination (mRF X nLO) and level (dBc)
##
## If no mixer file is selected, the default Mini-Circuits ASK-1+
## parameters are used.
##
## Mixer harmonic files must have *.spr extension and use csv
#################################################################
# To Do: add filter to show only spurs above designated threshold 
#        (maybe use alpha parameter proportional to level)
# To Do: add standard filter types (e.g. Chebychev) that can be selected 
#        for RF and IF and filter out-of-band spurs or
# To Do: draw rectangles for 3 dB, 20 dB, and 40 dB BW



import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QSpinBox, QDoubleSpinBox, QMessageBox, QRadioButton, QFileDialog
#from PyQt5.QtCore import pyqtSignal, pyqtSlot  ## may need later

import numpy as np
import csv

#################################################################
#### import matplotlib classes to enable plots in PyQt5
#################################################################
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import mplcursors  # used to display info when hovering over plot lines


version = "1.0"
date = "Feb 17, 2020"

#### Mini-Circuits ASK-1+ RF@-14 dBm, LO@+7 dBm
#### https://www.minicircuits.com/pages/s-params/ASK-1+_VIEW.pdf
#### Rows are RF harmonics [0..10]; Columns are LO harmonics [0..10]
#### Levels are -dBc
harmonicsTable = [[99, 17,  9, 14, 34, 19, 29, 27, 36, 34, 45],
                  [19,  0, 30, 11, 29, 25, 38, 36, 43, 43, 51],
                  [57, 60, 59, 64, 55, 56, 61, 59, 68, 62, 60],
                  [62, 69, 65, 62, 69, 59, 70, 70, 70, 70, 70],
                  [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70],
                  [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70],
                  [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70],
                  [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70],
                  [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70],
                  [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70],
                  [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70]]



#################################################################
class MplFigure(object):
    def __init__(self, parent):
        self.figure = plt.figure(facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        #self.toolbar = NavigationToolbar(self.canvas, parent) # not needed in simple plot
        #plt.style.use('seaborn-whitegrid')  # does not seem to be supported any longer
#################################################################


        
#################################################################
class uiMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Spur Analyzer UI.ui', self)  #### load Qt Designer UI design
        self.setWindowTitle("Spur Analyzer v" + version)
        self.file_label.setText("Mixer File: Default (MCL ASK-1+)")
       
        #### Connect signals from menu item selections ####
        self.actionOpen_Mixer_File.triggered.connect(lambda: self.clicked("Open Mixer File Was Clicked"))
        self.actionAbout.triggered.connect(lambda: self.clicked("About Was Clicked"))
        self.actionExit.triggered.connect(sys.exit)
        
        #### Connect signals from entry box changes ####
        self.loDoubleSpinBox.valueChanged.connect(self.onValueChanged)
        self.maxHarmSpinBox.valueChanged.connect(self.onValueChanged)

        self.rfMaxDoubleSpinBox.valueChanged.connect(self.onValueChanged)
        self.rfMinDoubleSpinBox.valueChanged.connect(self.onValueChanged)

        self.ifMaxDoubleSpinBox.valueChanged.connect(self.onValueChanged)
        self.ifMinDoubleSpinBox.valueChanged.connect(self.onValueChanged)

        self.useAlphaRadioButton.clicked.connect(self.onValueChanged)
    
        #### Setup and initialize plotting area in the verticalLayout box ####
        self.main_figure = MplFigure(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        #self.verticalLayout.addWidget(self.main_figure.toolbar)
        self.verticalLayout.addWidget(self.main_figure.canvas)
        self.initMplWidget()



    #################################################################
    #### initialize MatPlotLib plot and update with default values
    #################################################################
    def initMplWidget(self):
        self.ax = self.main_figure.figure.add_subplot(111)

        self.onValueChanged() # call event handler that reads input and updates plot
    #################################################################


    #################################################################
    #### added this method to handle clicking menu items and display
    #### text that is passed using the triggered/clicked connects
    #################################################################
    def clicked(self, text):
        #self.setStatusTip(text)

        if text == 'Open Mixer File Was Clicked':
            fileName, _ = QFileDialog.getOpenFileName(self, "Open Mixer Harmonics File", "",
                                                     "Spur Analyzer Files (*.spr);;All Files (*)")
            if fileName:
                try:
                    with open(fileName, "r") as mixerFile:
                        m=0
                        mixerTable = csv.reader(mixerFile, delimiter=',')
                        for row in mixerTable:
                            harmonicsTable[m] = [int(i) for i in row]
                            m+=1                        
                    self.file_label.setText("Mixer File: " + fileName)
                except Exception:
                    QMessageBox.warning(self,"Spur Analyzer - File Open Warning",
                    "Open: " + fileName + "\n\nFile not compatible with Spur Analyzer v" + version)
        
            self.onValueChanged() # update to reflect read parameters


        if text == 'About Was Clicked':
            QMessageBox.about(self, "Spur Analyzer", 
                                    "Spur Analyzer \n" +
                                    "Version: " + version + "\n" +
                                    "Author: Steve Harbin \n" +
                                    "Date: " + date + "\n" + 
                                    "----------------------- \n" +
                                    "Mixer Spurious Signal Analysis \n" +
                                    "Based on traditional crossing spur techniques " )

        # To Do: Add handlers for other menu actions if added                            
    #################################################################



    #################################################################
    #### added this method to handle changes in spinner boxes and 
    #### display new value calculations then update plot
    #################################################################
    #@pyqtSlot()   # Do I need this??
    def onValueChanged(self):
        
        self.rfMin = self.rfMinDoubleSpinBox.value()
        self.rfMax = self.rfMaxDoubleSpinBox.value()
        self.ifMin = self.ifMinDoubleSpinBox.value()
        self.ifMax = self.ifMaxDoubleSpinBox.value()
        self.lo = self.loDoubleSpinBox.value()
        self.maxHarm = self.maxHarmSpinBox.value()


        self.updatePlot() 
    #################################################################



    #################################################################
    #### Returns color intensity of each curve proportional to the  
    #### level of the corresponding spur if 'Use Alpha' is checked
    #################################################################
    def lineAlpha(self, m, n):
        if self.useAlphaRadioButton.isChecked():
            #lineAlpha = min([1/(.15*(abs(m)+abs(n))**2.5+.01), 1])
            #lineAlpha = min([14/(harmonicsTable[abs(m)][abs(n)]+.01), 1])
            x = harmonicsTable[abs(m)][abs(n)]
            lineAlpha = -0.000659*(x**2) + 0.033619*x + 1
            if (lineAlpha < 0): lineAlpha = 0
            if (lineAlpha > 1): lineAlpha = 1
        else: 
            lineAlpha = 1
        return lineAlpha
    #################################################################


 
    #################################################################
    #### Recalculate and Redraw plot when values changed from     
    #### the User Interface                                      
    #################################################################
    def updatePlot(self):
        
        self.ax.clear()  #also clears titles and gridlines, etc.  Is there a better way to do this?

        self.ax.set_title('Mixer Crossing Spurious Analysis') 

        self.ax.set_xlabel('RF (MHz)') 
        self.ax.set_ylabel('IF (MHz)') 

        self.ax.set_xlim(np.floor(0.9*self.rfMin), np.ceil(1.1*self.rfMax))
        self.ax.set_ylim(np.floor(0.9*self.ifMin), np.ceil(1.1*self.ifMax))
        
        self.ax.grid(visible=True, which='both') 


        # Cycle through all harmonics (mRF x nLO) and plot the spur lines
        rfRange = np.linspace(np.floor(0.9*self.rfMin), np.ceil(1.1*self.rfMax), num=200)
        for m in range(-self.maxHarm, self.maxHarm+1):
            for n in range(-(self.maxHarm-abs(m)), self.maxHarm-abs(m)+1):
            #for n in range(-self.maxHarm, self.maxHarm+1):

                # Define the label to display when hovering over curves
                spur_label = (str(m)+ 'RF'+'x'+str(n)+'LO -'+
                              str(harmonicsTable[abs(m)][abs(n)])+' dBc')

                # Plot the main (1x1) spur lines with heavier lines
                lwidth = 1.5 # default width
                if (abs(m)==1 and abs(n)==1): lwidth = 3 

                # Tune through RF range values, calculate and plot corresponding IF values
                xRange = []
                yRange = []
                for RF in rfRange:
                    IF = (m*RF + n*self.lo)
                    yRange = np.append(yRange, IF)
                    xRange = np.append(xRange, RF)
                self.ax.plot(xRange, yRange, alpha=self.lineAlpha(m,n), linewidth=lwidth, 
                             label=spur_label)



        # Calculate and plot the filter boundary box based on RF and IF ranges
        rfFilterMin = self.rfMin
        rfFilterMax = self.rfMax
        ifFilterMin = self.ifMin
        ifFilterMax = self.ifMax

        xValues = [rfFilterMin, rfFilterMin, rfFilterMax, rfFilterMax, rfFilterMin]
        yValues = [ifFilterMin, ifFilterMax, ifFilterMax, ifFilterMin, ifFilterMin]
        self.ax.plot(xValues, yValues, linestyle='--', color='b', linewidth=2, 
                     label='Filter Bounds', marker='o') 

        

        # Interactively display the label when cursor hovers over a line
        mplcursors.cursor(hover=mplcursors.HoverMode.Transient).connect(
           "add", lambda sel: sel.annotation.set_text(sel.artist.get_label()))

        self.ax.figure.canvas.draw()        
    #####################################################################################

        


#######################################
#### Start application and UI Loop ####
#######################################
if __name__ == "__main__":
    app = QApplication(sys.argv)        
    ui = uiMainWindow()
    ui.show()
    sys.exit(app.exec_())
######### End of application ##########

