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
    SET_APIKEY_MESSAGE = "Tunnisteavainta ei ole määritetty. Aseta se valikossa File->Aseta tunnisteavain"
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
            self.ui.stationComboBox_2.addItem(s["Name"])

        self.ui.stationComboBox.currentIndexChanged.connect(self._selectPlace)
        self.ui.stationComboBox_2.currentIndexChanged.connect(self._selectPlace)
        self.ui.stationComboBox.setCurrentIndex(self.api.getIndexOfPlace("Hämeenlinna Lammi Pappila"))
        self.ui.stationComboBox_2.setCurrentIndex(self.api.getIndexOfPlace("Hämeenlinna Lammi Pappila"))
        self.ui.pushButton.clicked.connect(self._download_daily)
        self.ui.pushButton_2.clicked.connect(self._download_realtime)

        self.ui.endtime_dateEdit.dateChanged.connect(self._dateEditedDaily)
        self.ui.startimeDateEdit.dateChanged.connect(self._dateEditedDaily)

        self.ui.endtime_dateTimeEdit_2.dateChanged.connect(self._dateEditedRealTime)
        self.ui.startimeDateTimeEdit_2.dateChanged.connect(self._dateEditedRealTime)

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
        msgbox.information(self, "Tietoa", "Yksinkertainen sovellus ilmatieteenlaitoksen säähavaintodatan lataamiseen.\nJos ohjelma lakkaa toimimasta, voit ottaa yhteyttä\n\nTuomas Salmi, 2015\nhttps://github.com/Tumetsu?tab=repositories\nsalmi.tuomas@gmail.com")
        msgbox.show()

    @pyqtSlot()
    def _set_apikey(self):
        key = QInputDialog.getText(self, "Aseta tunnisteavain", "Käyttääksesi sovellusta tarvitset ilmatieteenlaitoksen avoimen datan tunnisteavaimen.\nMene osoitteeseen http://ilmatieteenlaitos.fi/avoin-data saadaksesi lisätietoa avaimen hankkimisesta.\n\n"
                                         "Kun olet rekisteröitynyt ja saanut tekstimuotoisen tunnisteavaimen, kopioi se tähän:", text=self.apiKey)
        if key[1]:
            self.apiKey = key[0]
            self.api.auth(self.apiKey)
            self.settings.setValue("apikey", self.apiKey)





    @pyqtSlot(int)
    def _selectPlace(self,placeIndex):
        self.ui.stationComboBox_2.setCurrentIndex(placeIndex)
        self.ui.stationComboBox.setCurrentIndex(placeIndex)
        self.currentSelectedModel = self.api.getStationsList()[placeIndex]
        self.ui.data_availableLabel.setText(self.currentSelectedModel["Since"])

        self._setDailyFieldLimits(placeIndex)
        self._setRealTimeFieldLimits(placeIndex)




    def _setRealTimeFieldLimits(self, placeIndex):
        #realtime values are available only after 2010.
        minYear = int(self.currentSelectedModel["Since"])
        if  minYear > 2010:
            self.ui.data_availableLabel_2.setText(str(minYear))
        else:
            minYear = 2010
            self.ui.data_availableLabel_2.setText("1.1.2010")

        self.ui.startimeDateTimeEdit_2.clearMinimumDate()
        minDate = QDate(minYear, 1, 1)
        self.ui.startimeDateTimeEdit_2.setMinimumDate(minDate)

        self.ui.startimeDateTimeEdit_2.clearMaximumDate()
        maxDate = QDate(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
        self.ui.startimeDateTimeEdit_2.setMaximumDate(maxDate)

        self.ui.endtime_dateTimeEdit_2.clearMinimumDate()
        minDate = QDate(minYear, 1, 1)
        self.ui.endtime_dateTimeEdit_2.setMinimumDate(minDate)

        self.ui.endtime_dateTimeEdit_2.clearMaximumDate()
        maxDate = QDate(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
        self.ui.endtime_dateTimeEdit_2.setMaximumDate(maxDate)

        newDate = QDate(self.ui.startimeDateTimeEdit_2.date().year(), self.ui.startimeDateTimeEdit_2.date().month(), self.ui.startimeDateTimeEdit_2.date().day() +1)
        self.ui.endtime_dateTimeEdit_2.setDate(newDate)

        if self.ui.startimeDateTimeEdit_2.date() < self.ui.startimeDateTimeEdit_2.minimumDate():
            self.ui.startimeDateTimeEdit_2.setDate(self.ui.startimeDateTimeEdit_2.minimumDate())

    def _setDailyFieldLimits(self, placeIndex):
        #DAILY TAB
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
        filename = QFileDialog.getSaveFileName(self, "Tallenna säädata csv-muodossa:",
                                               path +"/weather_data.csv", "Comma separated values CSV (*.csv);;All files (*)")
        if filename[0] != "":
            self._saveToCsv(dataframe, filename[0])

    def _saveToCsv(self, df, path):
        #save
        print(df)
        df.to_csv(path, sep=";", date_format="%d.%m.%Y %H:%M", index=False)

    def _getDateTimeFromUI(self, dateEdit):
        return QDateTime(dateEdit.date()).toPyDateTime()

    @pyqtSlot()
    def _dateEditedDaily(self):


        if self.ui.startimeDateEdit.date() == self.ui.endtime_dateEdit.date():
            self.ui.startimeDateEdit.setStyleSheet("background-color: #FC9DB7;")
            self.ui.endtime_dateEdit.setStyleSheet("background-color: #FC9DB7;")
            self.statusBar().showMessage("Aloitus ja lopetuspäivämäärät eivät saa olla samoja", 5000)
            self.ui.pushButton.setEnabled(False)
        else:
            self.ui.startimeDateEdit.setStyleSheet("background-color: white;")
            self.ui.endtime_dateEdit.setStyleSheet("background-color: white;")
            self.ui.pushButton.setEnabled(True)

            if self.ui.endtime_dateEdit.date() < self.ui.startimeDateEdit.date():
                self.ui.endtime_dateEdit.setStyleSheet("background-color: #FC9DB7;")
                self.statusBar().showMessage("Lopetus päivämäärä ei saa edeltää aloitus päivämäärää", 5000)
                self.ui.pushButton.setEnabled(False)
            else:
                self.ui.endtime_dateEdit.setStyleSheet("background-color: white;")
                self.statusBar().showMessage("", 50)
                self.ui.pushButton.setEnabled(True)




    @pyqtSlot()
    def _dateEditedRealTime(self):
        #realtimetab
        if self.ui.startimeDateTimeEdit_2.date() == self.ui.endtime_dateTimeEdit_2.date():
            self.ui.startimeDateTimeEdit_2.setStyleSheet("background-color: #FC9DB7;")
            self.ui.endtime_dateTimeEdit_2.setStyleSheet("background-color: #FC9DB7;")
            self.statusBar().showMessage("Aloitus ja lopetuspäivämäärät eivät saa olla samoja", 5000)
            self.ui.pushButton_2.setEnabled(False)
        else:
            self.ui.startimeDateTimeEdit_2.setStyleSheet("background-color: white;")
            self.ui.endtime_dateTimeEdit_2.setStyleSheet("background-color: white;")
            self.ui.pushButton_2.setEnabled(True)

            if self.ui.endtime_dateTimeEdit_2.date() < self.ui.startimeDateTimeEdit_2.date():
                self.ui.endtime_dateTimeEdit_2.setStyleSheet("background-color: #FC9DB7;")
                self.statusBar().showMessage("Lopetus päivämäärä ei saa edeltää aloitus päivämäärää", 5000)
                self.ui.pushButton_2.setEnabled(False)
            else:
                self.ui.endtime_dateTimeEdit_2.setStyleSheet("background-color: white;")
                self.statusBar().showMessage("", 50)
                self.ui.pushButton_2.setEnabled(True)

    @pyqtSlot(int)
    def _download_daily(self):
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
                    self._showErrorAlerts("Määritettyä sääasemaa ei löydetty.\nIlmatieteenlaitoksen palvelussa on häiriö tai "
                                          "mikäli ongelma toistuu muillakin kohteilla, saattaa tämä ohjelma vaatia päivitystä. Katso tiedot yhteydenotosta File->Tietoa valikosta.\n\nVirheen kuvaus:\n" + str(e))
                if e.errorCode == 404:
                    #apikey on luultavastu väärä
                    self._showErrorAlerts("Datapyyntö ei onnistunut.\nOletko asettanut vaadittavan tunnisteavaimen tai onko se virheellinen? Ilmatieteenlaitos vaatii rekisteröitymistä palveluun "
                                          "ennen sen käyttöä. Katso lisätietoa valikosta File->Aseta tunnisteavain.")

                if e.errorCode == "NODATA":
                     #vastauksessa ei ollut dataa. Onko paikasta saatavissa dataa tältä aikaväliltä?
                     self._showErrorAlerts("Määritettyä ajanjaksoa ei löytynyt.\nTodennäköisesti ilmatieteenlaitoksella ei ole dataa tälle ajanjaksolle.\nKokeile "
                                           "pitempää ajanjaksoa, esim. yhtä vuotta tai myöhäisempää aloituspäivämäärää.\n\nVirheen kuvaus:\n" + str(e))
        except Exception as e:
             self._showErrorAlerts("Tuntematon virhe: " + str(e))



    @pyqtSlot(int)
    def _download_realtime(self):
        try:
            try:
                results = self.api.get_realtime_weather({"request" : "getFeature",
                           "storedquery_id" : "fmi::observations::weather::multipointcoverage",
                           "fmisid": self.currentSelectedModel["FMISID"],
                           "starttime" : self._getDateTimeFromUI(self.ui.startimeDateTimeEdit_2),
                           "endtime" : self._getDateTimeFromUI(self.ui.endtime_dateTimeEdit_2)
                })

                parser = FMIxmlParser()
                dataframe = parser.parse(results)
                parser = None
                self._saveData(dataframe)
                dataframe = None
            except (RequestException, NoDataException) as e:
                if e.errorCode == 400:
                    #luultavasti komento jolla pyydetään on väärä tai palvelussa on vika tälle paikkakunnalle
                    self._showErrorAlerts("Määritettyä sääasemaa ei löydetty.\nIlmatieteenlaitoksen palvelussa on häiriö tai "
                                          "mikäli ongelma toistuu muillakin kohteilla, saattaa tämä ohjelma vaatia päivitystä. Katso tiedot yhteydenotosta File->Tietoa valikosta.\n\nVirheen kuvaus:\n" + str(e))
                if e.errorCode == 404:
                    #apikey on luultavasti väärä
                    self._showErrorAlerts("Datapyyntö ei onnistunut.\nOletko asettanut vaadittavan tunnisteavaimen tai onko se virheellinen? Ilmatieteenlaitos vaatii rekisteröitymistä palveluun "
                                          "ennen sen käyttöä. Katso lisätietoa valikosta File->Aseta tunnisteavain.")

                if e.errorCode == "NODATA":
                     #vastauksessa ei ollut dataa. Onko paikasta saatavissa dataa tältä aikaväliltä?
                     self._showErrorAlerts("Määritettyä ajanjaksoa ei löytynyt.\nTodennäköisesti ilmatieteenlaitoksella ei ole dataa tälle ajanjaksolle.\nKokeile "
                                           "pitempää ajanjaksoa, esim. yhtä vuotta tai myöhäisempää aloituspäivämäärää.\n\nVirheen kuvaus:\n" + str(e))
        except Exception as e:
             self._showErrorAlerts("Tuntematon virhe: " + str(e))




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


