import gspread
from oauth2client.service_account import ServiceAccountCredentials
#from jupyter_client.kernelspecapp import raw_input
import time

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
    def __init__(self):
        self.scope = ["https://spreadsheets.google.com/feeds"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name("client_secret.json", self.scope)

        self.client = gspread.authorize(self.creds)
        self.isheet = self.client.open("test").sheet1
        self.osheet = self.client.open("test").get_worksheet(1)
        self.asheet = self.client.open("test").get_worksheet(2)

    
    # ##Finds day of sign in/out
    def findDay(self):
        day = time.localtime()
        date = str(day.tm_mon) + "/" + str(day.tm_mday)
        # print(date)
        findDate = self.isheet.find(date)
        # print(findDate.col)
        return findDate.col

    # ##Gets time when sign in/out
    def getTime(self):
        tt = time.localtime()
        #print(tt)
        if tt.tm_min < 10:
            signInTime = str(tt.tm_hour) + "0" + str(tt.tm_min)
        else:
            signInTime = str(tt.tm_hour) + str(tt.tm_min)
            print(signInTime)
        return signInTime
    
    def addTotalTime(self, row):
        listC = len(self.isheet.row_values(1))
        val = 0
        totalH = 0
        if self.asheet.cell(row, 5).value != "":
            totalH = int(self.asheet.cell(row, 5).value)
        
        for y in range (5, listC):
            if self.isheet.cell(row, y).value != "" and self.osheet.cell(row, y).value != "":
                dif = int(self.osheet.cell(row, y).value) - int(self.isheet.cell(row, y).value)
                totalH = totalH + dif
                self.asheet.update_cell(row, 5, totalH)
            else:
                totalH = 0
                break
        #for x in :
    
    # ##adds time stamp to sign in/out
    def addTimeStamp(self, row, col):
        val = self.isheet.cell(row, col).value
        if val != "":
            self.osheet.update_cell(row, col, self.getTime())
            #self.addTotalTime(row)
            return "Good bye "  
        else:
            self.isheet.update_cell(row, col, self.getTime())
            return "Hello "

    # ##Finds the person and add data        
    def askForPerson(self, idNum):
        #idNum = raw_input("Enter Student id ")
        name = "test"
    
        colInput = self.findDay()
    
        try:
            name = self.isheet.find(idNum)
        except:
            print("Error, ID cannot be found")
            return -1, -1, ""
        state = self.addTimeStamp(name.row, colInput)
        return self.isheet.cell(name.row, 2), self.isheet.cell(name.row, 1), state
        #time.sleep(.5)
        #self.askForPerson()
