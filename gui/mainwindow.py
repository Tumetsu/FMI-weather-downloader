import datetime
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QDate, QDateTime, QTranslator, QStandardPaths, QCoreApplication, QEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QInputDialog, QMessageBox, QCompleter
from gui.ui_mainwindow import Ui_MainWindow
from PyQt5.QtGui import QIcon
from fmiapi.fmiapi import FMIApi
from gui.services.downloadProgress import *
from gui.services.settings import Settings
import gui.menubar_actions as menubar_actions
from gui.messages import Messages
from gui.services.checkupdates import CheckUpdatesOnStartup
import csv
from gui.services.csvwriter import CsvExport


class Mainwindow(QMainWindow):

    # signals
    setLanguageSignal = pyqtSignal(name="setLanguage")
    entrySelectedSignal = pyqtSignal(dict, name="entrySelected")

    def __init__(self, app, translators, parent=None):
        super(Mainwindow, self).__init__(parent)
        self.api = None
        self._language = menubar_actions.LANGUAGE_IDS["English"]
        self._current_selected_model = None
        self.api = FMIApi()
        self._settings = Settings()
        self._csvexport = CsvExport(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._set_up_ui()
        self._app = app
        self._translators = translators
        self.update_checker = CheckUpdatesOnStartup(self._settings)

        app_icon = QIcon()
        app_icon.addFile('icon.ico')
        app.setWindowIcon(app_icon)

    def show(self):
        """ Override so that we can show possible settings dialogs right after startup """
        super(Mainwindow, self).show()
        self._settings.load_qsettings(self)

    def set_language(self, language):
        """ Set the language of the UI """
        self._language = language
        self._app.installTranslator(self._translators[language])

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.ui.retranslateUi(self)
        super(Mainwindow, self).changeEvent(event)

    def _set_up_station_comboboxes(self):
        """ Set station names for combobox in both tabs. Configure completion."""
        self.ui.stationComboBox_daily.clear()
        stations = self.api.get_stations()
        completer_strings = []
        for s in stations:
            self.ui.stationComboBox_daily.addItem(s["Name"])
            self.ui.stationComboBox_realtime.addItem(s["Name"])
            completer_strings.append(s["Name"])
        self.comboboxCompleter = QCompleter(completer_strings, self)
        self.comboboxCompleter.setCompletionMode(0)
        self.ui.stationComboBox_daily.setCompleter(self.comboboxCompleter)
        self.ui.stationComboBox_realtime.setCompleter(self.comboboxCompleter)

        self.ui.stationComboBox_daily.currentIndexChanged.connect(self._select_place_from_combobox)
        self.ui.stationComboBox_realtime.currentIndexChanged.connect(self._select_place_from_combobox)
        self.ui.stationComboBox_daily.setCurrentIndex(self.api.get_index_of_station("Hämeenlinna Lammi Pappila"))
        self.ui.stationComboBox_realtime.setCurrentIndex(self.api.get_index_of_station("Hämeenlinna Lammi Pappila"))

    def _set_up_ui(self):
        self._set_up_station_comboboxes()

        # wire download buttons to actions
        self.ui.downloadButton_daily.clicked.connect(self._download_daily)
        self.ui.downloadButton_realtime.clicked.connect(self._download_realtime)

        # wire date fields to their actions
        self.ui.endDatetimeEdit_daily.dateChanged.connect(self._daily_date_edited)
        self.ui.startDatetimeEdit_daily.dateChanged.connect(self._daily_date_edited)
        self.ui.endDatetimeEdit_realtime.dateChanged.connect(self._realtime_date_edited)
        self.ui.startDatetimeEdit_realtime.dateChanged.connect(self._realtime_date_edited)

        # statusbar
        self.statusBar().setStyleSheet("color: red;")

        # menubar actions
        self.ui.actionSet_api_key.triggered.connect(lambda: menubar_actions.set_apikey(self, self._settings))
        self.ui.actionExit.triggered.connect(menubar_actions.quit)
        self.ui.actionAbout.triggered.connect(menubar_actions.about)
        self.ui.actionSet_language.triggered.connect(lambda: menubar_actions.select_language(self, self._settings))
        self.ui.actionView_instructions.triggered.connect(menubar_actions.open_manual)
        self.ui.actionCheck_updates.triggered.connect(lambda: menubar_actions.check_updates(self._settings))

        # language change signal
        self.setLanguageSignal.connect(lambda: menubar_actions.select_language(self, self._settings))

    @pyqtSlot(int, name='selectPlace')
    def _select_place_from_combobox(self, place_index):
        self.ui.stationComboBox_realtime.setCurrentIndex(place_index)
        self.ui.stationComboBox_daily.setCurrentIndex(place_index)
        self._current_selected_model = self.api.get_stations()[place_index]
        self.ui.availableDataFromContent_daily.setText(self._current_selected_model["Since"])

        self._set_daily_field_limits(place_index)
        self._set_realtime_field_limits(place_index)

    def _set_realtime_field_limits(self, place_index):
        # realtime values are available only after 2010.
        min_year = int(self._current_selected_model["Since"])
        if min_year > 2010:
            self.ui.availableFromContent_realtime.setText(str(min_year))
        else:
            min_year = 2010
            self.ui.availableFromContent_realtime.setText("1.1.2010")

        self.ui.startDatetimeEdit_realtime.clearMinimumDate()
        min_date = QDate(min_year, 1, 1)
        self.ui.startDatetimeEdit_realtime.setMinimumDate(min_date)

        self.ui.startDatetimeEdit_realtime.clearMaximumDate()
        max_date = QDate(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
        self.ui.startDatetimeEdit_realtime.setMaximumDate(max_date)

        self.ui.endDatetimeEdit_realtime.clearMinimumDate()
        min_date = QDate(min_year, 1, 1)
        self.ui.endDatetimeEdit_realtime.setMinimumDate(min_date)

        self.ui.endDatetimeEdit_realtime.clearMaximumDate()
        max_date = QDate(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
        self.ui.endDatetimeEdit_realtime.setMaximumDate(max_date)

        new_date = QDate(self.ui.startDatetimeEdit_realtime.date().year(), self.ui.startDatetimeEdit_realtime.date().month(), self.ui.startDatetimeEdit_realtime.date().day() + 1)
        self.ui.endDatetimeEdit_realtime.setDate(new_date)

        if self.ui.startDatetimeEdit_realtime.date() < self.ui.startDatetimeEdit_realtime.minimumDate():
            self.ui.startDatetimeEdit_realtime.setDate(self.ui.startDatetimeEdit_realtime.minimumDate())

    def _set_daily_field_limits(self, place_index):
        self.ui.startDatetimeEdit_daily.clearMinimumDate()
        min_date = QDate(int(self._current_selected_model["Since"]), 1, 1)
        self.ui.startDatetimeEdit_daily.setMinimumDate(min_date)

        self.ui.startDatetimeEdit_daily.clearMaximumDate()
        max_date = QDate(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
        self.ui.startDatetimeEdit_daily.setMaximumDate(max_date)

        self.ui.endDatetimeEdit_daily.clearMinimumDate()
        min_date = QDate(int(self._current_selected_model["Since"]), 1, 1)
        self.ui.endDatetimeEdit_daily.setMinimumDate(min_date)

        self.ui.endDatetimeEdit_daily.clearMaximumDate()
        max_date = QDate(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
        self.ui.endDatetimeEdit_daily.setMaximumDate(max_date)

        new_date = QDate(self.ui.startDatetimeEdit_daily.date().year(), self.ui.startDatetimeEdit_daily.date().month(), self.ui.startDatetimeEdit_daily.date().day() +1)
        self.ui.endDatetimeEdit_daily.setDate(new_date)

        if self.ui.startDatetimeEdit_daily.date() < self.ui.startDatetimeEdit_daily.minimumDate():
            self.ui.startDatetimeEdit_daily.setDate(self.ui.startDatetimeEdit_daily.minimumDate())

    def _choose_place_to_save_data(self, dataframe):
        paths = QStandardPaths.standardLocations(0)
        if len(paths) > 0:
            path = paths[0]
        else:
            path = ""
        filename = QFileDialog.getSaveFileName(self, Messages.save_weatherdata_csv(),
                                               path + "/weather_data.csv", "Comma separated values CSV (*.csv);;All files (*)")
        if filename[0] != "":
            self._save_to_csv(dataframe, filename[0])

    def _get_dateTime_from_UI(self, dateEdit, onlyDate=True):
        if onlyDate:
            return QDateTime(dateEdit.date()).toPyDateTime()
        else:
            return QDateTime(dateEdit.dateTime()).toPyDateTime()

    @pyqtSlot()
    def _daily_date_edited(self):
        if self.ui.startDatetimeEdit_daily.date() == self.ui.endDatetimeEdit_daily.date():
            self.ui.startDatetimeEdit_daily.setStyleSheet("background-color: #FC9DB7;")
            self.ui.endDatetimeEdit_daily.setStyleSheet("background-color: #FC9DB7;")
            self.statusBar().showMessage(Messages.start_end_date_warning(), 5000)
            self.ui.downloadButton_daily.setEnabled(False)
        else:
            self.ui.startDatetimeEdit_daily.setStyleSheet("background-color: white;")
            self.ui.endDatetimeEdit_daily.setStyleSheet("background-color: white;")
            self.ui.downloadButton_daily.setEnabled(True)

            if self.ui.endDatetimeEdit_daily.date() < self.ui.startDatetimeEdit_daily.date():
                self.ui.endDatetimeEdit_daily.setStyleSheet("background-color: #FC9DB7;")
                self.statusBar().showMessage(Messages.end_date_warning(), 5000)
                self.ui.downloadButton_daily.setEnabled(False)
            else:
                self.ui.endDatetimeEdit_daily.setStyleSheet("background-color: white;")
                self.statusBar().showMessage("", 50)
                self.ui.downloadButton_daily.setEnabled(True)

    @pyqtSlot(name='editRealtimeDate')
    def _realtime_date_edited(self):
        #realtimetab
        if self.ui.startDatetimeEdit_realtime.date() == self.ui.endDatetimeEdit_realtime.date():
            self.ui.startDatetimeEdit_realtime.setStyleSheet("background-color: #FC9DB7;")
            self.ui.endDatetimeEdit_realtime.setStyleSheet("background-color: #FC9DB7;")
            self.statusBar().showMessage(Messages.start_end_date_warning(), 5000)
            self.ui.downloadButton_realtime.setEnabled(False)
        else:
            self.ui.startDatetimeEdit_realtime.setStyleSheet("background-color: white;")
            self.ui.endDatetimeEdit_realtime.setStyleSheet("background-color: white;")
            self.ui.downloadButton_realtime.setEnabled(True)

            if self.ui.endDatetimeEdit_realtime.date() < self.ui.startDatetimeEdit_realtime.date():
                self.ui.endDatetimeEdit_realtime.setStyleSheet("background-color: #FC9DB7;")
                self.statusBar().showMessage(Messages.end_date_warning(), 5000)
                self.ui.downloadButton_realtime.setEnabled(False)
            else:
                self.ui.endDatetimeEdit_realtime.setStyleSheet("background-color: white;")
                self.statusBar().showMessage("", 50)
                self.ui.downloadButton_realtime.setEnabled(True)

    def _download_daily(self):
        """ Download daily weather data from FMI api """
        params = {"request": "getFeature",
                   "storedquery_id": "fmi::observations::weather::daily::multipointcoverage",
                   "fmisid": self._current_selected_model["FMISID"],
                   "starttime": self._get_dateTime_from_UI(self.ui.startDatetimeEdit_daily),
                   "endtime": self._get_dateTime_from_UI(self.ui.endDatetimeEdit_daily)
                  }

        download = DownloadProgress(self)
        download.finishedSignal.connect(self._csvexport.save_data_to_csv)
        download.begin_download(params, self.api.get_daily_weather)

    def _download_realtime(self):
        """ Download real time weather data from FMI api """
        params = {"request": "getFeature",
                  "storedquery_id": "fmi::observations::weather::multipointcoverage",
                  "fmisid": self._current_selected_model["FMISID"],
                  "starttime": self._get_dateTime_from_UI(self.ui.startDatetimeEdit_realtime, onlyDate=False),
                  "endtime": self._get_dateTime_from_UI(self.ui.endDatetimeEdit_realtime, onlyDate=False),
                  }

        download = DownloadProgress(self)
        download.finishedSignal.connect(self._csvexport.save_data_to_csv)
        download.begin_download(params, self.api.get_realtime_weather)

    def show_error_alerts(self, message):
        msgbox = QMessageBox()
        msgbox.information(self, "ERROR", message)
        msgbox.show()


def start():
    import sys

    # translators have to be created before anything else. List of them are then passed to
    # the Mainwindow
    translator_en = QTranslator()
    translator_en.load("translations/mainwindow_en.qm")
    translator_fi = QTranslator()
    translator_fi.load("translations/mainwindow_fi.qm")

    app = QApplication(sys.argv)

    downloader = Mainwindow(app, {"en": translator_en, "fi": translator_fi})
    downloader.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    start()
