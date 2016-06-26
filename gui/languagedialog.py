from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog, QProgressDialog, QMessageBox
from PyQt5.QtCore import pyqtSlot, QObject
from PyQt5.QtWidgets import  QRadioButton
from gui.ui_languagedialog import Ui_LanguageDialog


class LanguageDialog(QDialog):

    def __init__(self, language_ids, currentlanguage, parent=None):
        super(LanguageDialog, self).__init__(parent)
        self.ui = Ui_LanguageDialog()
        self.ui.setupUi(self)
        self.currentLang = currentlanguage
        self._LANGUAGE_IDS = language_ids
        self._radiobuttons = []

        for key, value in self._LANGUAGE_IDS.items():
            radio = QRadioButton(key)
            if currentlanguage == value:
                radio.setChecked(True)
            self.ui.groupBox.layout().addWidget(radio)
            self._radiobuttons.append(radio)

    def get_language(self):
        for r in self._radiobuttons:
            if r.isChecked():
                return self._LANGUAGE_IDS[r.text()]
