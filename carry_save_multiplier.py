import grn
from utils import get_regulators_list_and_products, run_grn, print_structured_output
from synthesis import synthesize
from adders import get_full_adder
from utils import generate_truth_table

def get_carry_save_multiplier() -> grn.grn:
    """
    Implements a 2x2 Carry Save Multiplier using the existing 2-bit multiplier and adders.
    """
    
    # Initialization of the carry-save multiplier GRN
    csm: grn.grn = grn.grn()
    
    # Inputs (2 bits each for two binary numbers A and B)
    csm.add_input_species("A1")
    csm.add_input_species("A0")
    csm.add_input_species("B1")
    csm.add_input_species("B0")
    
    # Outputs (4 bits for the final result)
    csm.add_species("P3", 0.1)  # Most significant bit
    csm.add_species("P2", 0.1)
    csm.add_species("P1", 0.1)
    csm.add_species("P0", 0.1)  # Least significant bit
    
    # Internal nodes for intermediate partial products
    for i in range(2):  # A1, A0
        for j in range(2):  # B1, B0
            csm.add_species(f"PP{i}{j}", 0.1)  # Partial Product (PPij = Ai * Bj)
    
    # AND gates for each bit of A and B to create the partial products (PPij = Ai * Bj)
    for i in range(2):
        for j in range(2):
            regulators_list, products = get_regulators_list_and_products(
                expression=f"A{i} and B{j}",
                outputs=[f"PP{i}{j}"]
            )
            for regulators in regulators_list:
                csm.add_gene(10, regulators, products)
    
    # Use Full Adders to sum partial products column by column
    
    full_adder_0: grn.grn = get_full_adder()
    full_adder_1: grn.grn = get_full_adder()
    
    csm = synthesize(
        named_grns=[
            (csm, "CSM"),
            (full_adder_0, "FA0"),
            (full_adder_1, "FA1"),
        ],
        connections=[
            (csm, "PP00", csm, "P0"),  # First bit is just PP00
            (csm, "PP10", full_adder_0, "A"),
            (csm, "PP01", full_adder_0, "B"),
            (full_adder_0, "S", csm, "P1"),
            (full_adder_0, "Cout", full_adder_1, "A"),
            (csm, "PP11", full_adder_1, "B"),
            (full_adder_1, "S", csm, "P2"),
            (full_adder_1, "Cout", csm, "P3"),  # Carry-out becomes the most significant bit
        ],
        inputs=[
            (csm, "A1"), (csm, "A0"),
            (csm, "B1"), (csm, "B0"),
        ]
    )
    
    return csm

def main():
    """
    Main function to create and run the Carry-Save Multiplier.
    """
    print("2x2 Carry-Save Multiplier:")
    carry_save_multiplier: grn.grn = get_carry_save_multiplier()
    results = run_grn(carry_save_multiplier)
    printed_result = print_structured_output(
        results,
        outputs_override=["CSM_P3", "CSM_P2", "CSM_P1", "CSM_P0"],
        pretty=True,
    )
    
    print("Truth Table for 2x2 Carry-Save")

    truth_table = generate_truth_table(2)

    print("compare results")
    print(truth_table == printed_result)

if __name__ == "__main__":
    main()
