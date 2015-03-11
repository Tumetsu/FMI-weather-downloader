from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QProgressDialog, QMessageBox
from PyQt5.QtCore import pyqtSlot, QObject
from fmierrors import *

""" RAJAPINTA:
PRIVATE_SIGNAALIT: UPDATE, RESULTS
PUBLIC_SIGNAALIT: EXCEPTION, FINISHED

TARVITSEE FUNKTION JOKA AJETAAN TYÖLÄISSÄIKEESSÄ. FUNKTION TARJOTTAVA PARAMETRI CALLBACK-FUNKTION TARJOAMISEEN
PÄIVITYKSIÄ VARTEN.
LUOKKA TARVITSEE MYÖS SLOTIT HOITMAAN JULKISET
SIGNAALIT UI-SÄIKEESSÄ.
"""

class ProgressBarTask(QObject):
    """ This is generic implementation which offers a simple way to execute stuff parallelly while
    displaying Qt-progress dialog and offering signals to connect to. Wraps signals and connections between
     UI-thread and worker-thread."""
    parent = None
    processCount = 0
    threadUpdateSignal = pyqtSignal(int, int, name="progressUpdate")
    threadExceptionSignal = pyqtSignal(object,name="exceptionInProcess")
    threadResultsSignal = pyqtSignal(list, name="results")
    finishedSignal = pyqtSignal(list, name="processFinished")
    result = {}

    def __init__(self, parent):
        super(ProgressBarTask, self).__init__(parent)
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
        self.progressDialog.setLabelText("Ladataan säädataa...")
        self.progressDialog.open()
        self.progressDialog.setValue(0)
        self.thread.run = self._runProcess
        self.requestParams = requestparams
        self.request_function = request_function
        self.thread.start()


    def _runProcess(self):
        try:

            #TODO: tähän funktio joka halutaan ajaa ja joka palauttaa jonkin tuloksen
            results = self.request_function(self.requestParams, self._processUpdateCallback)
            self.threadResultsSignal.emit(results)
        except Exception as e:
            print("virhe")
            self.threadExceptionSignal.emit(e)


    @pyqtSlot(int, int)
    def _updateProgressBarInMainThread(self, i, max):
        self.progressDialog.setRange(0, max)
        self.progressDialog.setValue(i)

    @pyqtSlot(object)
    def _loadingFailed(self, error):
        """POIKKEUSTEN KÄSITTELY UI-SÄIKEESSÄ"""
        self.progressDialog.cancel()
        print ("joo")
        try:
            try:
                raise error
            except (RequestException, NoDataException) as e:
                print ("joo")
                if e.errorCode == 400:
                    #luultavasti komento jolla pyydetään on väärä tai palvelussa on vika tälle paikkakunnalle
                    self.parent._show_error_alerts("Määritettyä sääasemaa ei löydetty.\nIlmatieteenlaitoksen palvelussa on häiriö tai "
                                          "mikäli ongelma toistuu muillakin kohteilla, saattaa tämä ohjelma vaatia päivitystä. Katso tiedot yhteydenotosta File->Tietoa valikosta.\n\nVirheen kuvaus:\n" + str(e))
                if e.errorCode == 404:
                    #apikey on luultavasti väärä
                    self.parent._show_error_alerts("Datapyyntö ei onnistunut.\nOletko asettanut vaadittavan tunnisteavaimen tai onko se virheellinen? Ilmatieteenlaitos vaatii rekisteröitymistä palveluun "
                                          "ennen sen käyttöä. Katso lisätietoa valikosta File->Aseta tunnisteavain.")

                if e.errorCode == 429:
                    #liikaa pyyntöjä
                     self.parent._show_error_alerts("Teit liikaa datapyyntöjä palveluun. Odota 5-10min ja yritä sitten uudelleen.")

                if e.errorCode == "NODATA":
                     #vastauksessa ei ollut dataa. Onko paikasta saatavissa dataa tältä aikaväliltä?
                     self.parent._show_error_alerts("Määritettyä ajanjaksoa ei löytynyt.\nTodennäköisesti ilmatieteenlaitoksella ei ole dataa tälle ajanjaksolle.\nKokeile "
                                           "pitempää ajanjaksoa, esim. yhtä vuotta tai myöhäisempää aloituspäivämäärää.\n\nVirheen kuvaus:\n" + str(e))
        except Exception as e:
             self.parent._show_error_alerts("Tuntematon virhe: " + str(e))




    @pyqtSlot(list)
    def _processFinished(self, result):
        print("valmis")
        self.result = result
        self.finishedSignal.emit(self.result)


    def _processUpdateCallback(self, i, max):
        self.threadUpdateSignal.emit(i, max)






