from __future__ import annotations

import os
import ast
import json
import traceback
import jinja2
from time import gmtime, strftime

from PySide2.QtGui import QFont
from PySide2.QtWidgets import QMainWindow, QApplication

import sd.api
import ui.sexeditor as sexeditor
import sexsyntax
import sexparser
import sdutils as sdu

from sdutils import app

from astutils import SexAstTransfomer
from sd.api.sdproperty import SDPropertyCategory
from sexparser import NODE_PROPERTY_DECORATOR, FXMAP_PROPERTY_DECORATOR, PIXEL_PROCESSOR_DECORATOR, VALUE_PROCESSOR_DECORATOR
import sex
from sex.settings import PluginSettings

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

    
class FunctionDecorator:
    def __init__(self) -> None:
        self.args: dict = {}

def parse_decorators(decorator_list: list[ast.AST]) -> dict[str, FunctionDecorator]:
    result: dict[str, FunctionDecorator] = {}    

    for decorator in decorator_list:

        if isinstance(decorator, ast.Name):
            result[decorator.id] = FunctionDecorator()
            continue

        if isinstance(decorator, ast.Call):
            d = FunctionDecorator()
            keyword: ast.keyword
            for keyword in decorator.keywords:
                key = keyword.arg
                d.args[key] = None

                if isinstance(keyword.value, ast.Num):
                    d.args[key] = keyword.value.n

                if isinstance(keyword.value, ast.Str):
                    d.args[key] = keyword.value.s
            
            result[decorator.func.id] = d
            continue

    return result

class MainWindow(QMainWindow):

    def __init__(self, parent=None, graph=None):
        super(MainWindow, self).__init__(parent)
        plugin_settings = PluginSettings()
        self.plugin_settings = plugin_settings
        self.graph: sd.api.SDGraph = graph
        self.ui = sexeditor.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.code_editor.setup_editor(plugin_settings["font"], plugin_settings["editor_font_size"])
        self.ui.render_view.setup_editor(plugin_settings["font"], plugin_settings["editor_font_size"])
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
        self.ui.code_editor.init_code_completion(sex.parser.keywords + self.get_package_inputs())
        self.frame_object: sd.api.SDGraphObjectFrame = None
       
        self.highlighter = sexsyntax.SexHighlighter(self.ui.code_editor.document())
        self.view_highlighter = sexsyntax.SexHighlighter(self.ui.render_view.document())

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
        
       

        builtin_functions = ([*sexparser.function_node_map]
                             + [*sexparser.vectors_map]
                             + [*sex.parser.imported_functions]
                             + [*sexparser.samplers_map]
                             + ["range"])

        builtin_types = ([*sexparser.constants_map] + [*sexparser.get_variable_map] 
            + [*sexparser.casts_map] + [PIXEL_PROCESSOR_DECORATOR, VALUE_PROCESSOR_DECORATOR, NODE_PROPERTY_DECORATOR, FXMAP_PROPERTY_DECORATOR])

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
        self.ui.console_output.appendHtml(timestamp + message)
        self.ui.console_output.repaint()

    def save_source(self, src):
        user_data = {"expression": src}
        user_data_property: sd.api.SDProperty = self.graph.getPropertyFromId("userdata", SDPropertyCategory.Annotation)
        if user_data_property is not None:
            self.graph.setPropertyValue(user_data_property, sdu.sd_value(json.dumps(user_data)))

        if self.frame_object is not None:
            self.frame_object.setDescription(src)

    def parse_expression_tree(self, ast_tree, inputs: dict = None):
        try:
            sex.parser.parse_tree(ast_tree, inputs)
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

    def get_package_compgraph(self, resources: list[sd.api.SDResource], res_id: str) -> sd.api.SDSBSCompGraph:
        return next((res for res in resources if res.getIdentifier() == res_id and res.getType().getId() == sdu.comp_graph_class), None)

    def get_package_functiongraph(self, resources: list[sd.api.SDResource], res_id: str) -> sd.api.SDSBSFunctionGraph:
        return next((res for res in resources if res.getIdentifier() == res_id and res.getType().getId() == sdu.function_graph_class), None)

    def create_nodes(self):
        self.console_message("Compiling...")

        src = self.ui.code_editor.toPlainText()
        self.save_source(src)

        sex.parser.main_window = self

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
            current_package: sd.api.SDPackage = self.graph.getPackage()
            resources: list[sd.api.SDResource] = current_package.getChildrenResources(True)

            for node in ast.walk(tree):

                if not isinstance(node, ast.FunctionDef):
                    continue

                function_name = node.name

                
                function_graph: sd.api.SDSBSFunctionGraph = None
                inputs_node: sd.api.SDNode = None

                decorators = parse_decorators(node.decorator_list)

                use_node_inputs = False

                if PIXEL_PROCESSOR_DECORATOR in decorators:
                    decorator = decorators[PIXEL_PROCESSOR_DECORATOR]
                    graph = self.get_package_compgraph(resources, decorator.args["graph"])
                    pp_node = sdu.get_graph_node(graph, uid=decorator.args["uid"])
                    prop = sdu.get_node_input(pp_node, "perpixel")
                    function_graph = pp_node.newPropertyGraph(prop, sdu.function_graph_class)
                    inputs_node = pp_node
                    use_node_inputs = True

                if VALUE_PROCESSOR_DECORATOR in decorators:
                    decorator = decorators[VALUE_PROCESSOR_DECORATOR]
                    graph = self.get_package_compgraph(resources, decorator.args["graph"])
                    vp_node = sdu.get_graph_node(graph, uid=decorator.args["uid"])
                    prop = sdu.get_node_input(vp_node, "function")
                    function_graph = vp_node.newPropertyGraph(prop, sdu.function_graph_class)
                    inputs_node = vp_node
                    use_node_inputs = True

                if NODE_PROPERTY_DECORATOR in decorators:
                    decorator = decorators[NODE_PROPERTY_DECORATOR]
                    graph = self.get_package_compgraph(resources, decorator.args["graph"])
                    comp_node = sdu.get_graph_node(graph, uid=decorator.args["uid"])

                    prop: sd.api.SDProperty = None
                    if "pid" in decorator.args:
                        prop = sdu.get_node_input(comp_node, decorator.args["pid"])

                    function_graph = comp_node.newPropertyGraph(prop, sdu.function_graph_class)
                    inputs_node = None


                if function_graph is None:
                    function_resource = self.get_package_functiongraph(resources, function_name)
                    function_graph = function_resource
                    if function_graph is None:
                        function_graph: sd.api.SDSBSFunctionGraph = sd.api.SDSBSFunctionGraph.sNew(current_package)
                        function_graph.setIdentifier(function_name)

                    inputs_node = function_graph
                    function_inputs = function_graph.getProperties(SDPropertyCategory.Input)

                    for finp in function_inputs:
                        function_graph.deleteProperty(finp)

                    for graph_node in function_graph.getNodes():
                        function_graph.deleteNode(graph_node)

                inputs = {}
                if inputs_node is not None:

                    arg: ast.arg
                    for arg in node.args.args:
                        input_name = f"__{function_name}_arg_{arg.arg}" if not use_node_inputs else f"#{arg.arg}"
                        inputs[input_name] = (arg.arg, arg.annotation.id)

                    for inp in inputs:
                        if use_node_inputs:
                            node_inputs = inputs_node.getProperties(SDPropertyCategory.Input)
                            for ni in node_inputs:
                                if ni.getId().startswith("#"):
                                    inputs_node.deleteProperty(ni)
                        var_name, var_type = inputs[inp]
                        prop: sd.api.SDProperty = inputs_node.newProperty(inp, sd_type_map[var_type], SDPropertyCategory.Input)
                        if not use_node_inputs:
                            inputs_node.setPropertyAnnotationValueFromId(prop, "label", sd.api.SDValueString.sNew(var_name))

                sex.parser.graph = function_graph
                self.parse_expression_tree(node, inputs)

            sex.parser.import_current_graph_functions(app)

            self.console_message("Delete current nodes...")
            sex.parser.graph = self.graph
            graph_nodes = self.graph.getNodes()
            for i in range(graph_nodes.getSize()):
                self.graph.deleteNode(graph_nodes.getItem(i))

            self.console_message("Create nodes...")
            self.parse_expression_tree(tree)
            if sex.parser.nodes_num <= self.plugin_settings["align_max_nodes"]:
                self.console_message("Align nodes...")
                sex.parser.align_nodes()
            self.console_message("<b><font color=\"lime\">DONE!</font></b>")