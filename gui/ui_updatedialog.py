# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'updatedialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CheckUpdatesDialog(object):
    def setupUi(self, CheckUpdatesDialog):
        CheckUpdatesDialog.setObjectName("CheckUpdatesDialog")
        CheckUpdatesDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        CheckUpdatesDialog.resize(400, 81)
        CheckUpdatesDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(CheckUpdatesDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.newVersion_label = QtWidgets.QLabel(CheckUpdatesDialog)
        self.newVersion_label.setObjectName("newVersion_label")
        self.verticalLayout.addWidget(self.newVersion_label)
        self.currentVersion_label = QtWidgets.QLabel(CheckUpdatesDialog)
        self.currentVersion_label.setObjectName("currentVersion_label")
        self.verticalLayout.addWidget(self.currentVersion_label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.checkUpdatesOnStartUp_Checkbox = QtWidgets.QCheckBox(CheckUpdatesDialog)
        self.checkUpdatesOnStartUp_Checkbox.setEnabled(True)
        self.checkUpdatesOnStartUp_Checkbox.setChecked(True)
        self.checkUpdatesOnStartUp_Checkbox.setObjectName("checkUpdatesOnStartUp_Checkbox")
        self.horizontalLayout.addWidget(self.checkUpdatesOnStartUp_Checkbox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.goToDownloads_Button = QtWidgets.QPushButton(CheckUpdatesDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.goToDownloads_Button.sizePolicy().hasHeightForWidth())
        self.goToDownloads_Button.setSizePolicy(sizePolicy)
        self.goToDownloads_Button.setObjectName("goToDownloads_Button")
        self.horizontalLayout.addWidget(self.goToDownloads_Button)
        self.buttonBox = QtWidgets.QDialogButtonBox(CheckUpdatesDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(CheckUpdatesDialog)
        self.buttonBox.accepted.connect(CheckUpdatesDialog.close)
        QtCore.QMetaObject.connectSlotsByName(CheckUpdatesDialog)

    def retranslateUi(self, CheckUpdatesDialog):
        _translate = QtCore.QCoreApplication.translate
        CheckUpdatesDialog.setWindowTitle(_translate("CheckUpdatesDialog", "Updates"))
        self.newVersion_label.setText(_translate("CheckUpdatesDialog", "Available FMIDownloader version: "))
        self.currentVersion_label.setText(_translate("CheckUpdatesDialog", "Your current version is: "))
        self.checkUpdatesOnStartUp_Checkbox.setText(_translate("CheckUpdatesDialog", "Check updates on startup"))
        self.goToDownloads_Button.setText(_translate("CheckUpdatesDialog", "Go to downloads"))

