from gui.mainwindow import *
from collections import OrderedDict
from PyQt5.QtCore import pyqtSlot, QObject
from queue import Queue


class BackgroundTask:
    """
    Class to run background tasks in one thread one at a time. This is used to retrieve catalogue data
    one at a time. Utilizes worker thread which waits something to fetch through synchronized queue.
    Each new task will clear previous ones from queue.
    """
    def __init__(self):
        self.queue = Queue()
        self.worker = BackgroundWorker(self.queue)
        self.worker.threadResultsSignal.connect(self._end)
        self.worker.threadExceptionSignal.connect(self._error)

        self.thread = QThread()
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def start(self, runnable_method, method_params, callback, error_callback):
        self.worker.moveToThread(self.thread)
        self.callback = callback
        self.error_callback = error_callback
        # Empty previous requests. Only newest matters
        while not self.queue.empty():
            self.queue.get()
        self.queue.put({'params': method_params, 'method': runnable_method})

    @pyqtSlot(object, name="taskFinished")
    def _end(self, results):
        self.callback(results)

    @pyqtSlot(object, name="exceptionInProcess")
    def _error(self, err):
        self.error_callback(err)


class BackgroundWorker(QObject):
    """
    A simple download worker class which is ran in separate thread to keep the ui responsive. utilizes
    FMIApi classes to process the data request made by user.
    """
    threadExceptionSignal = pyqtSignal(object, name="exceptionInProcess")
    threadResultsSignal = pyqtSignal(object, name="results")

    def __init__(self, queue, parent=None):
        super().__init__(parent)
        self.queue = queue

    def set_task(self, params, request_function):
        self.request_params = params
        self.request_function = request_function

    @pyqtSlot(name='services')
    def run(self):
        while True:
            task = self.queue.get()
            if task is not None:
                self.download_data(task['method'], task['params'])

    def download_data(self, request_function, request_params):
        try:
            results = request_function(request_params)
            self.threadResultsSignal.emit(results)
        except Exception as e:
            self.threadExceptionSignal.emit(e)
