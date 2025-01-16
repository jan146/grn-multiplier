import grn
from utils import InputList, OutputList, get_regulators_list_and_products, to_structured_output_string, run_grn
from synthesis import synthesize

def get_full_adder(param_kd: float, param_n: float, param_alpha: float, param_delta: float) -> grn.grn:
    # Initialization
    full_adder: grn.grn = grn.grn()
    # Inputs
    full_adder.add_input_species("A")
    full_adder.add_input_species("B")
    full_adder.add_input_species("Cin")
    # Outputs
    full_adder.add_species("S", param_delta)
    full_adder.add_species("Cout", param_delta)
    # Add genes for sum
    regulators_list, products = get_regulators_list_and_products(
        expression="""
            A and not(B) and not(Cin) or
            not(A) and B and not(Cin) or
            not(A) and not(B) and Cin or
            A and B and Cin
        """,
        outputs=["S"],
        param_kd=param_kd,
        param_n=param_n,
    )
    for regulators in regulators_list:
        full_adder.add_gene(param_alpha, regulators, products)
    # Add genes for carry
    regulators_list, products = get_regulators_list_and_products(
        expression="""
            A and B and not(Cin) or
            A and not(B) and Cin or
            not(A) and B and Cin or
            A and B and Cin
        """,
        outputs=["Cout"],
        param_kd=param_kd,
        param_n=param_n,
    )
    for regulators in regulators_list:
        full_adder.add_gene(param_alpha, regulators, products)
    return full_adder

def get_half_adder(param_kd: float, param_n: float, param_alpha: float, param_delta: float) -> grn.grn:
    # Initialization
    half_adder: grn.grn = grn.grn()
    # Inputs
    half_adder.add_input_species("A")
    half_adder.add_input_species("B")
    # Outputs
    half_adder.add_species("S", param_delta)
    half_adder.add_species("C", param_delta)
    # Add genes for sum
    regulators_list, products = get_regulators_list_and_products(
        expression="""
            A and not(B)
            or
            not(A) and B
        """,
        outputs=["S"],
        param_kd=param_kd,
        param_n=param_n,
    )
    for regulators in regulators_list:
        half_adder.add_gene(param_alpha, regulators, products)
    # Add genes for carry
    regulators_list, products = get_regulators_list_and_products(
        expression="A and B",
        outputs=["C"],
        param_kd=param_kd,
        param_n=param_n,
    )
    for regulators in regulators_list:
        half_adder.add_gene(param_alpha, regulators, products)
    return half_adder

def get_two_bit_adder(param_kd: float, param_n: float, param_alpha: float, param_delta: float) -> grn.grn:
    full_adder: grn.grn = get_full_adder(param_kd, param_n, param_alpha, param_delta)
    half_adder: grn.grn = get_half_adder(param_kd, param_n, param_alpha, param_delta)
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
        param_kd=param_kd,
        param_n=param_n,
        param_alpha=param_alpha,
        param_delta=param_delta,
    )
    return two_bit_adder

def main():
    # Create & run 2-bit adder
    print("2-bit adder:")
    two_bit_adder: grn.grn = get_two_bit_adder(param_kd=5, param_n=2, param_alpha=10, param_delta=0.1)
    results: list[tuple[InputList, OutputList]] = run_grn(two_bit_adder)
    structured_output_string: list[str] = to_structured_output_string(
        results,
        outputs_override=["HA_S", "FA_Cout", "FA_S"],
        pretty=True,
    )
    print("\n".join(structured_output_string))
    print()

if __name__ == "__main__":
    main()

