'''
Created on Dec 30, 2017
Depreciated all code moved to main.py
'''
import tkinter as tk
from spreadsheets import spreadsheet
from BarcodeScanner import barcodeVid
from BarcodeScanner import readBarcode
import cv2

class gui(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.var = tk.StringVar()
        self.label = tk.Label(self, text="Enter ID")
        self.entry = tk.Entry(self)
        self.button = tk.Button(self, text="Get", command=self.on_button)
        self.button2 = tk.Button(self, text="Video", command=self.video)
        self.message = tk.Message(self, textvariable = self.var)
        self.label.pack()
        self.entry.pack()
        self.button.pack()
        self.button2.pack()
        self.message.pack()
        self.firstN = ""
        self.LastN = ""
        self.vid = barcodeVid()
        self.read = readBarcode()
        self.results =""
        self.s = spreadsheet()
    
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
        id = self.entry.get()
        self.getEntry(id)

    def video(self):
        while self.results == "":
            image = self.vid.cycle()
            self.results = str(self.read.findImage(image))
            self.results = self.results[2:len(self.results)-1]
            if self.results != "":
                print(self.results)
                self.getEntry(self.results)
            elif cv2.waitKey(10) & 0xFF == ord('q'):
                self.vid.end()
                break
        self.results = ""
        self.vid.end()
       
app = gui()
app.mainloop()
