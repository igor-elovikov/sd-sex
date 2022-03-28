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
            