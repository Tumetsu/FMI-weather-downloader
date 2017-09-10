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
from gui.services.csvwriter import CsvExport
from gui.services.backgroundtask import BackgroundTask


class Mainwindow(QMainWindow):
    # signals
    setLanguageSignal = pyqtSignal(name="setLanguage")
    entrySelectedSignal = pyqtSignal(dict, name="entrySelected")

    def __init__(self, app, translators, parent=None):
        super(Mainwindow, self).__init__(parent)
        self._language = menubar_actions.LANGUAGE_IDS["English"]
        self._current_selected_model = None
        self._current_available_datasets = None
        self._current_selected_dataset = None
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
        if self._current_available_datasets is not None:
            self._set_available_datasets_from_catalogue(self._current_available_datasets)

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.ui.retranslateUi(self)
        super(Mainwindow, self).changeEvent(event)

    def _set_up_station_comboboxes(self):
        """ Set station names for combobox. Configure completion."""
        self.ui.stationComboBox.clear()
        stations = self.api.get_stations()
        completer_strings = []
        for s in stations:
            self.ui.stationComboBox.addItem(s["Name"])
            completer_strings.append(s["Name"])
        self.comboboxCompleter = QCompleter(completer_strings, self)
        self.comboboxCompleter.setCompletionMode(0)
        self.ui.stationComboBox.setCompleter(self.comboboxCompleter)

        # Select Lammi as a first station but do not run the selection logic on first run
        self.ui.stationComboBox.setCurrentIndex(self.api.get_index_of_station("Hämeenlinna Lammi Pappila"))
        self._current_selected_model = self.api.get_stations()[
            self.api.get_index_of_station("Hämeenlinna Lammi Pappila")]
        self.ui.stationComboBox.currentIndexChanged.connect(self._select_place_from_combobox)

    def _background_fmicatalogue_error(self, err):
        """
        Handle errors which happened in fmi catalogue retrieval background thread. This is a
        error callback function provided for BackgroundTask class on construction.
        :param err:
        :return:
        """
        if hasattr(err, 'error_code'):
            if err.error_code == 'NODATASETS':
                self.show_error_alerts(Messages.no_datasets_found())
            elif err.error_code == 'METADATA_RETRIEVAL':
                self.show_error_alerts(Messages.fmicatalogue_error())
            else:
                self.show_error_alerts(Messages.unknown_error() + str(err))
        else:
            self.show_error_alerts(Messages.unknown_error() + str(err))

        self._current_available_datasets = None
        self._current_selected_dataset = None
        self.ui.dataSelectionCombobox.clear()
        self._set_ui_controls_status()

    def _set_ui_controls_status(self):
        active = self._current_selected_dataset is not None
        self.ui.downloadButton.setEnabled(active)
        self.ui.endDatetimeEdit.setEnabled(active)
        self.ui.startDatetimeEdit.setEnabled(active)

    def _set_up_ui(self):
        # language change signal
        self.setLanguageSignal.connect(lambda: menubar_actions.select_language(self, self._settings))

        self._set_up_station_comboboxes()
        self.catalogue_task = BackgroundTask()
        self.catalogue_task.start(self.api.get_catalogue_of_station, self._current_selected_model['FMISID'],
                                  self._set_available_datasets_from_catalogue, self._background_fmicatalogue_error)

        # When dataset is selected
        self.ui.dataSelectionCombobox.currentIndexChanged.connect(self._select_dataset_from_combobox)

        # wire download buttons to actions
        self.ui.downloadButton.clicked.connect(self._download)

        # wire date fields to their actions
        self.ui.endDatetimeEdit.dateChanged.connect(self._date_edited)
        self.ui.startDatetimeEdit.dateChanged.connect(self._date_edited)

        # statusbar
        self.statusBar().setStyleSheet("color: red;")

        # menubar actions
        self.ui.actionSet_api_key.triggered.connect(lambda: menubar_actions.set_apikey(self, self._settings))
        self.ui.actionExit.triggered.connect(menubar_actions.quit)
        self.ui.actionAbout.triggered.connect(menubar_actions.about)
        self.ui.actionSet_language.triggered.connect(lambda: menubar_actions.select_language(self, self._settings))
        self.ui.actionView_instructions.triggered.connect(menubar_actions.open_manual)
        self.ui.actionCheck_updates.triggered.connect(lambda: menubar_actions.check_updates(self._settings))

    @pyqtSlot(int, name='selectPlace')
    def _select_place_from_combobox(self, place_index):
        self.ui.stationComboBox.setCurrentIndex(place_index)
        self._current_selected_model = self.api.get_stations()[place_index]

        # Fetch catalog information of the current station and set datasets on completion
        self.catalogue_task.start(self.api.get_catalogue_of_station, self._current_selected_model['FMISID'],
                                  self._set_available_datasets_from_catalogue, self._background_fmicatalogue_error)

    def _set_available_datasets_from_catalogue(self, available_datasets):
        """
        Catalogue fetch completed, update contents of dataset combobox with fetched.
        :param available_datasets:
        :return:
        """
        self._current_available_datasets = available_datasets
        self.ui.dataSelectionCombobox.clear()
        for q in available_datasets:
            self.ui.dataSelectionCombobox.addItem(q["name"][self._language])
        self.ui.dataSelectionCombobox.setCurrentIndex(0)
        self._current_selected_dataset = self._current_available_datasets[0]
        self._set_ui_controls_status()
        self._set_time_field_limits()

    @pyqtSlot(int, name='selectDataset')
    def _select_dataset_from_combobox(self, dataset_index):
        """
        When new dataset is selected, update time data.
        :param dataset_index:
        :return:
        """
        if self._current_available_datasets is not None:
            self._current_selected_dataset = self._current_available_datasets[dataset_index]
            self.ui.availableFromContent.setText(
                datetime.datetime.strftime(self._current_selected_dataset["starttime"], '%d.%m.%Y'))
            self._set_time_field_limits()

    def _set_time_field_limits(self):
        # minimum date
        self.ui.startDatetimeEdit.clearMinimumDate()
        min_date = QDate(self._current_selected_dataset["starttime"])
        self.ui.startDatetimeEdit.setMinimumDate(min_date)

        self.ui.endDatetimeEdit.clearMinimumDate()
        min_date = QDate(self._current_selected_dataset["starttime"])
        self.ui.endDatetimeEdit.setMinimumDate(min_date)

        # maximum date
        self.ui.startDatetimeEdit.clearMaximumDate()
        if self._current_selected_dataset["endtime"] is not None:
            max_date = QDate(self._current_selected_dataset["endtime"])
        else:
            max_date = QDate(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
        self.ui.startDatetimeEdit.setMaximumDate(max_date)

        self.ui.endDatetimeEdit.clearMaximumDate()
        if self._current_selected_dataset["endtime"] is not None:
            max_date = QDate(self._current_selected_dataset["endtime"])
        else:
            max_date = QDate(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
        self.ui.endDatetimeEdit.setMaximumDate(max_date)

        new_date = QDate(self.ui.startDatetimeEdit.date().year(), self.ui.startDatetimeEdit.date().month(),
                         self.ui.startDatetimeEdit.date().day() + 1)
        self.ui.endDatetimeEdit.setDate(new_date)

        if self.ui.startDatetimeEdit.date() < self.ui.startDatetimeEdit.minimumDate():
            self.ui.startDatetimeEdit.setDate(self.ui.startDatetimeEdit.minimumDate())

    def _choose_place_to_save_data(self, dataframe):
        paths = QStandardPaths.standardLocations(0)
        if len(paths) > 0:
            path = paths[0]
        else:
            path = ""
        filename = QFileDialog.getSaveFileName(self, Messages.save_weatherdata_csv(),
                                               path + "/weather_data.csv",
                                               "Comma separated values CSV (*.csv);;All files (*)")
        if filename[0] != "":
            self._save_to_csv(dataframe, filename[0])

    def _get_date_time_from_ui(self, dateEdit, onlyDate=True):
        if onlyDate:
            return QDateTime(dateEdit.date()).toPyDateTime()
        else:
            return QDateTime(dateEdit.dateTime()).toPyDateTime()

    @pyqtSlot(name='editRealtimeDate')
    def _date_edited(self):
        """
        Date fields were edited. Check their content for invalid date ranges.
        :return:
        """
        if self.ui.startDatetimeEdit.date() == self.ui.endDatetimeEdit.date():
            self.ui.startDatetimeEdit.setStyleSheet("background-color: #FC9DB7;")
            self.ui.endDatetimeEdit.setStyleSheet("background-color: #FC9DB7;")
            self.statusBar().showMessage(Messages.start_end_date_warning(), 5000)
            self.ui.downloadButton.setEnabled(False)
        else:
            self.ui.startDatetimeEdit.setStyleSheet("background-color: white;")
            self.ui.endDatetimeEdit.setStyleSheet("background-color: white;")
            self.ui.downloadButton.setEnabled(True)

            if self.ui.endDatetimeEdit.date() < self.ui.startDatetimeEdit.date():
                self.ui.endDatetimeEdit.setStyleSheet("background-color: #FC9DB7;")
                self.statusBar().showMessage(Messages.end_date_warning(), 5000)
                self.ui.downloadButton.setEnabled(False)
            else:
                self.ui.endDatetimeEdit.setStyleSheet("background-color: white;")
                self.statusBar().showMessage("", 50)
                self.ui.downloadButton.setEnabled(True)

    def _download(self):
        """ Download weather data"""
        params = {"request": self._current_selected_dataset["request"],
                  "storedquery_id": self._current_selected_dataset["storedquery_id"],
                  "fmisid": self._current_selected_model["FMISID"],
                  "starttime": self._get_date_time_from_ui(self.ui.startDatetimeEdit, onlyDate=False),
                  "endtime": self._get_date_time_from_ui(self.ui.endDatetimeEdit, onlyDate=False),
                  "max_hours_range": self._current_selected_dataset["max_hours_range"]
                  }

        download = DownloadProgress(self)
        download.finishedSignal.connect(self._csvexport.save_data_to_csv)
        download.begin_download(params, self.api.get_data)

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
