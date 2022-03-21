# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sexeditor.ui'
##
## Created by: Qt User Interface Compiler version 5.15.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
    QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
    QPixmap, QRadialGradient)
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1104, 1446)
        self.actionCompile = QAction(MainWindow)
        self.actionCompile.setObjectName(u"actionCompile")
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setVerticalSpacing(6)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, -1, -1, -1)
        self.tabs = QTabWidget(self.centralwidget)
        self.tabs.setObjectName(u"tabs")
        font = QFont()
        font.setPointSize(10)
        self.tabs.setFont(font)
        self.tabs.setTabShape(QTabWidget.Rounded)
        self.tabs.setIconSize(QSize(16, 16))
        self.tabs.setElideMode(Qt.ElideNone)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)

        self.verticalLayout.addWidget(self.tabs)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.dockWidget = QDockWidget(MainWindow)
        self.dockWidget.setObjectName(u"dockWidget")
        self.dockWidget.setFont(font)
        self.dockWidget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.gridLayout_4 = QGridLayout(self.dockWidgetContents)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.console_output = QPlainTextEdit(self.dockWidgetContents)
        self.console_output.setObjectName(u"console_output")

        self.gridLayout_4.addWidget(self.console_output, 0, 0, 1, 1)

        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.BottomDockWidgetArea, self.dockWidget)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setAutoFillBackground(False)
        self.toolBar.setIconSize(QSize(24, 24))
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.toolBar.addAction(self.actionCompile)
        self.toolBar.addAction(self.actionSave)

        self.retranslateUi(MainWindow)

        self.tabs.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionCompile.setText(QCoreApplication.translate("MainWindow", u"Compile", None))
#if QT_CONFIG(tooltip)
        self.actionCompile.setToolTip(QCoreApplication.translate("MainWindow", u"Compile To Graph", None))
#endif // QT_CONFIG(tooltip)
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
#if QT_CONFIG(tooltip)
        self.actionSave.setToolTip(QCoreApplication.translate("MainWindow", u"Save Code", None))
#endif // QT_CONFIG(tooltip)
        self.dockWidget.setWindowTitle(QCoreApplication.translate("MainWindow", u"    CONSOLE", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

