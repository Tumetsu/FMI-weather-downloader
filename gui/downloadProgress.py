from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, QCoreApplication

from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import pyqtSlot, QObject
from fmiapi.fmierrors import *
from gui.mainwindow import *

class DownloadProgress(QObject):

    parent = None
    processCount = 0
    threadUpdateSignal = pyqtSignal(int, int, name="progressUpdate")
    threadExceptionSignal = pyqtSignal(object,name="exceptionInProcess")
    threadResultsSignal = pyqtSignal(list, name="results")
    finishedSignal = pyqtSignal(list, name="processFinished")
    result = {}

    def __init__(self, parent):
        super(DownloadProgress, self).__init__(parent)
        self.parent = parent
        self.thread = QThread(parent = self.parent)
        self.threadUpdateSignal.connect(self._updateProgressBarInMainThread)
        self.threadExceptionSignal.connect(self._loadingFailed)
        self.threadResultsSignal.connect(self._processFinished)
        self.requestParams = ""
        self.request_function = None

    def beginDownload(self, requestparams, request_function):
        self.progressDialog = QProgressDialog(self.parent)
        self.progressDialog.setCancelButton(None)
        self.progressDialog.setLabelText(QCoreApplication.translate("downloading_weatherdata","Ladataan säädataa..."))
        self.progressDialog.open()
        self.progressDialog.setValue(0)
        self.thread.run = self._runProcess
        self.requestParams = requestparams
        self.request_function = request_function
        self.thread.start()


    def _runProcess(self):
        try:
            results = self.request_function(self.requestParams, self._processUpdateCallback)
            self.threadResultsSignal.emit(results)
        except Exception as e:
            self.threadExceptionSignal.emit(e)


    @pyqtSlot(int, int)
    def _updateProgressBarInMainThread(self, i, max):
        self.progressDialog.setRange(0, max)
        self.progressDialog.setValue(i)

    @pyqtSlot(object)
    def _loadingFailed(self, error):
        self.progressDialog.cancel()

        try:
            try:
                raise error
            except (RequestException, NoDataException) as e:
                if e.errorCode == 400:
                    #luultavasti komento jolla pyydetään on väärä tai palvelussa on vika tälle paikkakunnalle
                    self.parent._show_error_alerts(QCoreApplication.translate("weatherstationnotfound_error", "Määritettyä sääasemaa ei löydetty.\nIlmatieteenlaitoksen palvelussa on häiriö tai "
                                          "mikäli ongelma toistuu muillakin kohteilla, saattaa tämä ohjelma vaatia päivitystä. Katso tiedot yhteydenotosta Tiedosto->Tietoa valikosta.\n\nVirheen kuvaus:\n") + str(e))
                if e.errorCode == 404:
                    #apikey on luultavasti väärä
                    self.parent._show_error_alerts(QCoreApplication.translate("requestfailed_error", "Datapyyntö ei onnistunut.\nOletko asettanut vaadittavan tunnisteavaimen tai onko se virheellinen?\n\nIlmatieteenlaitos vaatii rekisteröitymistä palveluun "
                                          "ennen sen käyttöä. Katso lisätietoa valikosta Tiedosto->Aseta tunnisteavain."))

                if e.errorCode == "NODATA":
                     #vastauksessa ei ollut dataa. Onko paikasta saatavissa dataa tältä aikaväliltä?
                     self.parent._show_error_alerts(Mainwindow._DATE_NOT_FOUND_ERROR + str(e))
        except Exception as e:
             self.parent._show_error_alerts(Mainwindow._UNKNOWN_ERROR + str(e))




    @pyqtSlot(list)
    def _processFinished(self, result):
        self.result = result
        self.finishedSignal.emit(self.result)


    def _processUpdateCallback(self, i, max):
        self.threadUpdateSignal.emit(i, max)






