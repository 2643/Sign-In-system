# pylint: disable=no-member
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
import numpy
from BarcodeScanner import barcodeVid
from BarcodeScanner import readBarcode
from spreadsheets import spreadsheet

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

        self.firstN = ""
        self.LastN = ""
        self.vid = barcodeVid()
        self.read = readBarcode()
        self.results = ""
        self.s = spreadsheet("test")

        self.top = tki.Tk()
        self.var = tki.StringVar()
        self.label = tki.Label(self.top, text="Enter ID Number")
        self.label2 = tki.Label(self.top, text="Press Scan ID if you have ID")
        self.entry = tki.Entry(self.top)
        self.button = tki.Button(self.top, text="Find ID", command=self.findUser)
        self.button2 = tki.Button(self.top, text="Scan ID", command=self.checkVidT)
        self.button3 = tki.Button(self.top, text="Cancel Scan", command=self.cancelScan)
        self.message = tki.Message(self.top, textvariable = self.var, width = 200)
        self.panel = None

        self.stopEvent= threading.Event()
        self.thread = threading.Thread(target = self.videoLoop, args=())
        self.thread2 = threading.Thread(target = self.updateLoop, args=())
        self.thread3 = None
        self.thread4 = None
        self.thread2.daemon = True
        self.thread2.start()
        self.thread.start()

        self.top.wm_title("Py SignIn System")
        self.top.wm_protocol("WM_DELETE_WINDOW", self.onClose)

 ###################################################################
    
    def videoLoop(self):
        try:
            while not self.stopEvent.is_set():
                if not isinstance(self.vs, numpy.ndarray):
                    ret, self.frame = self.vs.read()
                    self.frame = imutils.resize(self.frame, width = 750)
                    image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(image)
                    image = ImageTk.PhotoImage(image)
                else:
                    image = self.vs
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

###################################################################

    # set the stop event, cleanup the camera, and allow the rest of
    # the quit process to continue
    def onClose(self):
        print("[INFO] closing...")
        self.stopEvent.set()
        if self.stopEvent2 != None:
            self.stopEvent2.set()
        quit()
        sys.exit()
        self.top.quit()
        self.vs.release()
        cv2.destroyAllWindows()

###################################################################

    def pressed(self, test):
        self.on_button()

    def on_button(self):
        print("[INFO] running")
        id = self.entry.get()
        self.getEntry(id)   

    def getEntry(self, id):
        self.firstN, self.LastN, val = self.s.askForPerson(id)
        if self.firstN != -1:
            self.var.set(val + self.firstN.value + " " + self.LastN.value)
            self.entry.delete(0, len(self.entry.get()))
            self.message.pack()
        else:
            self.var.set("Error: No User Found")
            self.message.pack()
    
    def findUser(self):
        print("[INFO] Thread begins: ")
        self.thread4 = threading.Thread(target = self.on_button, args=())
        self.thread4.start()

###################################################################

    def checkVidT(self):
        print("[INFO] Thread begins: ")
        self.stopEvent2 = threading.Event()
        self.thread3 = threading.Thread(target = self.video, args=())
        self.thread3.start()
    
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
    
###################################################################

    #loop to check login status/refresh token
    def updateLoop(self):
        print("[INFO] initializing")
        while True:
            try:
                time.sleep(900)
                print("[INFO] Token Refresh")
                self.s.client.login()
            except Exception as e:
                print("[INFO] Token Cannot Be Refreshed")



'''EDIT THIS TO DETERMINE CAMERA'''
cap = cv2.VideoCapture(2)
if cap.isOpened(): #If there is a webcam
    cap.set(3, 1280)
    cap.set(4, 800)
    ret, image = cap.read()
    g = improvedGUI(cap)
    g.top.mainloop()
else: #else use a default image
    img = cv2.imread("1.jpg", 0)
    g = improvedGUI(img)
    g.top.mainloop()
    print("[INFO] camera not working disabling")
        

