import simulator
import grn
from src.utils import InputList, OutputList, get_regulators_list_and_products, get_structured_input_output, print_structured_output
import itertools
import numpy as np
from src.synthesis import synthesize

INPUT_CONCENTRATION_MIN: int = 0
INPUT_CONCENTRATION_MAX: int = 100
T_SINGLE: int = 250
PLOT_ON: bool = False

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

def main():
    results: list[tuple[InputList, OutputList]]
    # Create & run half adder
    print("Half adder:")
    half_adder: grn.grn = get_half_adder()
    results = run_grn(half_adder)
    print_structured_output(results)
    print()
    # Create & run full adder
    print("Full adder:")
    full_adder: grn.grn = get_full_adder()
    results = run_grn(full_adder)
    print_structured_output(results)
    print()
    # Create & run 2-bit adder
    print("2-bit adder:")
    two_bit_adder: grn.grn = synthesize(
        named_grns=[
            (half_adder, "HA"),
            (full_adder, "FA"),
        ],
        connections=[
            (half_adder, "C", full_adder, "Cin"),
        ],
        inputs={
            "A0": (half_adder, "A"),
            "B0": (half_adder, "B"),
            "A1": (full_adder, "A"),
            "B1": (full_adder, "B"),
        },
        outputs={
            "Y0": (half_adder, "S"),
            "Y1": (full_adder, "S"),
            "Y2": (full_adder, "Cout"),
        },
    )
    results = run_grn(two_bit_adder)
    print_structured_output(results)
    print()

if __name__ == "__main__":
    main()

