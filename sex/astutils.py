from __future__ import annotations
import ast

from typing import Any

class SexAstTransfomer(ast.NodeTransformer):

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        if not isinstance(node.op, ast.USub):
            return super().visit_UnaryOp(node)
        if not isinstance(node.operand, ast.Num):
            return super().visit_UnaryOp(node)

        new_node: ast.Num = ast.Num(-node.operand.n)
        new_node = ast.copy_location(new_node, node)

        return new_node
            