# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sexeditor.ui'
##
## Created by: Qt User Interface Compiler version 5.15.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
    QTime,
    QUrl,
)
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QIcon,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(579, 869)
        self.actionCompile = QAction(MainWindow)
        self.actionCompile.setObjectName("actionCompile")
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionShowTemplate = QAction(MainWindow)
        self.actionShowTemplate.setObjectName("actionShowTemplate")
        self.actionShowTemplate.setCheckable(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setVerticalSpacing(6)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, -1, -1, -1)
        self.tabs = QTabWidget(self.centralwidget)
        self.tabs.setObjectName("tabs")
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
        self.dockWidget.setObjectName("dockWidget")
        self.dockWidget.setFont(font)
        self.dockWidget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout_4 = QGridLayout(self.dockWidgetContents)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.console_output = QPlainTextEdit(self.dockWidgetContents)
        self.console_output.setObjectName("console_output")

        self.gridLayout_4.addWidget(self.console_output, 0, 0, 1, 1)

        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.BottomDockWidgetArea, self.dockWidget)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setAutoFillBackground(False)
        self.toolBar.setIconSize(QSize(24, 24))
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.toolBar.addAction(self.actionCompile)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionShowTemplate)

        self.retranslateUi(MainWindow)

        self.tabs.setCurrentIndex(-1)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "MainWindow", None))
        self.actionCompile.setText(QCoreApplication.translate("MainWindow", "Compile", None))
        # if QT_CONFIG(tooltip)
        self.actionCompile.setToolTip(
            QCoreApplication.translate("MainWindow", "Compile To Graph", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.actionSave.setText(QCoreApplication.translate("MainWindow", "Save", None))
        # if QT_CONFIG(tooltip)
        self.actionSave.setToolTip(QCoreApplication.translate("MainWindow", "Save Code", None))
        # endif // QT_CONFIG(tooltip)
        self.actionShowTemplate.setText(
            QCoreApplication.translate("MainWindow", "Show Template", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionShowTemplate.setToolTip(
            QCoreApplication.translate("MainWindow", "Show expanded code", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.dockWidget.setWindowTitle(
            QCoreApplication.translate("MainWindow", "    CONSOLE", None)
        )
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", "toolBar", None))

    # retranslateUi
