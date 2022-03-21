from __future__ import annotations

import os
import ast
import json
import traceback
import jinja2

from PySide2.QtWidgets import QGridLayout, QWidget

import sd.api
import sexsyntax
import sexparser
import sdutils as sdu

from sdutils import app

from astutils import SexAstTransfomer
from sd.api.sdproperty import SDPropertyCategory
from sexparser import NODE_PROPERTY_DECORATOR, FXMAP_PROPERTY_DECORATOR, PIXEL_PROCESSOR_DECORATOR, VALUE_PROCESSOR_DECORATOR
import sex

from .codeeditor import CodeEditor
from settings import ExpressionType

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


system_inputs = {
    "$pos": ("__sys_pos", "float2"),
    "$size": ("__sys_size", "float2"),
    "$sizelog2": ("__sys_sizelog2", "float2"),
    "$tiling": ("__sys_tiling", "int"),
    "$time": ("__sys_time", "float"),
    "$depth": ("__sys_depth", "float"),
    "$depthpow2": ("__sys_depthpow2", "float"),
    "$number": ("__sys_number", "float")
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

class EditorTab(QWidget):

    def __init__(self, main_window, graph: sd.api.SDGraph = None, expr_type: ExpressionType = ExpressionType.FUNCTION_GRAPH, parent = None):
        super().__init__(parent)

        self.main_window = main_window
        self.graph = graph
        self.package: sd.api.SDPackage = graph.getPackage()
        self.expr_type: ExpressionType = expr_type

        sex.parser.import_current_graph_functions(app)
        

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        code_editor = CodeEditor()
        settings = main_window.plugin_settings
        self.plugin_settings = settings

        code_editor.setup_editor(settings["font"], settings["editor_font_size"])
        code_editor.init_code_completion(sex.parser.keywords + self.get_package_inputs())
        code_editor.tab_spaces = settings["tab_spaces"]
        
        layout.addWidget(code_editor)

        self.setLayout(layout)
        
        self.source_code: str = ""
        self.code_editor = code_editor

        self.frame_object: sd.api.SDGraphObjectFrame = None
       
        self.highlighter = sexsyntax.SexHighlighter(code_editor.document())

        builtin_functions = ([*sexparser.function_node_map]
                             + [*sexparser.vectors_map]
                             + [*sex.parser.imported_functions]
                             + [*sexparser.samplers_map]
                             + ["range"])

        builtin_types = ([*sexparser.constants_map] + [*sexparser.get_variable_map] 
            + [*sexparser.casts_map] + [PIXEL_PROCESSOR_DECORATOR, VALUE_PROCESSOR_DECORATOR, NODE_PROPERTY_DECORATOR, FXMAP_PROPERTY_DECORATOR])

        self.highlighter.setup_rules(builtin_functions, builtin_types)

    def console_message(self, message):
        self.main_window.console_message(message)

    def get_rendered_code(self, code):
        package_file = self.graph.getPackage().getFilePath()
        package_dir = os.path.dirname(package_file)

        jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(package_dir))

        jenv.lstrip_blocks = True
        jenv.trim_blocks = True
        jenv.line_statement_prefix = "::"

        src_template = jenv.from_string(code)
        return src_template.render()

    def set_source(self, source):
        self.source_code = source
        self.code_editor.setPlainText(self.source_code)
        

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

    def save_source(self):

        if self.expr_type is ExpressionType.FUNCTION_GRAPH:

            user_data = {"expression": self.source_code}
            user_data_property: sd.api.SDProperty = self.graph.getPropertyFromId("userdata", SDPropertyCategory.Annotation)
            if user_data_property is not None:
                self.graph.setPropertyValue(user_data_property, sdu.sd_value(json.dumps(user_data)))

            if self.frame_object is not None:
                self.frame_object.setDescription(self.source_code)

        elif self.expr_type is ExpressionType.PACKAGE:

            pkg: sd.api.SDPackage = self.graph.getPackage()
            pkg_metada: sd.api.SDMetadataDict = pkg.getMetadataDict()
            pkg_metada.setPropertyValueFromId("expression", sdu.sd_value(self.source_code))

        elif self.expr_type is ExpressionType.COMPOSITE_GRAPH:

            graph_metadata: sd.api.SDMetadataDict = self.graph.getMetadataDict()
            graph_metadata.setPropertyValueFromId("expression", sdu.sd_value(self.source_code))

    def indent_fix(self, src: str) -> str:
        lines = src.splitlines()
        indent = " " * self.code_editor.tab_spaces
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


    def parse_expression_tree(self, ast_tree, inputs: dict = None, inputs_graph: sd.api.SDGraph = None):
        try:
            sex.parser.parse_tree(ast_tree, inputs, inputs_graph)
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

    def tab_change(self, tab_index):
        if tab_index == 1:
            src = self.code_editor.toPlainText()
            try:
                src = self.get_rendered_code(src)
            except jinja2.TemplateError as e:
                self.console_message(str(e))
                return
            
            stripped_src = self.indent_fix(src)
            self.render_view.setPlainText(stripped_src)

    def create_nodes(self):
        self.console_message("Compiling...")

        src = self.code_editor.toPlainText()
        self.source_code = src
        self.save_source()

        for sys_var in system_inputs:
            src = src.replace(sys_var, system_inputs[sys_var][0])

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

                self.console_message(f"Compiling function [{function_name}]")

                
                function_graph: sd.api.SDSBSFunctionGraph = None
                inputs_node: sd.api.SDNode = None

                decorators = parse_decorators(node.decorator_list)

                use_node_inputs = False

                if PIXEL_PROCESSOR_DECORATOR in decorators:
                    decorator = decorators[PIXEL_PROCESSOR_DECORATOR]
                    if self.expr_type is ExpressionType.COMPOSITE_GRAPH:
                        graph = self.graph
                    else:
                        graph = self.get_package_compgraph(resources, decorator.args["graph"])
                    pp_node = sdu.get_graph_node(graph, uid=decorator.args["uid"])
                    prop = sdu.get_node_input(pp_node, "perpixel")
                    function_graph = pp_node.newPropertyGraph(prop, sdu.function_graph_class)
                    inputs_node = pp_node
                    use_node_inputs = True

                if VALUE_PROCESSOR_DECORATOR in decorators:
                    decorator = decorators[VALUE_PROCESSOR_DECORATOR]
                    if self.expr_type is ExpressionType.COMPOSITE_GRAPH:
                        graph = self.graph
                    else:
                        graph = self.get_package_compgraph(resources, decorator.args["graph"])

                    vp_node = sdu.get_graph_node(graph, uid=decorator.args["uid"])
                    prop = sdu.get_node_input(vp_node, "function")
                    function_graph = vp_node.newPropertyGraph(prop, sdu.function_graph_class)
                    inputs_node = vp_node
                    use_node_inputs = True

                if NODE_PROPERTY_DECORATOR in decorators:
                    decorator = decorators[NODE_PROPERTY_DECORATOR]
                    if self.expr_type is ExpressionType.COMPOSITE_GRAPH:
                        graph = self.graph
                    else:
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

                    prop: sd.api.SDProperty = None
                    for inp in inputs:
                        if use_node_inputs:
                            node_inputs = inputs_node.getProperties(SDPropertyCategory.Input)
                            
                            need_to_create = True

                            for ni in node_inputs:

                                if ni.getId().startswith("#"):
                                    need_delete = False
                                    ni_name = ni.getId()

                                    if ni_name not in inputs:
                                        need_delete = True
                                    else:
                                        inp_type = type(sd_type_map[inputs[ni_name][1]])
                                        print(f"type: {inp_type}, ni_type: {ni.getType()}")                                        
                                        if not isinstance(ni.getType(), inp_type):
                                            need_delete = True
                                        else:
                                            need_to_create = False
                                            prop = ni

                                    if need_delete:
                                        inputs_node.deleteProperty(ni)
                        var_name, var_type = inputs[inp]
                        if need_to_create:
                            prop: sd.api.SDProperty = inputs_node.newProperty(inp, sd_type_map[var_type], SDPropertyCategory.Input)
                        if not use_node_inputs:
                            inputs_node.setPropertyAnnotationValueFromId(prop, "label", sd.api.SDValueString.sNew(var_name))

                sex.parser.graph = function_graph
                self.parse_expression_tree(node, {**inputs, **system_inputs}, graph)

            if self.expr_type is not ExpressionType.FUNCTION_GRAPH:
                return

            sex.parser.import_current_graph_functions(app)

            self.console_message("Delete current nodes...")
            sex.parser.graph = self.graph
            graph_nodes = self.graph.getNodes()
            for i in range(graph_nodes.getSize()):
                self.graph.deleteNode(graph_nodes.getItem(i))

            self.console_message("Create nodes...")
            self.parse_expression_tree(tree, system_inputs)
            if sex.parser.nodes_num <= self.plugin_settings["align_max_nodes"]:
                self.console_message("Align nodes...")
                sex.parser.align_nodes()
            self.console_message("<b><font color=\"lime\">DONE!</font></b>")    