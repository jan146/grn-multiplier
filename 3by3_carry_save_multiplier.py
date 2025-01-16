import grn
from utils import get_regulators_list_and_products, run_grn, print_structured_output
from synthesis import synthesize
from adders import get_full_adder
from utils import generate_truth_table

def get_carry_save_multiplier() -> grn.grn:
    """
    Implements a 3x3 Carry Save Multiplier using the existing 3-bit multiplier and adders.
    """
    # Initialization of the carry-save multiplier GRN
    csm: grn.grn = grn.grn()

    # Inputs (3 bits each for two binary numbers A and B)
    for i in range(3):
        csm.add_input_species(f"A{i}")
        csm.add_input_species(f"B{i}")

    # Outputs (6 bits for the final result)
    for i in range(6):
        csm.add_species(f"P{i}", 0.1)  # Output bits P0 to P5

    # Internal nodes for intermediate partial products
    for i in range(3):  # A2, A1, A0
        for j in range(3):  # B2, B1, B0
            csm.add_species(f"PP{i}{j}", 0.1)  # Partial Product (PPij = Ai * Bj)

    # AND gates for each bit of A and B to create the partial products (PPij = Ai * Bj)
    for i in range(3):
        for j in range(3):
            regulators_list, products = get_regulators_list_and_products(
                expression=f"A{i} and B{j}",
                outputs=[f"PP{i}{j}"]
            )
            for regulators in regulators_list:
                csm.add_gene(10, regulators, products)

    # Use Full Adders to sum partial products column by column
    full_adders = [get_full_adder() for _ in range(7)]  # Create enough full adders

    # Connections between partial products and full adders
    connections = []

    # First column: PP00 goes directly to P0
    connections.append((csm, "PP00", csm, "P0"))

    # Second column: PP01, PP10, and carry from the previous column
    connections.extend([
        (csm, "PP10", full_adders[0], "A"),
        (csm, "PP01", full_adders[0], "B"),
        (full_adders[0], "S", csm, "P1"),
        (full_adders[0], "Cout", full_adders[1], "A"),
    ])

    # Third column: PP02, PP11, PP20, and carry
    connections.extend([
        (csm, "PP20", full_adders[1], "B"),
        (csm, "PP11", full_adders[2], "A"),
        (csm, "PP02", full_adders[2], "B"),
        (full_adders[1], "S", csm, "P2"),
        (full_adders[1], "Cout", full_adders[2], "Cin"),
        (full_adders[2], "S", csm, "P3"),
        (full_adders[2], "Cout", full_adders[3], "A"),
    ])

    # Continue similarly for remaining columns
    connections.extend([
        (csm, "PP21", full_adders[3], "B"),
        (csm, "PP12", full_adders[4], "A"),
        (csm, "PP22", full_adders[4], "B"),
        (full_adders[3], "S", csm, "P4"),
        (full_adders[3], "Cout", full_adders[4], "Cin"),
        (full_adders[4], "S", csm, "P5"),
    ])

    csm = synthesize(
        named_grns=[
            (csm, "CSM"),
            *[(fa, f"FA{i}") for i, fa in enumerate(full_adders)],
        ],
        connections=connections,
        inputs=[
            (csm, "A2"), (csm, "A1"), (csm, "A0"),
            (csm, "B2"), (csm, "B1"), (csm, "B0"),
        ]
    )

    return csm

def main():
    """
    Main function to create and run the Carry-Save Multiplier.
    """
    print("3x3 Carry-Save Multiplier:")
    carry_save_multiplier: grn.grn = get_carry_save_multiplier()
    results = run_grn(carry_save_multiplier)
    output = print_structured_output(
        results,
        outputs_override=["CSM_P0", "CSM_P1", "CSM_P2", "CSM_P3", "CSM_P4", "CSM_P5"],
        pretty=True,
    )
    print()

    print("Truth Table for 3x3 Carry-Save")
    print(output)
    truth = generate_truth_table(3)

    print("compare results")
    print(truth == output)

    print(truth)


if __name__ == "__main__":
    main()
