import grn
from src.utils import InputList, OutputList, get_regulators_list_and_products, print_structured_output, run_grn
from src.synthesis import synthesize

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

def get_two_bit_adder() -> grn.grn:
    full_adder: grn.grn = get_full_adder()
    half_adder: grn.grn = get_half_adder()
    two_bit_adder: grn.grn = synthesize(
        named_grns=[
            (half_adder, "HA"),
            (full_adder, "FA"),
        ],
        connections=[
            (half_adder, "C", full_adder, "Cin"),
        ],
        inputs=[
            (full_adder, "B"),
            (full_adder, "A"),
            (half_adder, "B"),
            (half_adder, "A"),
        ],
    )
    return two_bit_adder

def main():
    # Create & run 2-bit adder
    print("2-bit adder:")
    two_bit_adder: grn.grn = get_two_bit_adder()
    results: list[tuple[InputList, OutputList]] = run_grn(two_bit_adder)
    print_structured_output(
        results,
        outputs_override=["HA_S", "FA_Cout", "FA_S"],
        pretty=True,
    )
    print()

if __name__ == "__main__":
    main()

