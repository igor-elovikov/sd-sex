import json

from PySide2.QtWidgets import QToolBar

import sd.api
import sexparser
from sdutils import app, qt_mgr, ui_mgr
from ui.window import MainWindow

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

    def open_sex_window(self, parser: sexparser.NodeCreator):
        self.parser.import_functions("functions.sbs", app)
        self.parser.import_current_graph_functions(app)

        main_sd_window = qt_mgr.getMainWindow()
        graph: sd.api.SDGraph = ui_mgr.getCurrentGraph()

        window = MainWindow(main_sd_window, graph)
        window.setWindowTitle(f"Expression Editor: {graph.getIdentifier()}")
        window.show()

        src: str
        graph_objects = graph.getGraphObjects()

        found_snippet = False

        for i in range(graph_objects.getSize()):
            graph_object = graph_objects.getItem(i)
            
            if isinstance(graph_object, sd.api.SDGraphObjectFrame) and graph_object.getTitle() == "snippet":
                found_snippet = True
                graph_object: sd.api.SDGraphObjectFrame
                src = graph_object.getDescription()
                window.ui.code_editor.setPlainText(src)
                window.frame_object = graph_object

                window.save_source(src)

        if not found_snippet:
            user_data_string = graph.getAnnotationPropertyValueFromId("userdata")
            if window.plugin_settings["use_snippet_object"] or user_data_string is None:
                new_frame_object = sd.api.SDGraphObjectFrame.sNew(graph)

                new_frame_object.setTitle("snippet")
                new_frame_object.setPosition(sd.api.sdbasetypes.float2(-sexparser.grid_size * 8.8, -sexparser.grid_size * 0.5))
                new_frame_object.setColor(sd.api.sdbasetypes.ColorRGBA(0.145, 0.145, 0.145, 1.0))
                new_frame_object.setSize(sd.api.sdbasetypes.float2(sexparser.grid_size * 8, sexparser.grid_size * 20))
                window.frame_object = new_frame_object

            try:
                user_data = json.loads(user_data_string.get())
                src = user_data.get("expression", "")
                window.ui.code_editor.setPlainText(src)
            except ValueError as e:
                pass