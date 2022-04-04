from __future__ import annotations
import ast

from typing import Any

def get_node_name(node: ast.Name | ast.Attribute) -> list[str]:

    if isinstance(node, ast.Name):
        return node.id

    names = []

    if isinstance(node, ast.Attribute):
        child = node
        while isinstance(child, ast.Attribute):
            names.append(child.attr)
            child = child.value
        if isinstance(child, ast.Name):
            names.append(child.id)
        
        names.reverse()
        return ".".join(names)

def get_node_value(node: ast.Num | ast.Str) -> int | float | str:
    if not isinstance(node, (ast.Num, ast.Str)):
        return None

    if isinstance(node, ast.Num):
        return node.n
    
    return node.s

class FunctionDecorator:
    def __init__(self) -> None:
        self.keyargs: dict = {}
        self.args: list[Any] = []

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
                d.keyargs[key] = None

                if isinstance(keyword.value, ast.Num):
                    d.keyargs[key] = keyword.value.n

                if isinstance(keyword.value, ast.Str):
                    d.keyargs[key] = keyword.value.s

            d.args = [get_node_value(arg) for arg in decorator.args]
            d.args = [v for v in d.args if v is not None]
           
            result[decorator.func.id] = d
            continue

    return result

class SexAstTransfomer(ast.NodeTransformer):

    def __init__(self) -> None:
        super().__init__()

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        if not isinstance(node.op, ast.USub):
            return node
        if not isinstance(node.operand, ast.Num):
            return node

        new_node: ast.Num = ast.Num(-node.operand.n)
        new_node = ast.copy_location(new_node, node)

        return new_node
            