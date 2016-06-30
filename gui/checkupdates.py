import webbrowser
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog
from PyQt5.QtCore import pyqtSlot, QObject
from gui.ui_updatedialog import Ui_CheckUpdatesDialog
from gui.app_information import ABOUT_INFORMATION
import http.client
import urllib.request
import json
import re
from gui.messages import Messages


class UpdateDialog(QDialog):
    def __init__(self, settings, their_version=None, parent=None):
        super(UpdateDialog, self).__init__(parent)
        self.ui = Ui_CheckUpdatesDialog()
        self.ui.setupUi(self)
        self.settings = settings
        self.ui.goToDownloads_Button.clicked.connect(self._go_to_downloads)
        self.ui.currentVersion_label.setText(self.ui.currentVersion_label.text() + ABOUT_INFORMATION['version'])
        self.ui.checkUpdatesOnStartUp_Checkbox.stateChanged.connect(self._checkbox_set)

        if settings.check_updates() == 'true':
            self.ui.checkUpdatesOnStartUp_Checkbox.setChecked(True)
        else:
            self.ui.checkUpdatesOnStartUp_Checkbox.setChecked(False)

        if their_version is None:
            self.worker = CheckUpdatesWorker(ABOUT_INFORMATION['github_api_host'],
                                             ABOUT_INFORMATION['github_api_releases_url'],
                                             ABOUT_INFORMATION['version'])
            self.worker.threadResultsSignal.connect(self._updates_information_retrieved)

            self.thread = QThread()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.check_updates)
            self.thread.start()
        else:
            self.ui.newVersion_label.setText(self.ui.newVersion_label.text() + their_version)

    def _checkbox_set(self):
        value = self.ui.checkUpdatesOnStartUp_Checkbox.checkState()
        self.settings.setValue("checkupdates", value != 0)

    @pyqtSlot(object, name='updateInfoRetrieved')
    def _updates_information_retrieved(self, result):
        if result['status'] == 'success':
            # Update version info to the dialog
            their_version = result['their_version']
            self.ui.newVersion_label.setText(self.ui.newVersion_label.text() + their_version)
        else:
            self.ui.newVersion_label.setText(self.ui.newVersion_label.text() + Messages.failed_to_get_version())

    @pyqtSlot(name='gotoDownloads')
    def _go_to_downloads(self):
        webbrowser.open(ABOUT_INFORMATION['releases_url'])


class CheckUpdatesOnStartup:
    def __init__(self, settings):
        self.settings = settings
        if settings.check_updates() == 'true':
            # Retrieve update information on background:
            self.worker = CheckUpdatesWorker(ABOUT_INFORMATION['github_api_host'],
                                             ABOUT_INFORMATION['github_api_releases_url'],
                                             ABOUT_INFORMATION['version'])
            self.worker.threadResultsSignal.connect(self._updates_information_retrieved)
            self.thread = QThread()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.check_updates)
            self.thread.start()

    @pyqtSlot(name='startupcheck')
    def _updates_information_retrieved(self, result):
        if result['status'] == 'success' and result['should_update']:
            updates_dialog = UpdateDialog(self.settings, their_version=result['their_version'])
            updates_dialog.exec()


class CheckUpdatesWorker(QObject):
    threadResultsSignal = pyqtSignal(object, name="results")

    def __init__(self, host, url, current_version, parent=None):
        super().__init__(parent)
        self.url = url
        self.host = host
        self.current_version = current_version

    def _get_release_version(self, received):
        if not received['prerelease']:
            # Naive version number comparator
            # tags should be in form of v0.71.1 or v1.2b etc.
            p = re.compile('v\.?\s?(.+)', flags=re.IGNORECASE)
            m = p.search(received['tag_name'])
            if m is not None:
                their_tokens = m.group(1).split('.')[0:3]
                my_tokens = self.current_version.split('.')[0:3]
                # Make sure lists are sized 3
                if len(their_tokens) < 3:
                    their_tokens = their_tokens + ['0'] * (3-len(their_tokens))
                if len(my_tokens) < 3:
                    my_tokens = my_tokens + ['0'] * (3-len(my_tokens))

                there_is_update = False
                for index, n in enumerate(their_tokens):
                    their = int(re.sub('[a-zA-z]', '', n))  # remove possible letters
                    my = int(re.sub('[a-zA-z]', '', my_tokens[index]))  # remove possible letters
                    if their > my:
                        there_is_update = True
                        break
                return there_is_update
            return False

    @pyqtSlot(name='download')
    def check_updates(self):
        try:
            connection = http.client.HTTPSConnection(self.host)
            headers = {'User-Agent': 'FMI-weather-downloader'}
            connection.request("GET", self.url, headers=headers)

            response = connection.getresponse()
            if response.status == 200:
                data = response.read().decode('utf-8')
                data = json.loads(data)
                should_update = self._get_release_version(data)
                self.threadResultsSignal.emit({'status': 'success', 'raw_data': data,
                                               'should_update': should_update,
                                               'their_version': data['tag_name']})
            else:
                raise Exception('Error ' + str(response.status))
        except Exception:
            self.threadResultsSignal.emit({'status': 'error'})
