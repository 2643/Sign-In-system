import gspread
from oauth2client.service_account import ServiceAccountCredentials
#from jupyter_client.kernelspecapp import raw_input
import time
from datetime import *

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
        #print("[INFO] " + str(col))
 
        addVal = self.asheet.cell(row, 5).value
        returnVal = None

        for c in range(5, col+1):
            #print("[INFO] " + str(c))
            inVal = self.isheet.cell(row, c).value
            outVal = self.osheet.cell(row, c).value

            enterT = datetime.strptime(inVal, '%H:%M:%S').time()
            exitT = datetime.strptime(outVal, '%H:%M:%S').time()
            #print("[INFO] Enter: " + str(enterT) + "     [INFO] Exit: " + str(exitT))
            
            dif = datetime.combine(datetime.today(), exitT) - datetime.combine(datetime.today(), enterT)
            #print("[INFO] " + str(dif))
            if c != 5:
                totalH = totalH + dif
            else:
                totalH = datetime.combine(datetime.today(), totalH) + dif
            returnVal = str(totalH.hour) + ":" + str(totalH.minute) + ":" + str(totalH.second)
        #print("[INFO] " + returnVal)
        self.asheet.update_cell(row, 5, returnVal)
    
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
