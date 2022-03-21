from __future__ import annotations

from time import gmtime, strftime
from typing import Iterator

from PySide2.QtGui import QFont
from PySide2.QtWidgets import QMainWindow, QApplication

from ui.editortab import EditorTab

from . import sexeditor
from settings import PluginSettings, get_plugin_icon, ExpressionType
from sdutils import qt_mgr

import sd.api as sda


main_window: MainWindow = None

def get_main_window() -> MainWindow:
    global main_window

    if main_window is None:
        main_window = MainWindow(qt_mgr.getMainWindow())
        main_window.show()
        return main_window
    else:
        return main_window

style_sheet = """
QToolBar {spacing: 1}
QToolButton {padding: 4; margin: 2}
"""

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        plugin_settings = PluginSettings()
        self.plugin_settings = plugin_settings

        self.setStyleSheet(style_sheet)

        self.ui = sexeditor.Ui_MainWindow()
        self.ui.setupUi(self)

        tab_font = self.ui.tabs.font()
        tab_font.setPointSize(plugin_settings["tab_font_size"])
        self.ui.tabs.setFont(tab_font)

        self.ui.actionCompile.setIcon(get_plugin_icon("build.png"))
        self.ui.actionCompile.triggered.connect(self.on_compile)

        self.ui.actionSave.setIcon(get_plugin_icon("save.png"))

        font = QFont(self.plugin_settings["font"])
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(plugin_settings["console_font_size"])

        self.ui.console_output.setFont(font)
        self.ui.console_output.setReadOnly(True)

        font = QFont(self.plugin_settings["font"])
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(plugin_settings["editor_font_size"])
        
        QApplication.setFont(font, "CodeEditor")

        width = plugin_settings["window_size"][0]
        height = plugin_settings["window_size"][1]
        pos_x = plugin_settings["window_pos"][0]
        pos_y = plugin_settings["window_pos"][1]
        #self.setGeometry(pos_x, pos_y, width, height)
        self.move(pos_x, pos_y)
        self.resize(width, height)

        self.setWindowTitle("Expression Editor")
        self.ui.tabs.tabCloseRequested.connect(self.ui.tabs.removeTab)

    def closeEvent(self, event):
        global main_window
        main_window = None

        self.plugin_settings["window_size"] = [self.width(), self.height()]
        self.plugin_settings["window_pos"] = [self.pos().x(), self.pos().y()]
        self.plugin_settings.save()

    def console_message(self, message):
        timestamp = strftime("[%H:%M:%S] ", gmtime())
        self.ui.console_output.appendHtml(timestamp + message)
        self.ui.console_output.repaint()

    def add_editor_tab(self, tab: EditorTab, title: str):
        self.ui.tabs.addTab(tab, title)

    def editor_tabs(self) -> Iterator[EditorTab]:
        return (self.ui.tabs.widget(i) for i in range(self.ui.tabs.count()))

    def find_graph_tab(self, graph: sda.SDGraph) -> EditorTab:
        graph_url = graph.getUrl()
        if not graph_url:
            return None
        return next((t for t in self.editor_tabs() if t.expr_type is not ExpressionType.PACKAGE and t.graph.getUrl() == graph_url), None)

    def find_package_tab(self, pkg: sda.SDPackage) -> sda.SDGraph:
        pkg_path = pkg.getFilePath()
        return next((t for t in self.editor_tabs() if t.expr_type is ExpressionType.PACKAGE and t.package.getFilePath() == pkg_path), None)


    def on_compile(self):
        current_tab: EditorTab = self.ui.tabs.currentWidget()
        if current_tab is not None:
            current_tab.create_nodes()