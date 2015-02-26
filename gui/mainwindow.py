from PyQt5.QtCore import pyqtSlot, pyqtSignal, QDate, QDateTime, QDir
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QInputDialog, QMessageBox
from PyQt5.QtCore import pyqtSlot, QEvent, QSettings, QStandardPaths

from PyQt5.QtGui import QStatusTipEvent, QDesktopServices
from gui.ui_mainwindow import Ui_MainWindow
from fmiapi import FMIApi
import datetime
from fmixmlparser import FMIxmlParser
import sys
from fmierrors import *


class Mainwindow(QMainWindow):

    api = None
    entrySelectedSignal = pyqtSignal(dict, name="entrySelected")
    currentSelectedModel = None
    apiKey = ""
    SET_APIKEY_MESSAGE = "API-key not provided. Set it on Settings -> Set api-key"
    settings = None

    def __init__(self, parent=None):
        super(Mainwindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.api = FMIApi()
        self.api.auth(self.apiKey)
        self.ui.stationComboBox.clear()
        stations = self.api.getStationsList()
        for s in stations:
            self.ui.stationComboBox.addItem(s["Name"])

        self.ui.stationComboBox.currentIndexChanged.connect(self._selectPlace)
        self.ui.stationComboBox.setCurrentIndex(self.api.getIndexOfPlace("Hämeenlinna Lammi Pappila"))
        self.ui.pushButton.clicked.connect(self._download)

        self.ui.endtime_dateEdit.dateChanged.connect(self._dateEdited)
        self.ui.startimeDateEdit.dateChanged.connect(self._dateEdited)

        #statusbar
        self.statusBar().setStyleSheet("color: red;")

        self.ui.actionSet_api_key.triggered.connect(self._set_apikey)
        self.ui.actionExit.triggered.connect(self._quit)
        self.ui.actionAbout.triggered.connect(self._about)


        self.settings = QSettings("api", "api")
        storedApikey = self.settings.value("apikey")
        if storedApikey is not None:
            self.apiKey = storedApikey
            self.api.auth(self.apiKey)

        if self.apiKey == "":
            self.statusBar().showMessage(self.SET_APIKEY_MESSAGE, 0)

    @pyqtSlot()
    def _quit(self):
        QApplication.quit()

    @pyqtSlot()
    def _about(self):
        msgbox = QMessageBox()
        msgbox.information(self, "About", "A quick weather data download client.\nIf it stops working check updates in following url or contact me.\n\nTuomas Salmi, 2015\nhttps://github.com/Tumetsu?tab=repositories\nsalmi.tuomas@gmail.com")
        msgbox.show()

    @pyqtSlot()
    def _set_apikey(self):
        key = QInputDialog.getText(self, "Set API-key", "To use FMI weather service, you need to register and receive the API-key.\nGo to http://ilmatieteenlaitos.fi/avoin-data for more instructions.\n"
                                         "When you have the key, copy it below:", text=self.apiKey)
        if key[1]:
            self.apiKey = key[0]
            self.api.auth(self.apiKey)
            self.settings.setValue("apikey", self.apiKey)



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
        paths = QStandardPaths.standardLocations(0)
        if len(paths) > 0:
            path = paths[0]
        else:
            path = ""
        filename = QFileDialog.getSaveFileName(self, "Save weather data as csv",
                                               path +"/weather_data.csv", "Comma separated values CSV (*.csv);;All files (*)")
        if filename[0] != "":
            self._saveToCsv(dataframe, filename[0])

    def _saveToCsv(self, df, path):
        #save
        print(df)
        df.to_csv(path, sep=";", date_format="%d.%m.%Y", index=False)

    def _getDateTimeFromUI(self, dateEdit):
        return QDateTime(dateEdit.date()).toPyDateTime()

    @pyqtSlot()
    def _dateEdited(self):

        if self.ui.endtime_dateEdit.date() <= self.ui.startimeDateEdit.date():
            self.ui.endtime_dateEdit.setStyleSheet("background-color: red;")
            self.ui.pushButton.setEnabled(False)
        else:
            self.ui.endtime_dateEdit.setStyleSheet("background-color: white;")
            self.ui.pushButton.setEnabled(True)

        if self.ui.startimeDateEdit.date() >= self.ui.endtime_dateEdit.date():
            self.ui.startimeDateEdit.setStyleSheet("background-color: red;")
            self.ui.pushButton.setEnabled(False)
        else:
            self.ui.startimeDateEdit.setStyleSheet("background-color: white;")
            self.ui.pushButton.setEnabled(True)



    @pyqtSlot(int)
    def _download(self):
        try:
            try:
                results = self.api.get_daily_weather({"request" : "getFeature",
                           "storedquery_id" : "fmi::observations::weather::daily::multipointcoverage",
                           "fmisid": self.currentSelectedModel["FMISID"],
                           "starttime" : self._getDateTimeFromUI(self.ui.startimeDateEdit),
                           "endtime" : self._getDateTimeFromUI(self.ui.endtime_dateEdit)
                })

                parser = FMIxmlParser()
                dataframe = parser.parse(results)
                parser = None
                self._saveData(dataframe)
                dataframe = None
            except (RequestException, NoDataException) as e:
                if e.errorCode == 400:
                    #luultavasti komento jolla pyydetään on väärä tai palvelussa on vika tälle paikkakunnalle
                    self._showErrorAlerts("Couldn't find the specified station from FMI-service.\nEither there is a problem "
                                          "on FMI's service, or if this error-message is shown on every station this program likely needs "
                                          "update. Check File->About for contact information.")
                if e.errorCode == 404:
                    #apikey on luultavastu väärä
                    self._showErrorAlerts("Couldn't complete request.\nHave you set your API-key? FMI requires registering on their page before "
                                          "this program can be used. Check more information on File->Set api-key menu.")

                if e.errorCode == "NODATA":
                    #vastauksessa ei ollut dataa. Onko paikasta saatavissa dataa tältä aikaväliltä?
                     self._showErrorAlerts("Couldn't find data on specified time interval.\nMost likely FMI doesn't have data on this timespan.\nTry longer "
                                           "timespan, for example one year to see if you can find data.")
        except Exception as e:
             self._showErrorAlerts("Unknown error: " + str(e))




    def _showErrorAlerts(self, message):
        msgbox = QMessageBox()
        msgbox.information(self, "ERROR", message)
        msgbox.show()


def start():
    import sys
    app = QApplication(sys.argv)
    downloader = Mainwindow()
    downloader.show()
    sys.exit(app.exec_())

if __name__ == '__main__':

    start()


