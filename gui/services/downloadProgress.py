from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, QCoreApplication, Qt
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import pyqtSlot, QObject
from fmiapi.fmierrors import *
from gui.mainwindow import *
from collections import OrderedDict
from gui.services.downloadworker import DownloadWorker
from gui.messages import Messages


class DownloadProgress(QObject):
    """
    Dialog which is shown during download and parsing of the data. Displays the progress of the task
    of downloading and parsing. Creates a worker thread to do the actual download process in the background.
    """
    finishedSignal = pyqtSignal(OrderedDict, dict, name="processFinished")

    def __init__(self, parent):
        super(DownloadProgress, self).__init__(parent)
        self.parent = parent
        self.progressDialog = None
        self.worker = None
        self.thread = None

    def begin_download(self, request_params, request_function):
        self.progressDialog = QProgressDialog(self.parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.progressDialog.setWindowTitle(Messages.downloading_weatherdata())
        self.progressDialog.setAutoClose(False)
        self.progressDialog.setCancelButton(None)
        self.progressDialog.setLabelText(Messages.downloading_weatherdata())
        self.progressDialog.open()
        self.progressDialog.setValue(0)

        self.request_params = request_params
        self.worker = DownloadWorker(request_params, request_function)
        self.worker.threadUpdateSignal.connect(self._update_progress_bar)
        self.worker.threadExceptionSignal.connect(self._loading_failed)
        self.worker.threadResultsSignal.connect(self._process_finished)
        self.worker.threadChangeTaskSignal.connect(self._change_progress_dialog)

        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.download_data)
        self.thread.start()

    @pyqtSlot(int, int, name="progressUpdate")
    def _update_progress_bar(self, i, max_value):
        self.progressDialog.setRange(0, max_value)
        self.progressDialog.setValue(i)

    @pyqtSlot(object, name="exceptionInProcess")
    def _loading_failed(self, error):
        self.progressDialog.cancel()

        try:
            raise error
        except RequestException as e:
            if e.error_code == 400:
                # command to ask data probably invalid or there is a problem with current station
                self.parent.show_error_alerts(Messages.weatherstation_error() + str(e))
            else:
                self.parent.show_error_alerts(Messages.unknown_error() + str(e))
        except InvalidApikeyException:
                # apikey is invalid
                self.parent.show_error_alerts(Messages.request_failed_error())
        except NoDataException:
            self.parent.show_error_alerts(Messages.date_not_found_error())
        except QueryLimitException as e:
            self.parent.show_error_alerts(Messages.query_limit_error().format(e.wait_time))
        except Exception as e:
            self.parent.show_error_alerts(Messages.unknown_error() + str(e))

    @pyqtSlot(str, name="progressChange")
    def _change_progress_dialog(self, header):
        """
        When the "topic" of the progress bar changes from download to parsing for example.
        :param header:
        :return:
        """
        self.progressDialog.setLabelText(header)
        self.progressDialog.setValue(0)

    @pyqtSlot(list, name="results")
    def _process_finished(self, result):
        self.result = result
        self.progressDialog.close()
        self.finishedSignal.emit(self.result, self.request_params)
