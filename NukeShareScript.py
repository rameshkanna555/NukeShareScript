'''
SCRIPT AUTHOR : RAMESHKANNA

'''
import sys

sys.path.append('F:/PYTHON/Python calculator/venv/Lib/site-packages')


from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import nuke
import getpass,datetime,os
import pymongo
from mainUI import Ui_MainWindow


#####   Connecting Mongodb server    #######

SERVER = pymongo.MongoClient('localhost',27017)
DB = SERVER['NukeShare']
COLLECTION = DB['NukeData']

now = datetime.datetime.now()

username = getpass.getuser()



class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.receivedScriptList()
        self.sentRecent()
        self.show()

        self.ShareButton.clicked.connect(self.insertData)

        artistNames = ['kanna','Bunny','kiran','Bujji','DELL']
        self.completer = QCompleter(artistNames)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.SenderName.addItems(artistNames)
        self.SenderName.setEditable(True)
        self.SenderName.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.SenderName.setInsertPolicy(QComboBox.NoInsert)
        self.SenderName.setCompleter(self.completer)

        self.ReceivedList.setHorizontalHeaderLabels(['Script-Name', 'Sender', 'Time   '])
        self.ReceivedList.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ReceivedList.hideColumn(3)
        self.ReceivedList.hideColumn(4)
        self.ReceivedList.itemClicked.connect(self.clickedReceivedList)


        self.SentList.setHorizontalHeaderLabels(['Script-Name', 'Sent-To', 'Time   '])
        self.SentList.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.SentList.hideColumn(3)
        self.SentList.hideColumn(4)
        self.SentList.itemClicked.connect(self.clickedSentList)




        self.ReceivedNameEdit.setText(username)

        self.SentNameEdit.setText(username)

        self.Pastebutton.clicked.connect(self.pasteScript)

        self.Refreshbutton.clicked.connect(self.refreshApp)


    def clickedReceivedList(self):
        self.SentList.clearSelection()
        self.RL = True


    def clickedSentList(self):
        self.ReceivedList.clearSelection()
        self.RL = False


    def insertData(self):

        NukeScriptName = nuke.root().knob('name').value()
        ScriptName = os.path.basename(NukeScriptName)
        if NukeScriptName == "":
            ScriptName = 'From - '+username
        else :
            pass
        self.Sending_To = self.SenderName.currentText()
        nuke.nodeCopy("%clipboard%")
        script = QApplication.clipboard().text()
        NukeData = {'ScriptName':ScriptName, 'Send_To': self.Sending_To,'SenderName':username,'date':now,'script':script}
        COLLECTION.insert_one(NukeData)



    def receivedScriptList(self):

        nukedata = COLLECTION.find({'Send_To':username}).sort('date',-1)
        self.ReceivedList.setRowCount(nukedata.count())
        self.ReceivedList.setColumnCount(5)

        for x,i in enumerate(nukedata):

            ScriptName = i['ScriptName']
            SenderName = i['SenderName']
            time = self.time_difference(i['date'])
            NukeScript = i['script']
            Received = 'Received'


            self.ReceivedList.setItem(x,0,QTableWidgetItem(ScriptName))
            self.ReceivedList.setItem(x,1,QTableWidgetItem(SenderName))
            self.ReceivedList.setItem(x,2,QTableWidgetItem(time))
            self.ReceivedList.setItem(x, 3, QTableWidgetItem(NukeScript))
            self.ReceivedList.setItem(x, 4, QTableWidgetItem(Received))



    def sentRecent(self):

        nukedata = COLLECTION.find({'SenderName':username}).sort('date',-1)
        self.SentList.setRowCount(nukedata.count())
        self.SentList.setColumnCount(5)

        for x,i in enumerate(nukedata):

            ScriptName = i['ScriptName']
            Send_To = 'Sent-'+i['Send_To']
            time = self.time_difference(i['date'])
            NukeScript = i['script']
            Sent = "Sent"


            self.SentList.setItem(x,0,QTableWidgetItem(ScriptName))
            self.SentList.setItem(x,1,QTableWidgetItem(Send_To))
            self.SentList.setItem(x,2,QTableWidgetItem(time))
            self.SentList.setItem(x, 3, QTableWidgetItem(NukeScript))
            self.SentList.setItem(x, 4, QTableWidgetItem(Sent))


    def pasteScript(self):

        if self.RL == True:
            row = self.ReceivedList.currentRow()
            item = self.ReceivedList.item(row,3).text()

        else:
            row = self.SentList.currentRow()
            item = self.SentList.item(row,3).text()


        QApplication.clipboard().setText(item)
        nuke.nodePaste('%clipboard%')


    def time_difference(self, date):

        delta = datetime.datetime.today() - date
        if delta.days:
            return "%s day(s)" % delta.days
        seconds = delta.seconds
        if seconds < 60:
            return "A few seconds ago"
        elif seconds < 3600:
            return "%s minute(s) ago" % int(seconds/60)
        elif seconds < 86400:
            return "%s hours(s) ago" % int(seconds/3600)


    def refreshApp(self):

        self.receivedScriptList()
        self.sentRecent()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())