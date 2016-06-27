import datetime
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QDate, QDateTime, QTranslator, QStandardPaths, QCoreApplication, QEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QInputDialog, QMessageBox, QCompleter
from gui.ui_mainwindow import Ui_MainWindow
from PyQt5.QtGui import QIcon
from fmiapi.fmiapi import FMIApi
from gui.download.downloadProgress import *
from gui.settings import Settings
import gui.menubar_actions as menubar_actions
from gui.messages import Messages
import csv


class Mainwindow(QMainWindow):

    # signals
    setLanguageSignal = pyqtSignal(str, name="setLanguage")
    entrySelectedSignal = pyqtSignal(dict, name="entrySelected")

    def __init__(self, app, translators, parent=None):
        super(Mainwindow, self).__init__(parent)
        self.api = None
        self._language = menubar_actions.LANGUAGE_IDS["English"]
        self._current_selected_model = None
        self.api = FMIApi()
        self._settings = Settings()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._set_up_ui()
        self._app = app
        self._translators = translators

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
        self.ui.stationComboBox.clear()
        stations = self.api.get_stations()
        completer_strings = []
        for s in stations:
            self.ui.stationComboBox.addItem(s["Name"])
            self.ui.stationComboBox_2.addItem(s["Name"])
            completer_strings.append(s["Name"])
        self.comboboxCompleter = QCompleter(completer_strings, self)
        self.comboboxCompleter.setCompletionMode(0)
        self.ui.stationComboBox.setCompleter(self.comboboxCompleter)
        self.ui.stationComboBox_2.setCompleter(self.comboboxCompleter)

        self.ui.stationComboBox.currentIndexChanged.connect(self._select_place_from_combobox)
        self.ui.stationComboBox_2.currentIndexChanged.connect(self._select_place_from_combobox)
        self.ui.stationComboBox.setCurrentIndex(self.api.get_index_of_station("Hämeenlinna Lammi Pappila"))
        self.ui.stationComboBox_2.setCurrentIndex(self.api.get_index_of_station("Hämeenlinna Lammi Pappila"))

    def _set_up_ui(self):
        self._set_up_station_comboboxes()

        # wire download buttons to actions
        self.ui.pushButton.clicked.connect(self._download_daily)
        self.ui.pushButton_2.clicked.connect(self._download_realtime)

        # wire date fields to their actions
        self.ui.endtime_dateEdit.dateChanged.connect(self._daily_date_edited)
        self.ui.startimeDateEdit.dateChanged.connect(self._daily_date_edited)
        self.ui.endtime_dateTimeEdit_2.dateChanged.connect(self._realtime_date_edited)
        self.ui.startimeDateTimeEdit_2.dateChanged.connect(self._realtime_date_edited)

        # statusbar
        self.statusBar().setStyleSheet("color: red;")

        # menubar actions
        self.ui.actionSet_api_key.triggered.connect(lambda: menubar_actions.set_apikey(self, self._settings))
        self.ui.actionExit.triggered.connect(menubar_actions.quit)
        self.ui.actionAbout.triggered.connect(menubar_actions.about)
        self.ui.actionAseta_kieli.triggered.connect(lambda: menubar_actions.select_language(self, self._settings))
        self.ui.actionOhjeet.triggered.connect(menubar_actions.open_manual)

        # language change signal
        self.setLanguageSignal.connect(lambda: menubar_actions.select_language(self, self._settings))

    @pyqtSlot(int, name='selectPlace')
    def _select_place_from_combobox(self, place_index):
        self.ui.stationComboBox_2.setCurrentIndex(place_index)
        self.ui.stationComboBox.setCurrentIndex(place_index)
        self._current_selected_model = self.api.get_stations()[place_index]
        self.ui.data_availableLabel.setText(self._current_selected_model["Since"])

        self._set_daily_field_limits(place_index)
        self._set_realtime_field_limits(place_index)

    def _set_realtime_field_limits(self, place_index):
        # realtime values are available only after 2010.
        min_year = int(self._current_selected_model["Since"])
        if min_year > 2010:
            self.ui.data_availableLabel_2.setText(str(min_year))
        else:
            min_year = 2010
            self.ui.data_availableLabel_2.setText("1.1.2010")

        self.ui.startimeDateTimeEdit_2.clearMinimumDate()
        min_date = QDate(min_year, 1, 1)
        self.ui.startimeDateTimeEdit_2.setMinimumDate(min_date)

        self.ui.startimeDateTimeEdit_2.clearMaximumDate()
        max_date = QDate(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
        self.ui.startimeDateTimeEdit_2.setMaximumDate(max_date)

        self.ui.endtime_dateTimeEdit_2.clearMinimumDate()
        min_date = QDate(min_year, 1, 1)
        self.ui.endtime_dateTimeEdit_2.setMinimumDate(min_date)

        self.ui.endtime_dateTimeEdit_2.clearMaximumDate()
        max_date = QDate(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
        self.ui.endtime_dateTimeEdit_2.setMaximumDate(max_date)

        new_date = QDate(self.ui.startimeDateTimeEdit_2.date().year(), self.ui.startimeDateTimeEdit_2.date().month(), self.ui.startimeDateTimeEdit_2.date().day() + 1)
        self.ui.endtime_dateTimeEdit_2.setDate(new_date)

        if self.ui.startimeDateTimeEdit_2.date() < self.ui.startimeDateTimeEdit_2.minimumDate():
            self.ui.startimeDateTimeEdit_2.setDate(self.ui.startimeDateTimeEdit_2.minimumDate())

    def _set_daily_field_limits(self, place_index):
        self.ui.startimeDateEdit.clearMinimumDate()
        min_date = QDate(int(self._current_selected_model["Since"]), 1, 1)
        self.ui.startimeDateEdit.setMinimumDate(min_date)

        self.ui.startimeDateEdit.clearMaximumDate()
        max_date = QDate(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
        self.ui.startimeDateEdit.setMaximumDate(max_date)

        self.ui.endtime_dateEdit.clearMinimumDate()
        min_date = QDate(int(self._current_selected_model["Since"]), 1, 1)
        self.ui.endtime_dateEdit.setMinimumDate(min_date)

        self.ui.endtime_dateEdit.clearMaximumDate()
        max_date = QDate(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
        self.ui.endtime_dateEdit.setMaximumDate(max_date)

        new_date = QDate(self.ui.startimeDateEdit.date().year(), self.ui.startimeDateEdit.date().month(), self.ui.startimeDateEdit.date().day() +1)
        self.ui.endtime_dateEdit.setDate(new_date)

        if self.ui.startimeDateEdit.date() < self.ui.startimeDateEdit.minimumDate():
            self.ui.startimeDateEdit.setDate(self.ui.startimeDateEdit.minimumDate())

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

    def _save_to_csv(self, df, path):
        with open(path, 'w', newline='\n') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(df.keys())
            writer.writerows(zip(*df.values()))
            outfile.close()

    def _get_dateTime_from_UI(self, dateEdit, onlyDate=True):
        if onlyDate:
            return QDateTime(dateEdit.date()).toPyDateTime()
        else:
            return QDateTime(dateEdit.dateTime()).toPyDateTime()


    @pyqtSlot()
    def _daily_date_edited(self):
        if self.ui.startimeDateEdit.date() == self.ui.endtime_dateEdit.date():
            self.ui.startimeDateEdit.setStyleSheet("background-color: #FC9DB7;")
            self.ui.endtime_dateEdit.setStyleSheet("background-color: #FC9DB7;")
            self.statusBar().showMessage(Messages.start_end_date_warning(), 5000)
            self.ui.pushButton.setEnabled(False)
        else:
            self.ui.startimeDateEdit.setStyleSheet("background-color: white;")
            self.ui.endtime_dateEdit.setStyleSheet("background-color: white;")
            self.ui.pushButton.setEnabled(True)

            if self.ui.endtime_dateEdit.date() < self.ui.startimeDateEdit.date():
                self.ui.endtime_dateEdit.setStyleSheet("background-color: #FC9DB7;")
                self.statusBar().showMessage(Messages.end_date_warning(), 5000)
                self.ui.pushButton.setEnabled(False)
            else:
                self.ui.endtime_dateEdit.setStyleSheet("background-color: white;")
                self.statusBar().showMessage("", 50)
                self.ui.pushButton.setEnabled(True)

    @pyqtSlot(name='editRealtimeDate')
    def _realtime_date_edited(self):
        #realtimetab
        if self.ui.startimeDateTimeEdit_2.date() == self.ui.endtime_dateTimeEdit_2.date():
            self.ui.startimeDateTimeEdit_2.setStyleSheet("background-color: #FC9DB7;")
            self.ui.endtime_dateTimeEdit_2.setStyleSheet("background-color: #FC9DB7;")
            self.statusBar().showMessage(Messages.start_end_date_warning(), 5000)
            self.ui.pushButton_2.setEnabled(False)
        else:
            self.ui.startimeDateTimeEdit_2.setStyleSheet("background-color: white;")
            self.ui.endtime_dateTimeEdit_2.setStyleSheet("background-color: white;")
            self.ui.pushButton_2.setEnabled(True)

            if self.ui.endtime_dateTimeEdit_2.date() < self.ui.startimeDateTimeEdit_2.date():
                self.ui.endtime_dateTimeEdit_2.setStyleSheet("background-color: #FC9DB7;")
                self.statusBar().showMessage(Messages.end_date_warning(), 5000)
                self.ui.pushButton_2.setEnabled(False)
            else:
                self.ui.endtime_dateTimeEdit_2.setStyleSheet("background-color: white;")
                self.statusBar().showMessage("", 50)
                self.ui.pushButton_2.setEnabled(True)

    def _download_daily(self):
        """ Download daily weather data from FMI api """
        params = {"request": "getFeature",
                   "storedquery_id": "fmi::observations::weather::daily::multipointcoverage",
                   "fmisid": self._current_selected_model["FMISID"],
                   "starttime": self._get_dateTime_from_UI(self.ui.startimeDateEdit),
                   "endtime": self._get_dateTime_from_UI(self.ui.endtime_dateEdit)
                  }

        download = DownloadProgress(self)
        download.finishedSignal.connect(self._choose_place_to_save_data)
        download.begin_download(params, self.api.get_daily_weather)

    def _download_realtime(self):
        """ Download real time weather data from FMI api """
        params = {"request": "getFeature",
                  "storedquery_id": "fmi::observations::weather::multipointcoverage",
                  "fmisid": self._current_selected_model["FMISID"],
                  "starttime": self._get_dateTime_from_UI(self.ui.startimeDateTimeEdit_2, onlyDate=False),
                  "endtime": self._get_dateTime_from_UI(self.ui.endtime_dateTimeEdit_2, onlyDate=False),
                  }

        download = DownloadProgress(self)
        download.finishedSignal.connect(self._choose_place_to_save_data)
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
