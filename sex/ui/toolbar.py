import json

from PySide2.QtWidgets import QToolBar

import sd.api
import sexparser
from sdutils import app, qt_mgr, ui_mgr
from ui.window import get_main_window

from ui.editortab import EditorTab

class SexToolBar(QToolBar):
    def __init__(self, graph_view_id, qt_ui_mgr, parser):
        super(SexToolBar, self).__init__(parent=qt_ui_mgr.getMainWindow())

        # Save the graphViewID and uiMgr for later use.
        self.__graph_view_id = graph_view_id
        self.__qt_ui_mgr = qt_ui_mgr
        self.parser = parser

        # Add actions to our toolbar.
        act = self.addAction("Expression")
        act.setToolTip("Open expression editor")
        act.triggered.connect(self.open_sex_window)

    def open_sex_window(self):
        self.parser.import_functions("functions.sbs", app)
        self.parser.import_current_graph_functions(app)

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