from PyQt5.QtCore import QSettings
from gui.messages import Messages

class Settings(QSettings):

    def __init__(self):
        super().__init__("fmidownloader", "fmidownloader")

    def load_qsettings(self, app):
        self._load_lang_settings(app)
        self._load_api_settings(app)

    def _load_api_settings(self, app):
        stored_apikey = self.value("apikey")
        if stored_apikey is not None:
            app.api.set_apikey(stored_apikey)
        else:
            app.statusBar().showMessage(Messages.set_apikey_message(), 0)

    def _load_lang_settings(self, app):
        stored_lang = self.value("language")
        if stored_lang is not None:
            app.set_language(stored_lang)
        else:
            print('emit setLanguageSignal')
            app.setLanguageSignal.emit()

