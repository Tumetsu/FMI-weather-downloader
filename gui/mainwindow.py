from PyQt5.QtCore import pyqtSlot, pyqtSignal, QDate, QDateTime
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog
from PyQt5.QtCore import pyqtSlot
from gui.ui_mainwindow import Ui_MainWindow
from fmiapi import FMIApi
import datetime
from fmixmlparser import FMIxmlParser

class Mainwindow(QMainWindow):

    api = None
    entrySelectedSignal = pyqtSignal(dict, name="entrySelected")
    currentSelectedModel = None

    def __init__(self, parent=None):
        super(Mainwindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.api = FMIApi()
        self.api.auth("4d7bcd64-01af-4dbb-8a43-404e97b8c2cd")
        self.ui.stationComboBox.clear()
        stations = self.api.getStationsList()
        for s in stations:
            self.ui.stationComboBox.addItem(s["Name"])

        self.ui.stationComboBox.currentIndexChanged.connect(self._selectPlace)
        self.ui.stationComboBox.setCurrentIndex(self.api.getIndexOfPlace("Hämeenlinna Lammi Pappila"))
        self.ui.pushButton.clicked.connect(self._download)


    @pyqtSlot(int)
    def _selectPlace(self,placeIndex):
        self.currentSelectedModel = self.api.getStationsList()[placeIndex]
        self.ui.data_availableLabel.setText(self.currentSelectedModel["Since"])

        self.ui.startimeDateEdit.clearMinimumDate()
        minDate = QDate(int(self.currentSelectedModel["Since"]), 1, 1)
        self.ui.startimeDateEdit.setMinimumDate(minDate)

        self.ui.startimeDateEdit.clearMaximumDate()
        maxDate = QDate(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
        self.ui.startimeDateEdit.setMaximumDate(maxDate)

        self.ui.endtime_dateEdit.clearMinimumDate()
        minDate = QDate(int(self.currentSelectedModel["Since"]), 1, 1)
        self.ui.endtime_dateEdit.setMinimumDate(minDate)

        self.ui.endtime_dateEdit.clearMaximumDate()
        maxDate = QDate(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
        self.ui.endtime_dateEdit.setMaximumDate(maxDate)

        newDate = QDate(self.ui.startimeDateEdit.date().year(), self.ui.startimeDateEdit.date().month(), self.ui.startimeDateEdit.date().day() +1)
        self.ui.endtime_dateEdit.setDate(newDate)


        if self.ui.startimeDateEdit.date() < self.ui.startimeDateEdit.minimumDate():
            self.ui.startimeDateEdit.setDate(self.ui.startimeDateEdit.minimumDate())



    def _saveData(self, dataframe):
        filename = QFileDialog.getSaveFileName(self, "Save weather data as csv",
                                               "", "Comma separated values CSV (*.csv);;All files (*)")
        if filename[0] != "":
            self._saveToCsv(dataframe, filename[0])

    def _saveToCsv(self, df, path):
        #save
        self.df_observations = df.applymap(str).replace(r'\.',',',regex=True)    #decimal dot to comma
        df.to_csv(path, sep=";", date_format="%d.%m.%Y", index=False)

    def _getDateTimeFromUI(self, dateEdit):
        return QDateTime(dateEdit.date()).toPyDateTime()



    @pyqtSlot(int)
    def _download(self):
        results = self.api.get_daily_weather({"request" : "getFeature",
                   "storedquery_id" : "fmi::observations::weather::daily::multipointcoverage",
                   "fmisid": self.currentSelectedModel["FMISID"],
                   "starttime" : self._getDateTimeFromUI(self.ui.startimeDateEdit),
                   "endtime" : self._getDateTimeFromUI(self.ui.endtime_dateEdit)
        })
        parser = FMIxmlParser()
        dataframe = parser.parse(results)
        self._saveData(dataframe)




def start():
    import sys
    app = QApplication(sys.argv)
    downloader = Mainwindow()
    downloader.show()
    sys.exit(app.exec_())

if __name__ == '__main__':

    start()


