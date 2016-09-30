from gui.mainwindow import *
from collections import OrderedDict
from PyQt5.QtCore import pyqtSlot, QObject


class BackgroundTask:
    def __init__(self, runnable_method, method_params, callback):
        self.worker = BackgroundWorker(method_params, runnable_method)
        self.worker.threadResultsSignal.connect(self._end)
        self.callback = callback
        self.thread = QThread()

    def start(self):
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.download_data)
        self.thread.start()

    @pyqtSlot(object, name="taskFinished")
    def _end(self, results):
        self.callback(results)
        self.thread.quit()


class BackgroundWorker(QObject):
    """
    A simple download worker class which is ran in separate thread to keep the ui responsive. utilizes
    FMIApi classes to process the data request made by user.
    """
    threadExceptionSignal = pyqtSignal(object, name="exceptionInProcess")
    threadResultsSignal = pyqtSignal(object, name="results")

    def __init__(self, params, request_function, parent=None):
        super().__init__(parent)
        self.request_params = params
        self.request_function = request_function

    @pyqtSlot(name='services')
    def download_data(self):
        try:
            results = self.request_function(self.request_params)
            self.threadResultsSignal.emit(results)
        except Exception as e:
            self.threadExceptionSignal.emit(e)
