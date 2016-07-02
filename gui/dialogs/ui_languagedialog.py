# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'language.ui'
#
# Created: Wed Apr  1 12:53:33 2015
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LanguageDialog(object):
    def setupUi(self, LanguageDialog):
        LanguageDialog.setObjectName("LanguageDialog")
        LanguageDialog.resize(387, 143)
        self.verticalLayout = QtWidgets.QVBoxLayout(LanguageDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(LanguageDialog)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(LanguageDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(LanguageDialog)
        self.buttonBox.accepted.connect(LanguageDialog.accept)
        self.buttonBox.rejected.connect(LanguageDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(LanguageDialog)

    def retranslateUi(self, LanguageDialog):
        _translate = QtCore.QCoreApplication.translate
        LanguageDialog.setWindowTitle(_translate("LanguageDialog", "Language"))
        self.groupBox.setTitle(_translate("LanguageDialog", "Select language"))

