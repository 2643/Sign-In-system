from __future__ import print_function
from PIL import Image
from PIL import ImageTk
import tkinter as tki
import threading
import datetime
import imutils
import cv2
import os
import time
import sys
import numpy as np
import zbar
import gspread
from oauth2client.service_account import ServiceAccountCredentials
#from jupyter_client.kernelspecapp import raw_input
import time
from datetime import *

class barcodeVid:

    def __init__(self):
        self.cap = cv2.VideoCapture(1)

    def cycle(self):
        ret, image = self.cap.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        cv2.imshow("Gray", gray)
        cv2.waitKey(10)
        return gray

    def end(self):
        #self.cap.release()
        cv2.destroyAllWindows()
        
        
class readBarcode():
    def __init__(self):
        print("ready to scan")
        
    def findImage(self, image):
        self.scanner = zbar.Scanner()
        results = self.scanner.scan(image)
        #print(results)
        #cv2.imshow('image', image)
        #cv2.waitKey(1)
        id = ""
        for result in results:
            #print(result.type, result.data, result.quality, result.position)
            id = result.data
            
        return id

class spreadsheet:
    
    #----Reference----
    # data = sheet.get_all_records()
    # result = sheet.row_values(1)
    # print(result)
    # print(idNum)
    # print(name.row)
    # dayFromF = time.localtime()
    # print(dayFromF)
    # print(dayFromF.tm_year)
    def __init__(self, spreadSheetName):
        self.scope = ["https://spreadsheets.google.com/feeds"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name("client_secret.json", self.scope)

        self.client = gspread.authorize(self.creds)
        self.isheet = self.client.open(spreadSheetName).sheet1
        self.osheet = self.client.open(spreadSheetName).get_worksheet(1)
        self.asheet = self.client.open(spreadSheetName).get_worksheet(2)
        self.row = None
        self.col = None
    
    # ##Finds day of sign in/out
    def findDay(self):
        day = datetime.today()
        date = str(day.month) + "/" + str(day.day)
        # print(date)
        findDate = self.isheet.find(date)
        # print(findDate.col)
        self.col = findDate.col
    
    def addTotalTime(self, row, col):
        listC = len(self.isheet.row_values(1))
        val = 0
        totalH = datetime.strptime('00:00:00', '%H:%M:%S').time()
        #print(totalH)
        inVal = self.isheet.cell(row, col).value
        outVal = self.osheet.cell(row, col).value
        addVal = self.asheet.cell(row, 5).value
        if addVal != "":
            totalH = datetime.strptime(addVal, '%H:%M:%S').time()
            #print(totalH)
            
        if inVal != "" and outVal != "":
            enterT = datetime.strptime(inVal, '%H:%M:%S').time()
            exitT = datetime.strptime(outVal, '%H:%M:%S').time()
            #print(enterT)
            #print(exitT)
            dif = datetime.combine(datetime.today(), exitT) - datetime.combine(datetime.today(), enterT)
            #print(dif)
            #dif = datetime.strptime(dif, '%H:%M:%S').time()
            totalH = datetime.combine(datetime.today(), totalH) + dif
            returnVal = str(totalH.hour) + ":" + str(totalH.minute) + ":" + str(totalH.second)
            #print(returnVal)
            self.asheet.update_cell(row, 5, returnVal)
        else:
            totalH = 0
    
    # ##adds time stamp to sign in/out
    def addTimeStamp(self, row, col):
        val = self.isheet.cell(row, col).value
        tt = datetime.today()
        ts = str(tt.hour) + ":" + str(tt.minute) + ":" + str(tt.second)
        if val != "":
            self.osheet.update_cell(row, col, ts)
            self.addTotalTime(row, col)
            return "Good bye "  
        else:
            self.isheet.update_cell(row, col, ts)
            return "Hello "

    # ##Finds the person and add data        
    def askForPerson(self, idNum):
        #idNum = raw_input("Enter Student id ")
        name = "test"
    
        self.findDay()
    
        try:
            name = self.isheet.find(idNum)
            self.row= name.row
        except:
            print("[INFO] Error, ID cannot be found")
            return -1, -1, ""
        state = self.addTimeStamp(self.row, self.col)
        return self.isheet.cell(self.row, 2), self.isheet.cell(self.row, 1), state
        #time.sleep(.5)
        #self.askForPerson()

class improvedGUI():
    def __init__(self, vs):
        self.vs = vs
        self.frame = None
        self.thread = None
        self.thread2 = None
        self.stopEvent = None
        self.stopEvent2 = None
        self.gFrame = None
        #self.useGui = gui()

        self.top = tki.Tk()
        self.var = tki.StringVar()
        self.label = tki.Label(self.top, text="Enter ID Number")
        self.label2 = tki.Label(self.top, text="Press Scan ID if you have ID")
        self.entry = tki.Entry(self.top)
        self.button = tki.Button(self.top, text="Find ID", command=self.on_button)
        self.button2 = tki.Button(self.top, text="Scan ID", command=self.checkVidT)
        self.button3 = tki.Button(self.top, text="Cancel Scan", command=self.cancelScan)
        self.message = tki.Message(self.top, textvariable = self.var, width = 200)
        self.panel = None
        
        self.firstN = ""
        self.LastN = ""
        self.vid = barcodeVid()
        self.read = readBarcode()
        self.results = ""
        self.s = spreadsheet("test")

        self.stopEvent= threading.Event()
        self.thread = threading.Thread(target = self.videoLoop, args=())
        self.thread.start()

        self.top.wm_title("Py SignIn System")
        self.top.wm_protocol("WM_DELETE_WINDOW", self.onClose)

    def pressed(self, test):
        self.on_button()
    
    def videoLoop(self):
        try:
            while not self.stopEvent.is_set():
                ret, self.frame = self.vs.read()
                self.frame = imutils.resize(self.frame, width = 750)

                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)
                
                if self.panel is None:
                    self.bind = self.top.bind('<Return>', self.pressed)
                    self.bind2 = self.top.bind('<KP_Enter>', self.pressed)
                    self.panel = tki.Label(image=image)
                    self.panel.image = image
                    self.panel.pack(side="left", padx=10, pady=10)
                    self.label.pack()
                    self.entry.pack()
                    self.button.pack()
                    self.label2.pack()
                    self.button2.pack()
                    self.button3.pack()
                    self.message.pack()
                else:
                    #print("updating video output")
                    #cv2.waitKey()
                    self.panel.configure(image=image)
                    self.panel.image = image
                    
        except RuntimeError as e:
            print("[INFO] caught a RuntimeError")
            quit()

    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        self.stopEvent.set()
        if self.stopEvent2 != None:
            self.stopEvent2.set()
        quit()
        sys.exit()
        self.top.quit()
        self.vs.release()
        cv2.destroyAllWindows()
        
    def getEntry(self, id):
        self.firstN, self.LastN, val = self.s.askForPerson(id)
        if self.firstN != -1:
            self.var.set(val + self.firstN.value + " " + self.LastN.value)
            self.entry.delete(0, len(self.entry.get()))
            self.message.pack()
        else:
            self.var.set("Error: No User Found")
            self.message.pack()
        
    def on_button(self):
        print("[INFO] running")
        id = self.entry.get()
        self.getEntry(id)
    
    def checkVidT(self):
        print("[INFO] Thread begins: ")
        self.stopEvent2 = threading.Event()
        self.thread2 = threading.Thread(target = self.video, args=())
        self.thread2.start()
    
    def cancelScan(self):
        if not self.stopEvent2.is_set():
            self.stopEvent2.set()
            time.sleep(0.01)
            self.var.set("")
            self.message.pack()
        
    def video(self):
        while self.results == "" and not self.stopEvent2.is_set():
            
            self.var.set("Scanning for ID")
            self.message.pack()
            image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            
            self.results = str(self.read.findImage(image))
            self.results = self.results[2:len(self.results)-1]
            #print(self.results)
            if self.results != "":
                self.var.set("ID found!")
                self.message.pack()
                print("[INFO] Scan Successful")
                self.getEntry(self.results)
                self.stopEvent2.set()

        self.results = ""
        #self.vid.end()

'''EDIT THIS TO DETERMINE CAMERA'''
cap = cv2.VideoCapture(0)
if cap.isOpened():
    #print(cap.get(3))
    #print(cap.get(4))
    cap.set(3, 1280)
    cap.set(4, 800)
    #print(cap.get(3))
    #print(cap.get(4))
    ret, image = cap.read()
    g = improvedGUI(cap)
    #g.top.bind('<Enter>', g.on_button())
    g.top.mainloop()
else:
    print("[INFO] camera not working retry")
