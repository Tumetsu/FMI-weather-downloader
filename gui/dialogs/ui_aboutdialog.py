# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'aboutdialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(400, 170)
        AboutDialog.setModal(True)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(AboutDialog)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.aboutHeader = QtWidgets.QLabel(AboutDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.aboutHeader.setFont(font)
        self.aboutHeader.setAlignment(QtCore.Qt.AlignCenter)
        self.aboutHeader.setObjectName("aboutHeader")
        self.verticalLayout_3.addWidget(self.aboutHeader)
        self.descriptionLabel = QtWidgets.QLabel(AboutDialog)
        self.descriptionLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.descriptionLabel.setWordWrap(True)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.verticalLayout_3.addWidget(self.descriptionLabel)
        self.authorLabel = QtWidgets.QLabel(AboutDialog)
        self.authorLabel.setTextFormat(QtCore.Qt.RichText)
        self.authorLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.authorLabel.setOpenExternalLinks(True)
        self.authorLabel.setObjectName("authorLabel")
        self.verticalLayout_3.addWidget(self.authorLabel)
        self.emailLabel = QtWidgets.QLabel(AboutDialog)
        self.emailLabel.setTextFormat(QtCore.Qt.RichText)
        self.emailLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.emailLabel.setOpenExternalLinks(True)
        self.emailLabel.setObjectName("emailLabel")
        self.verticalLayout_3.addWidget(self.emailLabel)
        self.githubLabel = QtWidgets.QLabel(AboutDialog)
        self.githubLabel.setTextFormat(QtCore.Qt.RichText)
        self.githubLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.githubLabel.setOpenExternalLinks(True)
        self.githubLabel.setObjectName("githubLabel")
        self.verticalLayout_3.addWidget(self.githubLabel)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.closeButton = QtWidgets.QPushButton(AboutDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.closeButton.sizePolicy().hasHeightForWidth())
        self.closeButton.setSizePolicy(sizePolicy)
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout.addWidget(self.closeButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.retranslateUi(AboutDialog)
        self.closeButton.clicked.connect(AboutDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        _translate = QtCore.QCoreApplication.translate
        AboutDialog.setWindowTitle(_translate("AboutDialog", "About"))
        self.aboutHeader.setText(_translate("AboutDialog", "FMIDownloader"))
        self.descriptionLabel.setText(_translate("AboutDialog", "Yksinkertainen sovellus ilmatieteenlaitoksen säähavaintodatan lataamiseen.Jos ohjelmasta herää kysymyksiä, voit ottaa yhteyttä"))
        self.authorLabel.setText(_translate("AboutDialog", "<a href=\'http://www.tuomassalmi.com\'>Tuomas Salmi 2015-2016</a>"))
        self.emailLabel.setText(_translate("AboutDialog", "<a href=\'mailto:salmi.tuomas@gmail.com\'>salmi.tuomas@gmail.com</a>"))
        self.githubLabel.setText(_translate("AboutDialog", "<a href=\'https://github.com/Tumetsu/FMI-weather-downloader\'>FMIDownloader Github</a>"))
        self.closeButton.setText(_translate("AboutDialog", "Close"))

