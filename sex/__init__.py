from __future__ import annotations

import os
import sys
import ast
import traceback
import json

from functools import partial
from time import gmtime, strftime
from PySide2.QtGui import QFont, QIcon
from PySide2.QtWidgets import QApplication, QMainWindow, QToolBar

sys.path.append(os.path.dirname(__file__))

import sd
import sd.api
import sexeditor
import sexparser
import sexsyntax
import jinja2

from sd.api.sdproperty import SDPropertyCategory
from astutils import SexAstTransfomer

ctx = sd.getContext()
app = ctx.getSDApplication()
ui_mgr = app.getUIMgr()
qt_mgr = app.getQtForPythonUIMgr()

parser = sexparser.NodeCreator()

sd_type_map = {
    "float": sd.api.SDTypeFloat.sNew(),
    "float2": sd.api.SDTypeFloat2.sNew(),
    "float3": sd.api.SDTypeFloat3.sNew(),
    "float4": sd.api.SDTypeFloat4.sNew(),
    "int": sd.api.SDTypeInt.sNew(),
    "int2": sd.api.SDTypeInt2.sNew(),
    "int3": sd.api.SDTypeInt3.sNew(),
    "int4": sd.api.SDTypeInt4.sNew(),
}

class PluginSettings:
    def __init__(self):
        self._json_defaults = \
        """
{
    "window_size": [
        1463,
        952
    ],
    "editor_font_size": 11,
    "console_font_size": 10,
    "tab_font_size": 11,
    "button_font_size": 13,
    "tab_spaces": 4,
    "align_max_nodes": 50,
    "window_pos": [
        233,
        229
    ]
}        
        """
        path = os.path.dirname(os.path.abspath(__file__))
        self.settings_file_path = os.path.join(path, "..", "settings.json")
        self.settings = {}
        self.defaults = json.loads(self._json_defaults)
        self.load()
       
    def __getitem__(self, key):
        if key in self.settings:
            return self.settings[key]
        elif key in self.defaults:
            return self.defaults[key]
        else:
            raise KeyError(f"No setting [{key}]!")

    def __setitem__(self, key, value):
        self.settings[key] = value

    def load(self):
        settings_file_exists = os.path.isfile(self.settings_file_path)
        if settings_file_exists:
            with open(self.settings_file_path) as settings_file:
                self.settings = json.load(settings_file)

    def save(self):
        settings_to_save = self.defaults.copy()
        settings_to_save.update(self.settings)
        with open(self.settings_file_path, "w") as settings_file:
            json.dump(settings_to_save, settings_file, indent=4)
    

class MainWindow(QMainWindow):

    def __init__(self, parent=None, graph=None):
        super(MainWindow, self).__init__(parent)
        plugin_settings = PluginSettings()
        self.plugin_settings = plugin_settings
        self.graph: sd.api.SDGraph = graph
        self.ui = sexeditor.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.code_editor.setup_editor(plugin_settings["editor_font_size"])
        self.ui.render_view.setup_editor(plugin_settings["editor_font_size"])
        self.ui.code_editor.tab_spaces = plugin_settings["tab_spaces"]
        button_font = self.ui.compile.font()
        button_font.setPointSize(plugin_settings["button_font_size"])
        self.ui.compile.setFont(button_font)

        tab_font = self.ui.tabs.font()
        tab_font.setPointSize(plugin_settings["tab_font_size"])
        self.ui.tabs.setFont(tab_font)

        # tab_font = self.ui.render_tab.font()
        # tab_font.setPointSize(plugin_settings["tab_font_size"])
        # self.ui.render_tab.setFont(tab_font)


        self.ui.compile.clicked.connect(self.create_nodes)
        self.ui.tabs.currentChanged.connect(self.tab_change)
        self.ui.code_editor.init_code_completion(parser.keywords + self.get_package_inputs())
        self.frame_object: sd.api.SDGraphObjectFrame = None
       
        self.highlighter = sexsyntax.SexHighlighter(self.ui.code_editor.document())
        self.view_highlighter = sexsyntax.SexHighlighter(self.ui.render_view.document())

        font = QFont("Courier New")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(plugin_settings["console_font_size"])
        self.ui.console_output.setFont(font)
        self.ui.console_output.setReadOnly(True)

        font = QFont("Courier New")
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
        
       

        builtin_functions = ([*sexparser.function_node_map]
                             + [*sexparser.vectors_map]
                             + [*parser.imported_functions]
                             + [*sexparser.samplers_map]
                             + ["range"])

        builtin_types = [*sexparser.constants_map] + [*sexparser.get_variable_map] + [*sexparser.casts_map]

        self.highlighter.setup_rules(builtin_functions, builtin_types)
        self.view_highlighter.setup_rules(builtin_functions, builtin_types)
        self.setWindowTitle("Expression Editor")

    def get_package_inputs(self):
        result = set()

        pkg = self.graph.getPackage()
        pkg_resources = pkg.getChildrenResources(True)

        res: sd.api.SDResource
        for res in pkg_resources:
            res_inputs = res.getProperties(sd.api.sdproperty.SDPropertyCategory.Input)

            res_input: sd.api.SDProperty
            for res_input in res_inputs:
                res_input_id = res_input.getId()

                if res_input_id[0] != "$":
                    result.add(res_input_id)

        return list(result)

    def closeEvent(self, event):
        self.plugin_settings["window_size"] = [self.width(), self.height()]
        self.plugin_settings["window_pos"] = [self.pos().x(), self.pos().y()]
        self.plugin_settings.save()

    def indent_fix(self, src: str) -> str:
        lines = src.splitlines()
        indent = " " * self.ui.code_editor.tab_spaces
        current_ident = ""
        for index, line in enumerate(lines):
            if current_ident and line and not line.startswith(" "):
                current_ident = ""

            line = current_ident + line.lstrip()
            lines[index] = line
            
            if line.lstrip().startswith("def "):
                current_ident = indent
                continue


        return "\n".join(lines)


    def tab_change(self, tab_index):
        if tab_index == 1:
            src = self.ui.code_editor.toPlainText()
            try:
                src = self.get_rendered_code(src)
            except jinja2.TemplateError as e:
                self.console_message(str(e))
                return
            
            stripped_src = self.indent_fix(src)
            self.ui.render_view.setPlainText(stripped_src)


    def get_rendered_code(self, code):
        package_file = self.graph.getPackage().getFilePath()
        package_dir = os.path.dirname(package_file)

        jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(package_dir))

        jenv.lstrip_blocks = True
        jenv.trim_blocks = True
        jenv.line_statement_prefix = "::"

        src_template = jenv.from_string(code)
        return src_template.render()



    def console_message(self, message):
        timestamp = strftime("[%H:%M:%S] ", gmtime())
        self.ui.console_output.appendPlainText(timestamp + message)
        self.ui.console_output.repaint()

    def save_source(self):
        src = self.ui.code_editor.toPlainText()
        self.frame_object.setDescription(src)

    def parse_expression_tree(self, ast_tree):
        parser.graph = self.graph
        parser.main_window = self
        try:
            parser.parse_tree(ast_tree)
        except sexparser.ParserError as err:
            self.console_message(str(err))
        except Exception as err:
            self.console_message("Unhandled exception")
            self.console_message(str(err))
            self.console_message(traceback.format_exc())
        else:
            self.console_message("Nodes are succesfully created")

    def get_package_resource(self, resources: list[sd.api.SDResource], res_id: str) -> sd.api.SDResource:
        return next((res for res in resources if res.getIdentifier() == res_id), None)

    def create_nodes(self):
        self.console_message("Compiling...")
        src = self.ui.code_editor.toPlainText()
        self.frame_object.setDescription(src)

        try:
            src = self.get_rendered_code(src)
        except jinja2.TemplateError as e:
            self.console_message(str(e))
            return
        try:
            stripped_src = self.indent_fix(src)
            ast_tree = ast.parse(stripped_src, mode="exec")
            tree: ast.AST = SexAstTransfomer().visit(ast_tree)
        except SyntaxError as err:
            self.console_message(str(err))
            self.console_message(err.text)
        else:
            self.console_message("Delete current nodes...")
            graph_nodes = self.graph.getNodes()
            for i in range(graph_nodes.getSize()):
                self.graph.deleteNode(graph_nodes.getItem(i))

            self.console_message("Create nodes...")
            self.parse_expression_tree(tree)
            if parser.nodes_num <= self.plugin_settings["align_max_nodes"]:
                self.console_message("Align nodes...")
                parser.align_nodes()
            self.console_message("DONE")

            current_package: sd.api.SDPackage = self.graph.getPackage()
            resources: list[sd.api.SDResource] = current_package.getChildrenResources(True)

            for node in ast.walk(tree):

                if not isinstance(node, ast.FunctionDef):
                    continue

                function_name = node.name

                function_resource = self.get_package_resource(resources, function_name)
                if function_resource is not None:
                    function_resource.delete()

                inputs = {}
                arg: ast.arg
                for arg in node.args.args:
                    input_name = f"__{function_name}_arg_{arg.arg}"
                    inputs[input_name] = (arg.arg, arg.annotation.id)

                function_graph: sd.api.SDSBSFunctionGraph = sd.api.SDSBSFunctionGraph.sNew(current_package)
                function_graph.setIdentifier(function_name)

                for inp in inputs:
                    var_name, var_type = inputs[inp]
                    prop: sd.api.SDProperty = function_graph.newProperty(inp, sd_type_map[var_type], SDPropertyCategory.Input)
                    function_graph.setPropertyAnnotationValueFromId(prop, "label", sd.api.SDValueString.sNew(var_name))

                parser.graph = function_graph
                parser.parse_tree(node, inputs)


class SexToolBar(QToolBar):
    def __init__(self, graph_view_id, qt_ui_mgr):
        super(SexToolBar, self).__init__(parent=qt_ui_mgr.getMainWindow())

        # Save the graphViewID and uiMgr for later use.
        self.__graph_view_id = graph_view_id
        self.__qt_ui_mgr = qt_ui_mgr

        # Add actions to our toolbar.
        act = self.addAction("Expression")
        act.setToolTip("Open expression editor")
        act.triggered.connect(self.open_sex_window)

    def open_sex_window(self):
        parser.import_functions("functions.sbs", app)
        parser.import_current_graph_functions(app)

        main_sd_window = qt_mgr.getMainWindow()
        graph = ui_mgr.getCurrentGraph()

        window = MainWindow(main_sd_window, graph)
        window.show()

        src: str
        graph_objects = graph.getGraphObjects()

        for i in range(graph_objects.getSize()):
            graph_object = graph_objects.getItem(i)
            
            if isinstance(graph_object, sd.api.SDGraphObjectFrame):
                graph_object: sd.api.SDGraphObjectFrame
                src = graph_object.getDescription()
                window.ui.code_editor.setPlainText(src)
                window.frame_object = graph_object

        if graph_objects.getSize() == 0:
            graph = ui_mgr.getCurrentGraph()
            new_frame_object = sd.api.SDGraphObjectFrame.sNew(graph)

            new_frame_object.setTitle("snippet")
            new_frame_object.setPosition(sd.api.sdbasetypes.float2(-sexparser.grid_size * 8.8, -sexparser.grid_size * 0.5))
            new_frame_object.setColor(sd.api.sdbasetypes.ColorRGBA(0.145, 0.145, 0.145, 1.0))
            new_frame_object.setSize(sd.api.sdbasetypes.float2(sexparser.grid_size * 8, sexparser.grid_size * 20))
            window.frame_object = new_frame_object

def onNewGraphViewCreated(graph_view_id, qt_ui_mgr: sd.api.qtforpythonuimgrwrapper.QtForPythonUIMgrWrapper):
    # Create our toolbar.
    toolbar = SexToolBar(graph_view_id, qt_ui_mgr)

    # Add our toolbar to the graph widget.
    created_graph = qt_ui_mgr.getGraphFromGraphViewID(graph_view_id)
    path = os.path.dirname(os.path.abspath(__file__))
    icon = QIcon(os.path.join(path, "ie-icon.png"))

    if isinstance(created_graph, sd.api.SDSBSFunctionGraph):
        qt_ui_mgr.addToolbarToGraphView(
            graph_view_id,
            toolbar,
            icon = icon,
            tooltip = "Expression Editor")

def initializeSDPlugin():
    qt_mgr.registerGraphViewCreatedCallback(partial(onNewGraphViewCreated, qt_ui_mgr = qt_mgr))
