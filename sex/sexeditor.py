# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sexeditor.ui'
##
## Created by: Qt User Interface Compiler version 5.14.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *

from codeeditor import CodeEditor


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1345, 1429)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setVerticalSpacing(6)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabs = QTabWidget(self.centralwidget)
        self.tabs.setObjectName(u"tabs")
        font = QFont()
        font.setPointSize(10)
        self.tabs.setFont(font)
        self.tabs.setTabShape(QTabWidget.Rounded)
        self.tabs.setIconSize(QSize(16, 16))
        self.tabs.setElideMode(Qt.ElideNone)
        self.editor_tab = QWidget()
        self.editor_tab.setObjectName(u"editor_tab")
        self.gridLayout_2 = QGridLayout(self.editor_tab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 6, 0, 0)
        self.code_editor = CodeEditor(self.editor_tab)
        self.code_editor.setObjectName(u"code_editor")

        self.gridLayout_2.addWidget(self.code_editor, 1, 0, 1, 1)

        self.tabs.addTab(self.editor_tab, "")
        self.render_tab = QWidget()
        self.render_tab.setObjectName(u"render_tab")
        self.gridLayout_3 = QGridLayout(self.render_tab)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 6, 0, 0)
        self.render_view = CodeEditor(self.render_tab)
        self.render_view.setObjectName(u"render_view")
        self.render_view.setReadOnly(True)

        self.gridLayout_3.addWidget(self.render_view, 0, 0, 1, 1)

        self.tabs.addTab(self.render_tab, "")

        self.verticalLayout.addWidget(self.tabs)

        self.compile = QPushButton(self.centralwidget)
        self.compile.setObjectName(u"compile")
        font1 = QFont()
        font1.setPointSize(14)
        self.compile.setFont(font1)

        self.verticalLayout.addWidget(self.compile)

        self.console_output = QPlainTextEdit(self.centralwidget)
        self.console_output.setObjectName(u"console_output")

        self.verticalLayout.addWidget(self.console_output)

        self.verticalLayout.setStretch(0, 4)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.tabs.setTabText(self.tabs.indexOf(self.editor_tab), QCoreApplication.translate("MainWindow", u"  Code Editor  ", None))
        self.tabs.setTabText(self.tabs.indexOf(self.render_tab), QCoreApplication.translate("MainWindow", u"  View Generated Code  ", None))
        self.compile.setText(QCoreApplication.translate("MainWindow", u"COMPILE", None))
    # retranslateUi

