from src.parser import SpeciesList, parse_dnf, parse_dnf_str
import ast

def get_regulators_list_and_products(expression: str | ast.Expr, outputs: list[str]) -> tuple[list[SpeciesList], SpeciesList]:
    """Convert DNF expression and outputs to pair (regulators_list, products)"""
    regulators_list: list[SpeciesList] = parse_dnf(expression) if isinstance(expression, ast.Expr) else parse_dnf_str(expression)
    products: SpeciesList = [{"name": output} for output in outputs]
    return regulators_list, products

