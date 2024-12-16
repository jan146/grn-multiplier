from src.parser import SpeciesList, parse_dnf, parse_dnf_str
import ast
import grn
import numpy as np
import numpy.typing as npt
from typing import TypeAlias
import itertools
import simulator

INPUT_CONCENTRATION_MIN: int = 0
INPUT_CONCENTRATION_MAX: int = 100
T_SINGLE: int = 250
PLOT_ON: bool = False

InputType: TypeAlias = tuple[str, float]
InputList: TypeAlias = list[InputType]
OutputType: TypeAlias = tuple[str, float]
OutputList: TypeAlias = list[OutputType]

def print_structured_output(structured_output: list[tuple[InputList, OutputList]]):
    for inputs, outputs in structured_output:
        print(f"{inputs} -> {outputs}")

def get_structured_input_output(grn: grn.grn, input_combinations: list[tuple[int,...]], Y: npt.NDArray, t_single: int) -> list[tuple[InputList, OutputList]]:
    # Get sampling points (time axis)
    t_samples: npt.NDArray = get_t_samples(num_input_combinations=len(input_combinations), t_single=t_single)
    if len(input_combinations) != t_samples.shape[0]:
        print(f"Warning: {len(input_combinations)=} != {t_samples.shape[0]=}")
    # Dear Santa, please provide me with built-in frozenlist this year, it's much cleaner than lists of tuples
    # Put results into mapping [(input_name, input_value)] |-> [(output_name, output_value)]
    results: list[tuple[InputList, OutputList]] = []
    for t_sample in t_samples:
        inputs: InputList = []
        outputs: OutputList = []
        for species_index, species_name in enumerate(grn.species_names):
            if species_name in grn.input_species_names:
                inputs.append((species_name, float(Y.T[species_index][t_sample])))
            else:
                outputs.append((species_name, float(Y.T[species_index][t_sample])))
        results.append((inputs, outputs))
    return results

def get_t_samples(num_input_combinations: int, t_single: int) -> npt.NDArray:
    return np.arange(num_input_combinations) * t_single + (int(t_single/2))

def get_regulators_list_and_products(expression: str | ast.Expr, outputs: list[str]) -> tuple[list[SpeciesList], SpeciesList]:
    """Convert DNF expression and outputs to pair (regulators_list, products)"""
    regulators_list: list[SpeciesList] = parse_dnf(expression) if isinstance(expression, ast.Expr) else parse_dnf_str(expression)
    products: SpeciesList = [{"name": output} for output in outputs]
    return regulators_list, products

def run_grn(grn: grn.grn) -> list[tuple[InputList, OutputList]]:
    # Prepare exhaustive list of input combinations
    input_combinations: list[tuple[int,...]] = list(itertools.product([INPUT_CONCENTRATION_MIN, INPUT_CONCENTRATION_MAX], repeat=len(grn.input_species_names)))
    # Run simulation
    _, Y = simulator.simulate_sequence(
        grn,
        input_combinations,
        t_single=T_SINGLE,
        plot_on=PLOT_ON,
    )
    if not isinstance(Y, np.ndarray):
        raise Exception(f"Error: Y is not a numpy array {type(Y)=}")
    # Get actually somewhat readable results
    results: list[tuple[InputList, OutputList]] = get_structured_input_output(grn, input_combinations=input_combinations, Y=Y, t_single=T_SINGLE)
    return results
