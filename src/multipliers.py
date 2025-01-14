from src.adders import get_full_adder, get_half_adder
import grn
from src.synthesis import synthesize
from src.utils import INPUT_CONCENTRATION_MAX, INPUT_CONCENTRATION_MIN, InputList, OutputList, get_regulators_list_and_products, to_structured_output_string, run_grn

def get_array_multiplier_row(size: int) -> grn.grn:

    # Initialization
    row: grn.grn = grn.grn()
    # Inputs
    for i in range(size):
        row.add_input_species(f"FA{i}_A")
        row.add_input_species(f"FA{i}_B")

    # Add full adders
    full_adders: list[grn.grn] = [get_full_adder() for _ in range(size)]

    # Prepare connections
    connections: list[tuple[grn.grn, str, grn.grn, str]] = []
    # Input connections
    for i in range(size):
        connections.append((row, f"FA{i}_A", full_adders[i], "A"))
        connections.append((row, f"FA{i}_B", full_adders[i], "B"))
    # Connections between full adders
    for i in range(size-1):
        connections.append((full_adders[i], "Cout", full_adders[i+1], "Cin"))

    # Synthesis
    row = synthesize(
        named_grns=[
            (row, "R"), *((full_adder, f"FA{i}") for i, full_adder in enumerate(full_adders))
        ],
        connections=connections,
        inputs=[
            (row, input) for input in row.input_species_names
        ],
    )
    return row

def get_four_bit_multiplier() -> grn.grn:

    # Initialization
    multiplier: grn.grn = grn.grn()
    # Inputs
    multiplier.add_input_species("X3")
    multiplier.add_input_species("X2")
    multiplier.add_input_species("X1")
    multiplier.add_input_species("X0")
    multiplier.add_input_species("Y3")
    multiplier.add_input_species("Y2")
    multiplier.add_input_species("Y1")
    multiplier.add_input_species("Y0")
    # Outputs
    multiplier.add_species("Z7", 0.1)
    multiplier.add_species("Z6", 0.1)
    multiplier.add_species("Z5", 0.1)
    multiplier.add_species("Z4", 0.1)
    multiplier.add_species("Z3", 0.1)
    multiplier.add_species("Z2", 0.1)
    multiplier.add_species("Z1", 0.1)
    multiplier.add_species("Z0", 0.1)

    # Rows
    rows: list[grn.grn] = [get_array_multiplier_row(4) for _ in range(3)]

    # Add AND gates
    for yi in ["Y3", "Y2", "Y1", "Y0"]:
        for xi in ["X3", "X2", "X1", "X0"]:
            multiplier.add_species(f"{xi}{yi}", 0.1)
            regulators_list, products = get_regulators_list_and_products(
                expression=f"{xi} and {yi}",
                outputs=[f"{xi}{yi}"],
            )
            for regulators in regulators_list:
                multiplier.add_gene(10, regulators, products)

    # Prepare connections
    connections: list[tuple[grn.grn, str, grn.grn, str]] = []
    # First row FA{i}_A
    for i in range(3):
        connections.append((multiplier, f"X{i+1}Y0", rows[0], f"FA{i}_A"))
    # FA{i}_B
    for i in range(3):
        for j in range(4):
            connections.append((multiplier, f"X{j}Y{i+1}", rows[i], f"FA{j}_B"))
    # Row carry
    for i in range(2):
        connections.append((rows[i], f"FA{3}_Cout", rows[i+1], f"FA{3}_A"))
    # Row results
    for i in range(len(rows)-1):
        for j in range(3):
            connections.append((rows[i], f"FA{j+1}_S", rows[i+1], f"FA{j}_A"))
    # Final outputs
    connections.append((multiplier, f"X0Y0", multiplier, f"Z0"))
    for i in range(len(rows)-1):
        connections.append((rows[i], f"FA0_S", multiplier, f"Z{i+1}"))
    for i in range(3):
        connections.append((rows[2], f"FA{i}_S", multiplier, f"Z{i+len(rows)}"))
    connections.append((rows[2], f"FA{3}_Cout", multiplier, f"Z{7}"))

    # Synthesis
    multiplier = synthesize(
        named_grns=[
            (multiplier, "M"),
            *((row, f"ROW{i}") for i, row in enumerate(rows)),
        ],
        connections=connections,
        inputs=[
            (multiplier, input) for input in multiplier.input_species_names
        ],
    )
    return multiplier

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

def to_structured_output_multiplier_specific(simulation_results: list[tuple[InputList, OutputList]], operand_1_inputs: list[str], operand_2_inputs: list[str], outputs: list[str]) -> tuple[list[str], float]:
    result: list[str] = []
    correct: int = 0
    threshold: float = (INPUT_CONCENTRATION_MIN + INPUT_CONCENTRATION_MAX) / 2.0
    for simlation_iteration in simulation_results:
        inputs_iteration: dict[str, float] = {input_name: value for input_name, value in simlation_iteration[0]}
        outputs_iteration: dict[str, float] = {output_name: value for output_name, value in simlation_iteration[1]}
        operand_1_value, operand_2_value, result_value = 0, 0, 0
        for operand_1_input in operand_1_inputs:
            operand_1_value = operand_1_value * 2 + (int(inputs_iteration[operand_1_input] > threshold))
        for operand_2_input in operand_2_inputs:
            operand_2_value = operand_2_value * 2 + (int(inputs_iteration[operand_2_input] > threshold))
        for output in outputs:
            result_value = result_value * 2 + (int(outputs_iteration[output] > threshold))
        result.append(f"{operand_1_value} * {operand_2_value} = {result_value}")
        if result_value != operand_1_value * operand_2_value:
            result[-1] = result[-1] + f" != {operand_1_value * operand_2_value}"
        else:
            correct += 1
    return result, (correct/len(simulation_results))

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
    structured_output_string, accuracy = to_structured_output_multiplier_specific(
        simulation_results=results,
        operand_1_inputs=["M_A1", "M_A0"],
        operand_2_inputs=["M_B1", "M_B0"],
        outputs=["M_M3", "M_M2", "M_M1", "M_M0"],
    )
    print("\n".join(structured_output_string))
    print(f"Accuracy: {accuracy*100:.1f}%")
    print()

    # Create & run 4-bit multiplier
    print("4-bit multiplier:")
    four_bit_multiplier: grn.grn = get_four_bit_multiplier()
    results = run_grn(four_bit_multiplier)
    structured_output_string = to_structured_output_string(
        results,
        outputs_override=[f"M_Z{i}" for i in range(8)],
        pretty=True,
    )
    print("\n".join(structured_output_string))
    structured_output_string, accuracy = to_structured_output_multiplier_specific(
        simulation_results=results,
        operand_1_inputs=["M_X3", "M_X2", "M_X1", "M_X0"],
        operand_2_inputs=["M_Y3", "M_Y2", "M_Y1", "M_Y0"],
        outputs=["M_Z7", "M_Z6", "M_Z5", "M_Z4", "M_Z3", "M_Z2", "M_Z1", "M_Z0"],
    )
    print("\n".join(structured_output_string))
    print(f"Accuracy: {accuracy*100:.1f}%")
    print()

if __name__ == "__main__":
    main()

