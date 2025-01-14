from src.adders import get_half_adder
import grn
from src.synthesis import synthesize
from src.utils import InputList, OutputList, get_regulators_list_and_products, to_structured_output_string, run_grn

def get_two_bit_multiplier() -> grn.grn:

    # Initialization
    multiplier: grn.grn = grn.grn()
    # Inputs
    multiplier.add_input_species("B1")
    multiplier.add_input_species("B0")
    multiplier.add_input_species("A1")
    multiplier.add_input_species("A0")
    # Outputs
    multiplier.add_species("M3", 0.1)
    multiplier.add_species("M2", 0.1)
    multiplier.add_species("M1", 0.1)
    multiplier.add_species("M0", 0.1)
    # Internal state variables
    multiplier.add_species("A1B0", 0.1)
    multiplier.add_species("A0B1", 0.1)
    multiplier.add_species("A1B1", 0.1)

    # Half adder for M1
    half_adder_0: grn.grn = get_half_adder()
    # Half adder for M2
    half_adder_1: grn.grn = get_half_adder()

    # Add AND gates
    regulators_list, products = get_regulators_list_and_products(
        expression="""
            A1 and B0
        """,
        outputs=["A1B0"],
    )
    for regulators in regulators_list:
        multiplier.add_gene(10, regulators, products)
    regulators_list, products = get_regulators_list_and_products(
        expression="""
            A0 and B1
        """,
        outputs=["A0B1"],
    )
    for regulators in regulators_list:
        multiplier.add_gene(10, regulators, products)
    regulators_list, products = get_regulators_list_and_products(
        expression="""
            A1 and B1
        """,
        outputs=["A1B1"],
    )
    for regulators in regulators_list:
        multiplier.add_gene(10, regulators, products)
    regulators_list, products = get_regulators_list_and_products(
        expression="""
            A0 and B0
        """,
        outputs=["M0"],
    )
    for regulators in regulators_list:
        multiplier.add_gene(10, regulators, products)

    # Synthesis
    multiplier = synthesize(
        named_grns=[
            (multiplier, "M"),
            (half_adder_0, "HA0"),
            (half_adder_1, "HA1"),
        ],
        connections=[
            (multiplier, "A1B0", half_adder_0, "A"),
            (multiplier, "A0B1", half_adder_0, "B"),
            (multiplier, "A1B1", half_adder_1, "A"),
            (half_adder_0, "C", half_adder_1, "B"),
            (half_adder_0, "S", multiplier, "M1"),
            (half_adder_1, "S", multiplier, "M2"),
            (half_adder_1, "C", multiplier, "M3"),
        ],
        inputs=[
            (multiplier, input) for input in multiplier.input_species_names
        ],
    )

    return multiplier

def main():
    # Create & run 2-bit multiplier
    print("2-bit multiplier:")
    two_bit_multiplier: grn.grn = get_two_bit_multiplier()
    results: list[tuple[InputList, OutputList]] = run_grn(two_bit_multiplier)
    structured_output_string: list[str] = to_structured_output_string(
        results,
        outputs_override=["M_M3", "M_M2", "M_M1", "M_M0"],
        pretty=True,
    )
    print("\n".join(structured_output_string))
    print()

if __name__ == "__main__":
    main()

