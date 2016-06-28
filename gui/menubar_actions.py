import webbrowser
from PyQt5.QtCore import pyqtSlot, QCoreApplication, Qt
from PyQt5.QtWidgets import QInputDialog, QApplication, QMessageBox, QDialog
from gui.messages import Messages
from gui.languagedialog import LanguageDialog
from gui.ui_aboutdialog import Ui_AboutDialog

_ABOUT_INFORMATION = {
    'author': "<a href='http://www.tuomassalmi.com'>Tuomas Salmi</a>",
    'email': "<a href='mailto:salmi.tuomas@gmail.com'>salmi.tuomas@gmail.com</a>",
    'github': "<a href='https://github.com/Tumetsu/FMI-weather-downloader'>FMIDownloader Github</a>",
    'version': 'v. 0.9'
}


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        self.insert_params(self.ui.emailLabel, {'email': _ABOUT_INFORMATION['email']})
        self.insert_params(self.ui.authorLabel, {'author': _ABOUT_INFORMATION['author']})
        self.insert_params(self.ui.githubLabel, {'github': _ABOUT_INFORMATION['github']})
        self.insert_params(self.ui.aboutHeader, {'version': _ABOUT_INFORMATION['version']})

    def insert_params(self, ui_element, param):
        ui_element.setText(ui_element.text().format(**param))


LANGUAGE_IDS = {"Finnish" : "fi", "English" : "en"}
_MANUAL_URL = "http://tumetsu.github.io/FMI-weather-downloader/quickstart/quickstart.html"

def select_language(app, settings):
    lang_dialog = LanguageDialog(LANGUAGE_IDS, app._language, app)
    do_change = lang_dialog.exec_()

    if do_change == 1:
        settings.setValue("language", lang_dialog.get_language())
        app.set_language(lang_dialog.get_language())


@pyqtSlot()
def set_apikey(app, settings):
    key = QInputDialog.getText(app, QCoreApplication.translate("setapikeyheading", "Aseta tunnisteavain"),
                               Messages.set_apikey_dialog(), text=app.api.get_apikey())
    if key[1]:
        # todo: tänne kutsu oikeaan paikkaan
        apikey = key[0].strip()
        settings.setValue("apikey", apikey)
        app.api.set_apikey(apikey)


@pyqtSlot()
def open_manual():
    webbrowser.open(_MANUAL_URL)

@pyqtSlot()
def quit():
    QApplication.quit()

@pyqtSlot()
def about():
    about_dialog = AboutDialog()
    about_dialog.exec()

