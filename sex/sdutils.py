from __future__ import annotations

import itertools as it
import ast

import sd
import sd.api
import sexparser
from sd.api.sdproperty import SDPropertyCategory

output_id = "unique_filter_output"
function_graph_class = "SDSBSFunctionGraph"
comp_graph_class = "SDSBSCompGraph"

ctx = sd.getContext()
app = ctx.getSDApplication()
ui_mgr = app.getUIMgr()
pkg_mgr = app.getPackageMgr()

class GraphBuilder:
    def __init__(self, graph: sd.api.SDGraph=None):
        self.node_pos_x = 0#grid_size * 4
        self.node_pos_y = 0#-grid_size * 4
        self.imported_functions = {}
        self.graph = graph
        self.grid_size = 1.4 * sd.ui.graphgrid.GraphGrid.sGetFirstLevelSize()
        self.max_nodes_in_row = 20

    def _reset(self):
        self.node_pos_x = 0
        self.node_pos_y = 0

    def delete_all_nodes(self):
        graph_nodes = self.graph.getNodes()
        for node in graph_nodes:
            self.graph.deleteNode(node)        

    def set_new_node_position(self, node: sd.api.SDNode):
        node.setPosition(sd.api.sdbasetypes.float2(self.node_pos_x, self.node_pos_y))        
        self.node_pos_y += self.grid_size
        if self.node_pos_y >= self.grid_size * self.max_nodes_in_row:
            self.node_pos_x -= self.grid_size 
            self.node_pos_y = 0

    def create_graph_node(self, graph_node_definition: str) -> sd.api.SDNode:
        graph_node = self.graph.newNode(graph_node_definition)
        self.set_new_node_position(graph_node)
        return graph_node

    def create_graph_node_from_resource(self, resource: sd.api.SDResource) -> sd.api.SDNode:
        graph_node = self.graph.newInstanceNode(resource)
        self.set_new_node_position(graph_node)
        return graph_node

class SDValue:
    sd_type_map = {
        (float, 1): (sd.api.SDValueFloat, float),
        (float, 2): (sd.api.SDValueFloat2, sd.api.sdbasetypes.float2),
        (float, 3): (sd.api.SDValueFloat3, sd.api.sdbasetypes.float3),
        (float, 4): (sd.api.SDValueFloat4, sd.api.sdbasetypes.float4),
        (int, 1): (sd.api.SDValueInt, int),
        (int, 2): (sd.api.SDValueInt2, sd.api.sdbasetypes.int2),
        (int, 3): (sd.api.SDValueInt3, sd.api.sdbasetypes.int3),
        (int, 4): (sd.api.SDValueInt4, sd.api.sdbasetypes.int4),
        (str, 1): (sd.api.SDValueString, str),
    }
    
    def __init__(self, value):
        value_len = 1
        if type(value) != str:
            try:
                value_len = len(value)
            except TypeError:
                value = (value,)
            if  value_len > 4:
                raise ValueError("Too many components")
        else:
            value = (value,)

        self.builtin_value = value

        value_type = type(value[0])
        is_all_components_same = all(type(v) == value_type for v in value)
        if not is_all_components_same:
            raise ValueError("Components type mismatch")

        for type_map_key in SDValue.sd_type_map:
            builtin_type, type_len = type_map_key
            if builtin_type == value_type and type_len == value_len:
                sd_value_type, sd_base_type = SDValue.sd_type_map[type_map_key]
                self.sd_value = sd_value_type.sNew(sd_base_type(*value))

def get_node_all_inputs(node: sd.api.SDNode) -> sd.api.SDArray:
    return node.getProperties(SDPropertyCategory.Input)

def get_node_all_outputs(node: sd.api.SDNode) -> sd.api.SDArray:
    return node.getProperties(SDPropertyCategory.Output)

def get_graph_node(graph: sd.api.SDGraph, uid: int) -> sd.api.SDNode:
    return graph.getNodeFromId(str(uid))

def get_node_input(node: sd.api.SDNode, input_id: str) -> sd.api.SDProperty:
    node_inputs = get_node_all_inputs(node)
    p: sd.api.SDProperty
    return next((p for p in node_inputs if p.getId() == input_id), None)

def get_node_all_annotations(node: sd.api.SDNode) -> sd.api.SDArray:
    return node.getProperties(SDPropertyCategory.Annotation)

def get_node_annotation(node: sd.api.SDNode, annotation_id: str) -> sd.api.SDProperty:
    annotations = get_node_all_annotations(node)
    a: sd.api.SDProperty
    return next((a for a in annotations if a.getId() == annotation_id), None)

def get_node_annotation_value(node: sd.api.SDNode, annotation_id: str):
    a: sd.api.SDProperty = get_node_annotation(node, annotation_id)
    if a is None:
        return None

    value = node.getAnnotationPropertyValueFromId(annotation_id)
    if value is not None:
        return value.get()
    else:
        return None

def set_node_annotation_value(node: sd.api.SDNode, annotation_id: str, annotation_value):
    a: sd.api.SDProperty = get_node_annotation(node, annotation_id)
    if a is None:
        print(f"No annotation [{annotation_id}] for node [{node.getIdentifier()}]")
    
    node.setAnnotationPropertyValueFromId(annotation_id, SDValue(annotation_value).sd_value)


def get_graph_all_input_nodes(graph: sd.api.SDGraph):
    nodes = graph.getNodes()
    n: sd.api.SDNode
    return [n for n in nodes if "sbs::compositing::input" in n.getDefinition().getId()]

def get_graph_all_output_nodes(graph: sd.api.SDGraph):
    nodes = graph.getNodes()
    n: sd.api.SDNode
    return [n for n in nodes if "sbs::compositing::output" in n.getDefinition().getId()]


def get_graph_all_inputs(graph: sd.api.SDGraph):
    return graph.getProperties(SDPropertyCategory.Input)

def get_all_comp_graphs():
    packages = pkg_mgr.getUserPackages()
    resources = [r for p in packages for r in p.getChildrenResources(True)]
    r: sd.api.SDResource
    return [r for r in resources if r.getClassName() == "SDSBSCompGraph"]

def get_property_all_annotations(graph: sd.api.SDGraph, prop: sd.api.SDProperty) -> sd.api.SDArray:
    return graph.getPropertyAnnotations(prop)

def get_property_annotation(graph: sd.api.SDGraph, prop: sd.api.SDProperty, annotation_id: str) -> sd.api.SDProperty:
    annotations = graph.getPropertyAnnotations(prop)
    p: sd.api.SDProperty
    return next((p for p in annotations if p.getId() == annotation_id), None)

def print_all_node_inputs(node: sd.api.SDNode):
    inputs: list[sd.api.SDProperty] = get_node_all_inputs(node)
    print(f"Node inputs: {[i.getId() for i in inputs]}")

def get_property_annotation_value(graph: sd.api.SDGraph, prop: sd.api.SDProperty, annotation_id: str):
    annotation_value = graph.getPropertyAnnotationValueFromId(prop, annotation_id)
    if annotation_value:
        return annotation_value.get()
    else:
        return None

def print_property_all_annotations(graph: sd.api.SDGraph, prop: sd.api.SDProperty):
    annotations = get_property_all_annotations(graph, prop)
    a: sd.api.SDProperty
    for a in annotations:
        value = get_property_annotation_value(graph, prop, a.getId())
        print(f"{a.getId()} = {value}")

def print_node_all_annotations(node: sd.api.SDNode):
    annotations = get_node_all_annotations(node)
    a: sd.api.SDProperty
    for a in annotations:
        value = node.getAnnotationPropertyValueFromId(a.getId())
        if value is not None:
            value = value.get()
        else:
            value = None
        print(f"{a.getId()} = {value}")

def get_resource_from_current_packages(identifier: str) -> sd.api.SDResource:
    packages = pkg_mgr.getUserPackages()
    resources = (r for p in packages for r in p.getChildrenResources(False))
    r: sd.api.SDResource
    return next((r for r in resources if r.getIdentifier() == identifier), None)

def get_resource_from_loaded_packages(identifier: str) -> sd.api.SDResource:
    packages = pkg_mgr.getPackages()
    resources = (r for p in packages for r in p.getChildrenResources(False))
    r: sd.api.SDResource
    return next((r for r in resources if r.getIdentifier() == identifier), None)

def get_compgraph_from_package(pkg: sd.api.SDPackage, identifier: str) -> sd.api.SDSBSCompGraph:
    resources: list[sd.api.SDResource] = (r for r in pkg.getChildrenResources(True))
    return (next(r for r in resources if r.getIdentifier() == identifier and r.getType().getId() == comp_graph_class), None)

def get_functiongraph_from_package(pkg: sd.api.SDPackage, identifier: str) -> sd.api.SDSBSFunctionGraph:
    resources: list[sd.api.SDResource] = (r for r in pkg.getChildrenResources(True))
    return (next(r for r in resources if r.getIdentifier() == identifier and r.getType().getId() == function_graph_class), None)

def compile_property_graph(node: sd.api.SDNode, property_id: str, property_source: str, parser: sexparser.NodeCreator):
    prop = get_node_input(node, property_id)
    ast_tree = ast.parse(property_source, mode="exec")
    prop_graph = node.newPropertyGraph(prop, function_graph_class)
    parser.graph = prop_graph
    parser.parse_module(ast_tree)