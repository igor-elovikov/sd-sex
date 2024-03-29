import ast
import imp
import re
import os

import sd
import sd.api
from sd.api.sdbasetypes import float2

grid_size = 1.4 * sd.ui.graphgrid.GraphGrid.sGetFirstLevelSize()
max_nodes_in_row = 20

output_id = "unique_filter_output"
output_variable_name = "_OUT_"
export_function_name = "export"
setvar_function_name = "setvar"
sequence_function_name = "sequence"
declare_inputs_function_name = "declare_inputs"

binary_operator_map = {
    ast.Add: "sbs::function::add",
    ast.Sub: "sbs::function::sub",
    ast.Mult: "sbs::function::mul",
    ast.Div: "sbs::function::div",
    ast.Mod: "sbs::function::mod",
    ast.MatMult: "sbs::function::mulscalar",
    ast.BitXor: "sbs::function::dot"
}

unary_operator_map = {
    ast.Not: "sbs::function::not",
    ast.USub: "sbs::function::neg"
}

bool_operator_map = {
    ast.And: "sbs::function::and",
    ast.Or: "sbs::function::or"
}

compare_operator_map = {
    ast.Gt: "sbs::function::gt",
    ast.GtE: "sbs::function::gteq",
    ast.Lt: "sbs::function::lr",
    ast.LtE: "sbs::function::lreq",
    ast.Eq: "sbs::function::eq",
    ast.NotEq: "sbs::function::noteq",
}

samplers_map = {
    "samplelum": "sbs::function::samplelum",
    "samplecol": "sbs::function::samplecol",
}

function_node_map = {
    "abs": ("sbs::function::abs", ["a"]),
    "floor": ("sbs::function::floor", ["a"]),
    "ceil": ("sbs::function::ceil", ["a"]),
    "cos": ("sbs::function::cos", ["a"]),
    "sin": ("sbs::function::sin", ["a"]),
    "tan": ("sbs::function::tan", ["a"]),
    "atan2": ("sbs::function::atan2", ["a"]),
    "cartesian": ("sbs::function::cartesian", ["rho", "theta"]),
    "sqrt": ("sbs::function::sqrt", ["a"]),
    "log": ("sbs::function::log", ["a"]),
    "exp": ("sbs::function::exp", ["a"]),
    "log2": ("sbs::function::log2", ["a"]),
    "pow2": ("sbs::function::pow2", ["a"]),
    "lerp": ("sbs::function::lerp", ["a", "b", "x"]),
    "min": ("sbs::function::min", ["a", "b"]),
    "max": ("sbs::function::max", ["a", "b"]),
    "rand": ("sbs::function::rand", ["a"]),
    "dot": ("sbs::function::dot", ["a", "b"]),
}

constants_map = {
    "float" : ("sbs::function::const_float1", sd.api.SDValueFloat, float),
    "float2" : ("sbs::function::const_float2", sd.api.SDValueFloat2, sd.api.sdbasetypes.float2),
    "float3" : ("sbs::function::const_float3", sd.api.SDValueFloat3, sd.api.sdbasetypes.float3),
    "float4" : ("sbs::function::const_float4", sd.api.SDValueFloat4, sd.api.sdbasetypes.float4),
    "int" : ("sbs::function::const_int1", sd.api.SDValueInt, int),
    "int2" : ("sbs::function::const_int2", sd.api.SDValueInt2, sd.api.sdbasetypes.int2),
    "int3" : ("sbs::function::const_int3", sd.api.SDValueInt3, sd.api.sdbasetypes.int3),
    "int4" : ("sbs::function::const_int4", sd.api.SDValueInt4, sd.api.sdbasetypes.int4)
}

vectors_map = {
    "vector2" : "sbs::function::vector2",
    "vector3" : "sbs::function::vector3",
    "vector4" : "sbs::function::vector4",
    "ivector2" : "sbs::function::ivector2",
    "ivector3" : "sbs::function::ivector3",
    "ivector4" : "sbs::function::ivector4"
}

get_variable_map = {
    "get_float" : "sbs::function::get_float1",
    "get_float2" : "sbs::function::get_float2",
    "get_float3" : "sbs::function::get_float3",
    "get_float4" : "sbs::function::get_float4",
    "get_int" : "sbs::function::get_integer1",
    "get_int2" : "sbs::function::get_integer2",
    "get_int3" : "sbs::function::get_integer3",
    "get_int4" : "sbs::function::get_integer4",
    "get_bool" : "sbs::function::get_bool",
    "get_string" : "sbs::function::get_string"
}

sd_types_node_map = {
    sd.api.SDTypeFloat: "sbs::function::get_float1",
    sd.api.SDTypeFloat2 : "sbs::function::get_float2",
    sd.api.SDTypeFloat3 : "sbs::function::get_float3",
    sd.api.SDTypeFloat4 : "sbs::function::get_float4",
    sd.api.SDTypeInt : "sbs::function::get_integer1",
    sd.api.SDTypeInt2 : "sbs::function::get_integer2",
    sd.api.SDTypeInt3 : "sbs::function::get_integer3",
    sd.api.SDTypeInt4 : "sbs::function::get_integer4",
    sd.api.SDTypeBool : "sbs::function::get_bool",
    sd.api.SDTypeString : "sbs::function::get_string"
}

casts_map = {
    "tofloat" : "sbs::function::tofloat",
    "tofloat2" : "sbs::function::tofloat2",
    "tofloat3" : "sbs::function::tofloat3",
    "tofloat4" : "sbs::function::tofloat4",
    "toint" : "sbs::function::toint1",
    "toint2" : "sbs::function::toint2",
    "toint3" : "sbs::function::toint3",
    "toint4" : "sbs::function::toint4"
}

float_components_map = {
    "x" : 0,
    "y" : 1,
    "z" : 2,
    "w" : 3
}

int_components_map = {
    "a" : 0,
    "b" : 1,
    "c" : 2,
    "d" : 3
}

sd_integer_vector_types = {
    1 : (sd.api.SDValueInt, int),
    2 : (sd.api.SDValueInt2, sd.api.sdbasetypes.int2),
    3 : (sd.api.SDValueInt3, sd.api.sdbasetypes.int3),
    4 : (sd.api.SDValueInt4, sd.api.sdbasetypes.int4)
}

class ParserError(Exception):
    pass

def check_operator_types(op):
    def wrapper(parser, operator) -> sd.api.SDNode:
        node: sd.api.SDNode = op(parser, operator)
        node_definition = node.getDefinition().getId() if node else ""

        # can't check swizzling (something wrong with connection types)
        is_swizzling_node = "sbs::function::swizzle" in node_definition or "sbs::function::iswizzle" in node_definition or "sbs::function::sequence" in node_definition
        if node and not is_swizzling_node:
            node_inputs = node.getProperties(sd.api.sdproperty.SDPropertyCategory.Input)

            n_input: sd.api.SDProperty
            for input_index, n_input in enumerate(node_inputs):

                if n_input.isConnectable():
                    input_connections = node.getPropertyConnections(n_input)
                    if len(input_connections):
                        prop_connection: sd.api.SDConnection = input_connections[0]
                        in_type = prop_connection.getInputProperty().getType().getId()
                        out_type = prop_connection.getOutputProperty().getType().getId()
                        if in_type != out_type:
                            parser._error(f"Type mismatch for parameter [{input_index + 1}]: {out_type} was expected ({in_type} was received)", operator)
        return node

    return wrapper   


class NodeCreator:
    def __init__(self, graph: sd.api.SDGraph=None):
        self.var_scope = {}
        self.var_declare_line = {}
        self.inputs_vars = []
        self.export_vars = []
        self.node_pos_x = grid_size * 4
        self.node_pos_y = -grid_size * 4
        self.imported_functions = {}
        self.current_graph_functions = []
        self.graph = graph
        self.keywords = []
        self.keywords += function_node_map.keys()
        self.keywords += constants_map.keys()
        self.keywords += vectors_map.keys()
        self.keywords += get_variable_map.keys()
        self.keywords += casts_map.keys()
        self.keywords += samplers_map.keys()
        self.keywords.append(output_variable_name)
        self.keywords.append(export_function_name)
        self.keywords.append(declare_inputs_function_name)
        self.keywords.append("True")
        self.keywords.append("False")
        self.main_window = None
        self.nodes_num = 0
        self.align_queue = []

    def _reset(self):
        self.node_pos_x = 0
        self.node_pos_y = 0
        self.nodes_num = 0
        self.var_scope = {}
        self.export_vars = []

    def _error(self, message: str, operator: ast.Expr):
        raise ParserError(f"[line {operator.lineno}: col {operator.col_offset}] ERROR: {message}")

    def get_package_functions(self, sd_package: sd.api.SDPackage, to_lower_case = False):
        functions = sd_package.getChildrenResources(True)
        sd_resource: sd.api.SDResource

        imported_functions = {}

        for i in range(functions.getSize()):
            sd_resource = functions.getItem(i)
            res_id = sd_resource.getIdentifier()
            res_type = sd_resource.getType().getId()

            if res_type == "SDSBSFunctionGraph":
                if to_lower_case:
                    func_name = res_id.lower()
                else:
                    func_name = res_id
                func_name = re.sub(r"[-(),.[\]]", "", func_name)
                if func_name[0].isdigit():
                    func_name = "_" + func_name

                props = sd_resource.getProperties(sd.api.sdproperty.SDPropertyCategory.Input)
                props_list = []

                if props.getSize() > 0:
                    props_list = [props.getItem(i).getId() for i in range(props.getSize())]

                #print((res_id, func_name, props_list))

                imported_functions[func_name] = (sd_resource, props_list)

                if not func_name in self.keywords:
                    self.keywords.append(func_name)

        return imported_functions

    def import_current_graph_functions(self, sd_app: sd.api.SDApplication):
        pkg_mgr = sd_app.getPackageMgr()

        self.keywords = [key for key in self.keywords if key not in self.current_graph_functions]

        user_packages = pkg_mgr.getUserPackages()
        self.current_graph_functions = []

        package: sd.api.SDPackage
        for package in user_packages:
            package_functions = self.get_package_functions(package)
            self.current_graph_functions.extend([*package_functions])
            self.imported_functions.update(package_functions)

    def import_functions(self, package_name: str, sd_app: sd.api.SDApplication):
        package_mgr = sd_app.getPackageMgr()
        loaded_packages = package_mgr.getPackages()
        
        functions_package: sd.api.SDPackage = None
        for i in range(loaded_packages.getSize()):
            package: sd.api.SDPackage = loaded_packages.getItem(i)
            if package_name in package.getFilePath():
                functions_package = package

        
        if functions_package is None:
            resource_path = sd_app.getPath(sd.api.sdapplication.SDApplicationPath.DefaultResourcesDir)
            package_path = os.path.join(resource_path, "packages", package_name)
            functions_package = package_mgr.loadUserPackage(package_path)

        self.imported_functions.update(self.get_package_functions(functions_package, to_lower_case=True))
       

    def declare_inputs(self, graph_id: str):
        pkg: sd.api.SDPackage = self.graph.getPackage()

        pkg_resources = pkg.getChildrenResources(True)

        resource: sd.api.SDResource
        inputs_graph: sd.api.SDGraph = None
        
        for resource in pkg_resources:
            if resource.getIdentifier() == graph_id and isinstance(resource, sd.api.SDGraph):
                inputs_graph = resource

        if inputs_graph is None:
            return False
        
        inputs = inputs_graph.getProperties(sd.api.sdproperty.SDPropertyCategory.Input)

        prop: sd.api.SDProperty
        for prop in inputs:
            prop_type = prop.getType()
            prop_id = prop.getId()

            if type(prop_type) in sd_types_node_map and prop_id[0] != "$":
                input_node = self.create_graph_node(sd_types_node_map[type(prop_type)])
                input_node.setInputPropertyValueFromId("__constant__", sd.api.SDValueString.sNew(prop_id))
                self.var_scope[prop_id] = input_node
                self.inputs_vars.append(prop_id)

        return True

    def set_new_node_position(self, node: sd.api.SDNode):
        node.setPosition(float2(self.node_pos_x, self.node_pos_y))        
        self.node_pos_y += grid_size
        if self.node_pos_y >= grid_size * max_nodes_in_row:
            self.node_pos_x += grid_size 
            self.node_pos_y = 0


    def create_graph_node(self, graph_node_definition: str) -> sd.api.SDNode:
        graph_node = self.graph.newNode(graph_node_definition)
        self.set_new_node_position(graph_node)
        self.nodes_num += 1
        return graph_node

    def add_node_to_aligh_queue(self, node: sd.api.SDNode, queue_index: int):

        node_id = node.getIdentifier()
        for i in range(len(self.align_queue)):
            n: sd.api.SDNode
            self.align_queue[i] = [n for n in self.align_queue[i] if n.getIdentifier() != node_id]

        if queue_index == len(self.align_queue):
            node_queue = []
            self.align_queue.append(node_queue)
        else:
            node_queue = self.align_queue[queue_index]

        node_queue.append(node)
        node_inputs = node.getProperties(sd.api.sdproperty.SDPropertyCategory.Input)
        pr: sd.api.SDProperty
        for pr in node_inputs:
            if pr.isConnectable():
                pr_connections = node.getPropertyConnections(pr)
                if len(pr_connections):
                    node_connection: sd.api.SDConnection = pr_connections[0]
                    input_node: sd.api.SDNode = node_connection.getInputPropertyNode()
                    self.add_node_to_aligh_queue(input_node, queue_index + 1)


    def align_nodes(self):
        nodes = self.graph.getNodes()
        self.align_queue.clear()

        node: sd.api.SDNode
        output_nodes = self.graph.getOutputNodes()
        output_node_id = ""
        if len(output_nodes):
            output_node: sd.api.SDNode = output_nodes[0]
            output_node_id = output_node.getIdentifier()
        
        for node in nodes:
            out_property: sd.api.SDProperty = node.getPropertyFromId(output_id, sd.api.sdproperty.SDPropertyCategory.Output)
            is_output_connected = False
            if out_property:
                out_connections = node.getPropertyConnections(out_property)
                if len(out_connections):
                    is_output_connected = True

            is_output_node = node.getIdentifier() == output_node_id
            if (not isinstance(node, sd.api.SDGraphObject) and not is_output_connected) or is_output_node:
                self.add_node_to_aligh_queue(node, 0)

        self.align_queue = [l for l in self.align_queue if len(l)]

        max_rows = len(max(self.align_queue, key = lambda l: len(l)))
        grid_size_h = grid_size * 1.3

        graph_height = max_rows * grid_size
        graph_width = len(self.align_queue) * grid_size_h

        for col_index, col_nodes in enumerate(self.align_queue):
            col_x = graph_width - (col_index + 1) * grid_size_h
            col_y = graph_height / 2.0  - len(col_nodes) / 2.0 * grid_size

            for row_index, node in enumerate(col_nodes):
                node.setPosition(float2(col_x, col_y + row_index * grid_size))


    def create_graph_node_from_resource(self, resource: sd.api.SDResource) -> sd.api.SDNode:
        graph_node = self.graph.newInstanceNode(resource)
        self.set_new_node_position(graph_node)
        return graph_node

    def parse_swizzling(self, operator: ast.Attribute) -> sd.api.SDNode:
        num_components = len(operator.attr)
        if num_components > 4:
            self._error(f"Swizzling supports up to 4 components ({num_components} given: .{operator.attr})", operator)

        float_components_found = all((c in float_components_map.keys()) for c in operator.attr)
        int_components_found = all((c in int_components_map.keys()) for c in operator.attr)

        if not float_components_found and not int_components_found:
            self._error(f"Unsupported components in swizzling (.{operator.attr})", operator)

        if float_components_found:
            node = self.create_graph_node(f"sbs::function::swizzle{num_components}")
            components_mask = [float_components_map[c] for c in operator.attr]
            sd_value_type, sd_base_type = sd_integer_vector_types[num_components]
            node.setInputPropertyValueFromId("__constant__", sd_value_type.sNew(sd_base_type(*components_mask)))
            return node

        if int_components_found:
            node = self.create_graph_node(f"sbs::function::iswizzle{num_components}")
            components_mask = [int_components_map[c] for c in operator.attr]
            sd_value_type, sd_base_type = sd_integer_vector_types[num_components]
            node.setInputPropertyValueFromId("__constant__", sd_value_type.sNew(sd_base_type(*components_mask)))
            return node            


    def parse_vector(self, operator: ast.Call) -> sd.api.SDNode:
        func_arguments = operator.args
        if len(func_arguments) != 2:
            self._error("Vector takes only two arguments", operator)
        vector_type = vectors_map[operator.func.id]
        node = self.create_graph_node(vector_type)

        in_node = self.parse_operator(func_arguments[0])
        last_node = self.parse_operator(func_arguments[1])

        in_node.newPropertyConnectionFromId(output_id, node, "componentsin")
        last_node.newPropertyConnectionFromId(output_id, node, "componentslast")

        return node
    
    def parse_value_cast(self, operator: ast.Call) -> sd.api.SDNode:
        func_arguments = operator.args
        if len(func_arguments) != 1:
            self._error(f"{operator.func.id}() takes only one argument ({len(func_arguments)} given)", operator)
        
        value_argument = func_arguments[0]
        node = self.create_graph_node(casts_map[operator.func.id])

        value_node = self.parse_operator(value_argument)
        value_node.newPropertyConnectionFromId(output_id, node, "value")

        return node

    def parse_get_variable(self, operator: ast.Call) -> sd.api.SDNode:
        func_arguments = operator.args

        if len(func_arguments) != 1:
            self._error("get_variable() has only one srting argument", operator)

        if not isinstance(func_arguments[0], ast.Str):
            self._error("get_variable() argument has to be string", operator)

        arg: ast.Str = func_arguments[0]
        node = self.create_graph_node(get_variable_map[operator.func.id])
        node.setInputPropertyValueFromId("__constant__", sd.api.SDValueString.sNew(arg.s))

        return node

    def parse_constant(self, operator: ast.Call) -> sd.api.SDNode:
        constant_type = operator.func.id
        (constant_node_definition, constant_sd_type, constant_sd_value) = constants_map[constant_type]

        num_components = int(constant_node_definition[-1:])
        func_arguments = operator.args

        arg_values = []

        if num_components != len(func_arguments):
            self._error(f"{constant_type}() takes {num_components} arguments ({len(func_arguments)} given)", operator)
        else:
            for arg in func_arguments:
                if not isinstance(arg, ast.Num):
                    self._error(f"{constant_type}() takes only const arguments", operator)
                else:
                    arg: ast.Num
                    arg_values.append(arg.n)

        
        constant_node = self.create_graph_node(constant_node_definition)
        constant_node.setInputPropertyValueFromId("__constant__", constant_sd_type.sNew(constant_sd_value(*arg_values)))
        return constant_node

    def parse_binary_operator(self, operator: ast.BinOp) -> sd.api.SDNode:
        if type(operator.op) in binary_operator_map:

            operator_node = self.create_graph_node(binary_operator_map[type(operator.op)])
            left_node = self.parse_operator(operator.left)
            right_node = self.parse_operator(operator.right)
            
            left_node.newPropertyConnectionFromId(output_id, operator_node, "a")
            right_input = "b"
            if isinstance(operator.op, ast.MatMult):
                right_input = "scalar"
            right_node.newPropertyConnectionFromId(output_id, operator_node, right_input)

            return operator_node

    def parse_unary_operator(self, operator: ast.UnaryOp) -> sd.api.SDNode:
        if type(operator.op) in unary_operator_map:
            node = self.create_graph_node(unary_operator_map[type(operator.op)])

            operand_node = self.parse_operator(operator.operand)
            operand_node.newPropertyConnectionFromId(output_id, node, "a")

            return node

    def parse_boolean_operator(self, operator: ast.BoolOp) -> sd.api.SDNode:
        if type(operator.op) in bool_operator_map:
            node = self.create_graph_node(bool_operator_map[type(operator.op)])
            operands = operator.values

            left_node = self.parse_operator(operands[0])
            right_node = self.parse_operator(operands[1])

            left_node.newPropertyConnectionFromId(output_id, node, "a")
            right_node.newPropertyConnectionFromId(output_id, node, "b")

            if len(operands) > 2:
                prev_node = node

                for opi in range(2, len(operands)):
                    operand_node = self.parse_operator(operands[opi])
                    node = self.create_graph_node(bool_operator_map[type(operator.op)])

                    prev_node.newPropertyConnectionFromId(output_id, node, "a")
                    operand_node.newPropertyConnectionFromId(output_id, node, "b")
                                        
                    prev_node = node

            return node

    def parse_ifexpr(self, operator: ast.IfExp) -> sd.api.SDNode:
        node = self.create_graph_node("sbs::function::ifelse")

        body_node = self.parse_operator(operator.body)
        test_node = self.parse_operator(operator.test)
        orelse_node = self.parse_operator(operator.orelse)

        body_node.newPropertyConnectionFromId(output_id, node, "ifpath")
        test_node.newPropertyConnectionFromId(output_id, node, "condition")
        orelse_node.newPropertyConnectionFromId(output_id, node, "elsepath")

        return node

    def parse_compare_operator(self, operator: ast.Compare) -> sd.api.SDNode:
        if len(operator.ops) != 1:
            self._error("Non binary comparisons are not supported", operator)

        if type(operator.ops[0]) in compare_operator_map:
            node = self.create_graph_node(compare_operator_map[type(operator.ops[0])])
            left_node = self.parse_operator(operator.left)
            right_node = self.parse_operator(operator.comparators[0])

            left_node.newPropertyConnectionFromId(output_id, node, "a")
            right_node.newPropertyConnectionFromId(output_id, node, "b")

            return node

    def parse_sampler(self, operator: ast.Call) -> sd.api.SDNode:
        function_name = operator.func.id

        node = self.create_graph_node(samplers_map[function_name])
        if len(operator.args) != 3:
            self._error(f"{function_name}() takes 3 arguments ({len(operator.args)} given)", operator)
        
        pos_node = self.parse_operator(operator.args[0])

        input_image_arg = operator.args[1]
        filter_image_arg = operator.args[2]

        if not isinstance(input_image_arg, ast.Num) or not isinstance(filter_image_arg, ast.Num):
            self._error(f"{function_name}() takes only constants for input image or filter", operator)

        node.setInputPropertyValueFromId("__constant__", sd.api.SDValueInt2.sNew(sd.api.sdbasetypes.int2(input_image_arg.n, filter_image_arg.n)))
        pos_node.newPropertyConnectionFromId(output_id, node, "pos")
        
        return node

    def parse_function_node(self, operator: ast.Call) -> sd.api.SDNode:
        function_name = operator.func.id

        function_sd_definition, input_names = function_node_map[function_name]
        node = self.create_graph_node(function_sd_definition)
        
        if len(operator.args) != len(input_names):
            self._error(f"{function_name}() takes {len(input_names)} arguments ({len(operator.args)} given)", operator)

        for arg, input_name in zip(operator.args, input_names):
            input_node = self.parse_operator(arg)
            input_node.newPropertyConnectionFromId(output_id, node, input_name)

        return node

    def parse_imported_function(self, operator: ast.Call) -> sd.api.SDNode:
        sd_resource, inputs_list = self.imported_functions[operator.func.id]
        node = self.create_graph_node_from_resource(sd_resource)

        if len(operator.args) != len(inputs_list):
            self._error(f"{operator.func.id}() takes {len(inputs_list)} arguments ({len(operator.args)} given)", operator)

        for arg, input_name in zip(operator.args, inputs_list):
            input_node = self.parse_operator(arg)
            input_node.newPropertyConnectionFromId(output_id, node, input_name)

        return node

    @check_operator_types
    def parse_operator(self, operator) -> sd.api.SDNode:
        if isinstance(operator, ast.BinOp):
            return self.parse_binary_operator(operator)

        if isinstance(operator, ast.UnaryOp):
            return self.parse_unary_operator(operator)

        if isinstance(operator, ast.Compare):
            return self.parse_compare_operator(operator)

        if isinstance(operator, ast.BoolOp):
            return self.parse_boolean_operator(operator)

        if isinstance(operator, ast.IfExp):
            return self.parse_ifexpr(operator)
                
        if isinstance(operator, ast.Num):
            operator: ast.Num
            value = operator.n

            if isinstance(value, int):
                node = self.create_graph_node("sbs::function::const_int1")
                node.setInputPropertyValueFromId("__constant__", sd.api.SDValueInt.sNew(value))
                return node
        
            if isinstance(value, float):
                node = self.create_graph_node("sbs::function::const_float1")
                node.setInputPropertyValueFromId("__constant__", sd.api.SDValueFloat.sNew(value))
                return node

        if isinstance(operator, ast.Attribute):
            operator: ast.Attribute
            if isinstance(operator.ctx, ast.Store):
                self._error("Assigning to attributes is not supported", operator)
            name_node = self.parse_operator(operator.value)
            swizzle_node = self.parse_swizzling(operator)
            name_node.newPropertyConnectionFromId(output_id, swizzle_node, "vector")
            return swizzle_node
        
        if isinstance(operator, ast.Name):
            operator: ast.Name
            variable_name = operator.id

            if variable_name in self.var_scope:
                return self.var_scope[variable_name]
            else:
                self._error(f"Variable [{variable_name}] not found", operator)

        if isinstance(operator, ast.NameConstant):
            operator: ast.NameConstant
            value = operator.value
            if value == True or value == False:
                node = self.create_graph_node("sbs::function::const_bool")
                node.setInputPropertyValueFromId("__constant__", sd.api.SDValueBool.sNew(value))
                return node
      
        if isinstance(operator, ast.Call):
            operator: ast.Call
            function_name = operator.func.id

            if function_name in constants_map:
                return self.parse_constant(operator)

            if function_name in vectors_map:
                return self.parse_vector(operator)

            if function_name in get_variable_map:
                return self.parse_get_variable(operator)

            if function_name in samplers_map:
                return self.parse_sampler(operator)

            if function_name in function_node_map:
                return self.parse_function_node(operator)

            if function_name in casts_map:
                return self.parse_value_cast(operator)

            if function_name in self.imported_functions:
                return self.parse_imported_function(operator)

            if function_name == export_function_name:
                node = self.create_graph_node("sbs::function::set")
                function_args = operator.args

                if len(function_args) != 1:
                    self._error(f"{export_function_name}() takes exactly one argument ({len(function_args)} given)", operator)

                if not isinstance(function_args[0], ast.Name):
                    self._error(f"{export_function_name}() takes only variables", operator)

                node_to_export = self.parse_operator(function_args[0])
                var_arg: ast.Name = function_args[0]

                node_to_export.newPropertyConnectionFromId(output_id, node, "value")
                node.setInputPropertyValueFromId("__constant__", sd.api.SDValueString.sNew(var_arg.id))

                self.export_vars.append(node)

                return node
            
            if function_name == declare_inputs_function_name:
                func_arguments = operator.args

                if len(func_arguments) != 1:
                    self._error(f"{declare_inputs_function_name}() has only one srting argument", operator)

                if not isinstance(func_arguments[0], ast.Str):
                    self._error(f"{declare_inputs_function_name}() argument has to be string", operator)

                arg: ast.Str = func_arguments[0]

                if not self.declare_inputs(arg.s):
                    self._error(f"Graph [{arg.s}] not found for {declare_inputs_function_name}()", operator)

                return None

            if function_name == setvar_function_name:
                function_args = operator.args

                if len(function_args) != 2:
                    self._error(f"{setvar_function_name}() takes two arguments ({len(function_args)} given)")

                if not isinstance(function_args[0], ast.Str):
                    self._error(f"{setvar_function_name}() first argument has to be string literal as variable name")

                value_node = self.parse_operator(function_args[1])

                node: sd.api.SDNode = self.create_graph_node("sbs::function::set")
                node.setInputPropertyValueFromId("__constant__", sd.api.SDValueString.sNew(function_args[0].s))
                value_node.newPropertyConnectionFromId(output_id, node, "value")

                return node

            if function_name == sequence_function_name:
                function_args = operator.args

                if len(function_args) != 2:
                    self._error(f"{sequence_function_name}() takes two arguments ({len(function_args)} given)")

                seqin_node = self.parse_operator(function_args[0])
                seqlast_node = self.parse_operator(function_args[1])

                node = self.create_graph_node("sbs::function::sequence")

                seqin_node.newPropertyConnectionFromId(output_id, node, "seqin")
                seqlast_node.newPropertyConnectionFromId(output_id, node, "seqlast")

                return node


            self._error(f"Function {function_name}() not found", operator)


    
    def parse_module(self, expr_tree: ast.Module):
        self._reset()

        expressions = expr_tree.body

        for expr in expressions:
            expr_node = self.parse_operator(expr.value)

            if isinstance(expr, ast.Assign):
                assign_operator: ast.Assign = expr
                variable_name = assign_operator.targets[0].id

                self.var_scope[variable_name] = expr_node
                self.var_declare_line[variable_name] = expr.lineno

                if variable_name == output_variable_name:
                    self.graph.setOutputNode(self.var_scope[variable_name], True)

        output_nodes = self.graph.getOutputNodes()

        if output_nodes.getSize() < 1:
            self._error(f"No {output_variable_name} provided or output type mismatch", expr.value)

        output_node: sd.api.SDNode = output_nodes.getItem(0)

        if len(self.export_vars) > 0:
            sequence_node = self.create_graph_node("sbs::function::sequence")
            
            set_node: sd.api.SDNode = self.export_vars[0]
            set_node.newPropertyConnectionFromId(output_id, sequence_node, "seqin")

            for i in range(1, len(self.export_vars)):
                set_node: sd.api.SDNode = self.export_vars[i]
                set_node.newPropertyConnectionFromId(output_id, sequence_node, "seqlast")
                prev_sequence_node = sequence_node

                sequence_node = self.create_graph_node("sbs::function::sequence")
                prev_sequence_node.newPropertyConnectionFromId(output_id, sequence_node, "seqin")

            output_node.newPropertyConnectionFromId(output_id, sequence_node, "seqlast")
            self.graph.setOutputNode(output_node, False)
            self.graph.setOutputNode(sequence_node, True)

        output_node = self.graph.getOutputNodes()[0]
        created_node: sd.api.SDNode

        # Remove all nodes without output connections (not recursive, just optimize using declare_inputs and unused variables)      
        for created_node in self.graph.getNodes():
            created_node_output = created_node.getPropertyFromId(output_id, sd.api.sdproperty.SDPropertyCategory.Output)
            output_connections = created_node.getPropertyConnections(created_node_output)

            if not (created_node.getIdentifier() == output_node.getIdentifier()) and not output_connections.getSize():

                scope_keys = [key for key, node in self.var_scope.items() 
                    if node.getIdentifier() == created_node.getIdentifier() and key not in self.inputs_vars]

                if scope_keys:
                    node_var_name = scope_keys[0]
                    node_var_line = self.var_declare_line[node_var_name]
                    if self.main_window:
                        self.main_window.console_message(f"Warning: Unused variable [{node_var_name}] (declared at line {node_var_line})")

                self.graph.deleteNode(created_node)
