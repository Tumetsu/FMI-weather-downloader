import webbrowser
from PyQt5.QtCore import pyqtSlot, QCoreApplication
from PyQt5.QtWidgets import QInputDialog, QApplication, QMessageBox
from gui.messages import Messages
from gui.languagedialog import LanguageDialog

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
    msgbox = QMessageBox()
    msgbox.information(None, QCoreApplication.translate("aboutheading", "Tietoa"), Messages.about_dialog())
    msgbox.show()
