import json
import os

from PySide2.QtWidgets import QToolBar, QAction, QLabel

import sd.api
from settings import ExpressionType
import sexparser
from sdutils import app, qt_mgr, ui_mgr
from ui.window import get_main_window

from ui.editortab import EditorTab

style_sheet = """
QToolButton {color: lightyellow; font: bold}
"""

class SexToolBar(QToolBar):
    def __init__(self, graph_view_id, qt_ui_mgr, parser):
        super().__init__(parent=qt_ui_mgr.getMainWindow())

        # Save the graphViewID and uiMgr for later use.
        self.__graph_view_id = graph_view_id
        self.__qt_ui_mgr = qt_ui_mgr
        self.parser = parser
        self.setStyleSheet(style_sheet)

        self.addWidget(QLabel("Expressions:"))

        # Add actions to our toolbar.
        act = self.addAction("Graph")
        act.setToolTip("Open Graph Expression Editor")
        act.triggered.connect(self.open_graph_expression_editor)

        pkg_action: QAction = self.addAction("Package")
        pkg_action.setToolTip("Open Package Expression Editor")
        pkg_action.triggered.connect(self.open_package_expression_editor)

    def prepare_editor(self):
        self.parser.import_functions("functions.sbs", app)
        self.parser.import_current_graph_functions(app)

    def open_package_expression_editor(self):
        self.prepare_editor()

        graph: sd.api.SDGraph = ui_mgr.getCurrentGraph()
        window = get_main_window()
        pkg: sd.api.SDPackage = graph.getPackage()

        
        package_tab = window.find_package_tab(pkg)
        if package_tab is not None:
            window.ui.tabs.setCurrentWidget(package_tab)
            return

        editor_tab = EditorTab(window, graph, ExpressionType.PACKAGE)

        pkg_path = pkg.getFilePath()
        pkg_name = "Unsaved Package"
        if pkg_path:
            pkg_name = os.path.splitext(os.path.basename(pkg_path))[0]

        
        window.add_editor_tab(editor_tab, pkg_name)
        window.ui.tabs.setCurrentWidget(editor_tab)

        try:
            mdata: sd.api.SDMetadataDict = pkg.getMetadataDict()
            src_value = mdata.getPropertyValueFromId("expression")
            if src_value:
                editor_tab.set_source(src_value.get())
        except sd.api.APIException:
            pass

    def open_graph_expression_editor(self):
        graph = ui_mgr.getCurrentGraph()

        if isinstance(graph, sd.api.SDSBSCompGraph):
            self.open_compgraph_expression_editor()

        elif isinstance(graph, sd.api.SDSBSFunctionGraph):
            self.open_funcgraph_expression_editor()


    def open_compgraph_expression_editor(self):
        self.prepare_editor()

        graph: sd.api.SDGraph = ui_mgr.getCurrentGraph()
        window = get_main_window()

        graph_tab = window.find_graph_tab(graph)
        if graph_tab is not None:
            window.ui.tabs.setCurrentWidget(graph_tab)
            return

        editor_tab = window.find_graph_tab(graph)
        if editor_tab is not None:
            window.ui.tabs.setCurrentWidget(editor_tab)

        tab_title = graph.getIdentifier()

        editor_tab = EditorTab(window, graph, ExpressionType.COMPOSITE_GRAPH)
        editor_tab.show()
        window.add_editor_tab(editor_tab, tab_title)
        window.ui.tabs.setCurrentWidget(editor_tab)

        mdata: sd.api.SDMetadataDict = graph.getMetadataDict()

        try:
            src_value = mdata.getPropertyValueFromId("expression")
            if src_value:
                editor_tab.set_source(src_value.get())
        except sd.api.APIException:
            pass


    def open_funcgraph_expression_editor(self):
        self.prepare_editor()

        graph: sd.api.SDGraph = ui_mgr.getCurrentGraph()
        window = get_main_window()

        graph_tab = window.find_graph_tab(graph)
        if graph_tab is not None:
            window.ui.tabs.setCurrentWidget(graph_tab)
            return

        editor_tab = EditorTab(window, graph)

        tab_title = graph.getIdentifier()
        if not tab_title:
            tab_title = "[ Property Graph ]"

        window.add_editor_tab(editor_tab, tab_title)
        editor_tab.show()
        window.ui.tabs.setCurrentWidget(editor_tab)

        src: str = ""
        graph_objects = graph.getGraphObjects()

        found_snippet = False

        for i in range(graph_objects.getSize()):
            graph_object = graph_objects.getItem(i)
            
            if isinstance(graph_object, sd.api.SDGraphObjectFrame) and graph_object.getTitle() == "snippet":
                found_snippet = True
                graph_object: sd.api.SDGraphObjectFrame
                src = graph_object.getDescription()

                editor_tab.set_source(src)
                editor_tab.frame_object = graph_object
                editor_tab.save_source()

        if not found_snippet:
            user_data_string = graph.getAnnotationPropertyValueFromId("userdata")
            if window.plugin_settings["use_snippet_object"] or user_data_string is None:
                new_frame_object = sd.api.SDGraphObjectFrame.sNew(graph)

                new_frame_object.setTitle("snippet")
                new_frame_object.setPosition(sd.api.sdbasetypes.float2(-sexparser.grid_size * 8.8, -sexparser.grid_size * 0.5))
                new_frame_object.setColor(sd.api.sdbasetypes.ColorRGBA(0.145, 0.145, 0.145, 1.0))
                new_frame_object.setSize(sd.api.sdbasetypes.float2(sexparser.grid_size * 8, sexparser.grid_size * 20))
                editor_tab.frame_object = new_frame_object

            if user_data_string is not None:

                try:
                    user_data = json.loads(user_data_string.get())
                    src = user_data.get("expression", "")
                    editor_tab.set_source(src)
                except ValueError as e:
                    pass