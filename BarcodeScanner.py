'''
Created on Dec 30, 2017

@author: adleywong
'''
import cv2
import numpy as np
import zbar

#ap = argparse.ArgumentParser()
#ap.add_argument("-i", "--image", required = True, help = "path to the image file")
#args = vars(ap.parse_args())
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
