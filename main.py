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
cap = cv2.VideoCapture(1)
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
        

