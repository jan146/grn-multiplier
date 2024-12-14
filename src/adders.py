import simulator
import grn
from src.utils import InputList, OutputList, get_regulators_list_and_products, get_structured_input_output
import itertools
import numpy as np

INPUT_CONCENTRATION_MIN: int = 0
INPUT_CONCENTRATION_MAX: int = 100
T_SINGLE: int = 250

def get_full_adder() -> grn.grn:
    # Initialization
    full_adder: grn.grn = grn.grn()
    # Inputs
    full_adder.add_input_species("A")
    full_adder.add_input_species("B")
    full_adder.add_input_species("Cin")
    # Outputs
    full_adder.add_species("S", 0.1)
    full_adder.add_species("Cout", 0.1)
    # Add genes for sum
    regulators_list, products = get_regulators_list_and_products(
        expression="""
            A and not(B) and not(Cin) or
            not(A) and B and not(Cin) or
            not(A) and not(B) and Cin or
            A and B and Cin
        """,
        outputs=["S"],
    )
    for regulators in regulators_list:
        full_adder.add_gene(10, regulators, products)
    # Add genes for carry
    regulators_list, products = get_regulators_list_and_products(
        expression="""
            A and B and not(Cin) or
            A and not(B) and Cin or
            not(A) and B and Cin or
            A and B and Cin
        """,
        outputs=["Cout"],
    )
    for regulators in regulators_list:
        full_adder.add_gene(10, regulators, products)
    return full_adder

def get_half_adder() -> grn.grn:
    # Initialization
    half_adder: grn.grn = grn.grn()
    # Inputs
    half_adder.add_input_species("A")
    half_adder.add_input_species("B")
    # Outputs
    half_adder.add_species("S", 0.1)
    half_adder.add_species("C", 0.1)
    # Add genes for sum
    regulators_list, products = get_regulators_list_and_products(
        expression="""
            A and not(B)
            or
            not(A) and B
        """,
        outputs=["S"],
    )
    for regulators in regulators_list:
        half_adder.add_gene(10, regulators, products)
    # Add genes for carry
    regulators_list, products = get_regulators_list_and_products(
        expression="A and B",
        outputs=["C"],
    )
    for regulators in regulators_list:
        half_adder.add_gene(10, regulators, products)
    return half_adder

def run_half_adder():
    # Create half adder
    half_adder: grn.grn = get_half_adder()
    # Prepare exhaustive list of input combinations
    input_combinations: list[tuple[int,...]] = [
        (INPUT_CONCENTRATION_MIN, INPUT_CONCENTRATION_MIN),
        (INPUT_CONCENTRATION_MIN, INPUT_CONCENTRATION_MAX),
        (INPUT_CONCENTRATION_MAX, INPUT_CONCENTRATION_MIN),
        (INPUT_CONCENTRATION_MAX, INPUT_CONCENTRATION_MAX),
    ]
    # Run simulation
    _, Y = simulator.simulate_sequence(
        half_adder,
        input_combinations,
        t_single=T_SINGLE,
    )
    if not isinstance(Y, np.ndarray):
        raise Exception(f"Error: Y is not a numpy array {type(Y)=}")
    # Get actually somewhat readable results
    results: list[tuple[InputList, OutputList]] = get_structured_input_output(half_adder, input_combinations=input_combinations, Y=Y, t_single=T_SINGLE)

def run_full_adder():
    # Create full adder
    full_adder: grn.grn = get_full_adder()
    # Prepare exhaustive list of input combinations
    input_combinations: list[tuple[int,...]] = list(itertools.product([INPUT_CONCENTRATION_MIN, INPUT_CONCENTRATION_MAX], repeat=len(full_adder.input_species_names)))
    # Run simulation
    _, Y = simulator.simulate_sequence(
        full_adder,
        input_combinations,
        t_single=T_SINGLE,
    )
    if not isinstance(Y, np.ndarray):
        raise Exception(f"Error: Y is not a numpy array {type(Y)=}")
    # Get actually somewhat readable results
    results: list[tuple[InputList, OutputList]] = get_structured_input_output(full_adder, input_combinations=input_combinations, Y=Y, t_single=T_SINGLE)

def main():
    run_half_adder()
    run_full_adder()

if __name__ == "__main__":
    main()

