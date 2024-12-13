import ast
import json
from typing import Any, TypeAlias, cast
import re

SpeciesList: TypeAlias = list[dict[str, Any]]

def parse_dnf_str(input: str) -> list[SpeciesList]:
    """Convert string of disjunctive normal form to regulators"""
    stmts: list[ast.stmt] = ast.parse(ast_string_cleaner(input)).body
    if len(stmts) != 1:
        raise Exception("Expression must have exactly one statement")
    return parse_dnf(cast(ast.Expr, stmts[0]))

def parse_dnf(tree: ast.Expr) -> list[SpeciesList]:
    """Convert expression of disjunctive normal form to regulators"""
    match tree.value:
        case ast.BoolOp():
            return parse_top_boolean(tree.value)
        case ast.UnaryOp() | ast.Name():
            return [parse_minterm(tree.value)]
        case _:
            raise Exception(f"Expression isn't in DNF: invalid top level operator: expected one of {{boolean operator, unary operator, variable name}}, got {tree.value}")

def ast_string_cleaner(input: str) -> str:
    """Remove unnecessary whitespaces before passing to AST parser"""
    input = re.sub(r"[\t\n\r\f\v]", r" ", input)
    input = re.sub(r"  +", r" ", input)
    input = input.strip()
    return input

def parse_minterm(node: ast.BoolOp | ast.UnaryOp | ast.Name) -> SpeciesList:
    match node:
        case ast.BoolOp():
            if not isinstance(node.op, ast.And):
                raise Exception(f"Invalid boolean operator, expected AND, got {node.op}")
            operands: list[ast.Name | ast.UnaryOp] = []
            for operand in node.values:
                if not isinstance(operand, ast.Name) and not isinstance(operand, ast.UnaryOp):
                    raise Exception(f"Invalid operand in conjunction: expected one of {{variable name, unary operator}}, got {operand}")
                operands.append(operand)
            regulators: SpeciesList = []
            for operand in operands:
                regulators.extend(parse_minterm(operand))
            return regulators
        case ast.UnaryOp():
            if not isinstance(node.op, ast.Not):
                raise Exception(f"Invalid unary operator: expected NOT, got: {node.op}")
            if not isinstance(node.operand, ast.Name):
                raise Exception(f"Invalid unary operator operand: {node.operand}")
            variable: ast.Name = node.operand
            return [{"name": variable.id, "type": -1, "Kd": 5, "n": 2}]
        case ast.Name():
            return [{"name": node.id, "type": 1, "Kd": 5, "n": 2}]
        case _:
            raise Exception(f"Expression isn't a minterm: expected one of {{variable name, boolean operator, unary operator}}, got {node}")

def parse_top_or(top_node: ast.BoolOp) -> list[SpeciesList]:
    regulators_list: list[SpeciesList] = []
    for node in top_node.values:
        match node:
            case ast.BoolOp() | ast.UnaryOp() | ast.Name():
                regulators_list.append(parse_minterm(node))
            case _:
                raise Exception(f"Invalid operand passed to top level or: expected one of {{boolean operator, unary operator, variable name}}, got {node}")
    return regulators_list

def parse_top_boolean(top_node: ast.BoolOp) -> list[SpeciesList]:
    match top_node.op:
        case ast.And():
            return [parse_minterm(top_node)]
        case ast.Or():
            return parse_top_or(top_node)
        case _:
            raise Exception(f"Expression isn't in DNF: invalid top level boolean operator: expected one of {{AND, OR}}, got {top_node.op}")
    return []

if __name__ == "__main__":
    regulators = parse_dnf(ast.Expr(value=
        ast.BoolOp(
            op=ast.Or(),
            values=[
                ast.BoolOp(
                    op=ast.And(),
                    values=[
                        ast.Name(id="A"),
                        ast.UnaryOp(
                            op=ast.Not(),
                            operand=ast.Name(id="B"),
                        ),
                    ],
                ),
                ast.BoolOp(
                    op=ast.And(),
                    values=[
                        ast.UnaryOp(
                            op=ast.Not(),
                            operand=ast.Name(id="A"),
                        ),
                        ast.Name(id="B"),
                    ],
                ),
            ],
        )
    ))
    print(json.dumps(regulators, indent=4))
    regulators = parse_dnf_str("(A and (not(B))) or (not(A) and B)")
    print(json.dumps(regulators, indent=4))

