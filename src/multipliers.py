from src.adders import get_full_adder, get_half_adder
import grn
from src.synthesis import synthesize
from src.utils import INPUT_CONCENTRATION_MAX, INPUT_CONCENTRATION_MIN, InputList, OutputList, get_regulators_list_and_products, to_structured_output_string, run_grn

def get_carry_save_multiplier_row(size: int, param_kd: float, param_n: float, param_alpha: float, param_delta: float) -> grn.grn:
    # Initialization
    row: grn.grn = grn.grn()
    # Inputs
    for i in range(size):
        row.add_input_species(f"FA{i}_A")
        row.add_input_species(f"FA{i}_B")
        row.add_input_species(f"FA{i}_Cin")

    # Add full adders
    full_adders: list[grn.grn] = [get_full_adder(param_kd, param_n, param_alpha, param_delta) for _ in range(size)]

    # Prepare connections
    connections: list[tuple[grn.grn, str, grn.grn, str]] = []
    # Input connections
    for i in range(size):
        connections.append((row, f"FA{i}_A", full_adders[i], "A"))
        connections.append((row, f"FA{i}_B", full_adders[i], "B"))
        connections.append((row, f"FA{i}_Cin", full_adders[i], "Cin"))

    # Synthesis
    row = synthesize(
        named_grns=[
            (row, "R"), *((full_adder, f"FA{i}") for i, full_adder in enumerate(full_adders))
        ],
        connections=connections,
        inputs=[
            (row, input) for input in row.input_species_names
        ],
        param_kd=param_kd,
        param_n=param_n,
        param_alpha=param_alpha,
        param_delta=param_delta,
    )
    return row

def get_carry_save_multiplier(size: int, param_kd: float, param_n: float, param_alpha: float, param_delta: float) -> grn.grn:
    # Initialization
    multiplier: grn.grn = grn.grn()
    # Inputs
    for i in reversed(range(size)):
        multiplier.add_input_species(f"X{i}")
    for i in reversed(range(size)):
        multiplier.add_input_species(f"Y{i}")
    # Outputs
    for i in reversed(range(2*size)):
        multiplier.add_species(f"Z{i}", param_delta)

    # Add AND gates
    for yi in [f"Y{i}" for i in range(size)]:
        for xj in [f"X{j}" for j in range(size)]:
            multiplier.add_species(f"{xj}{yi}", param_delta)
            regulators_list, products = get_regulators_list_and_products(
                expression=f"{xj} and {yi}",
                outputs=[f"{xj}{yi}"],
                param_kd=param_kd,
                param_n=param_n,
            )
            for regulators in regulators_list:
                multiplier.add_gene(param_alpha, regulators, products)

    # Rows (last one is different)
    rows: list[grn.grn] = [get_carry_save_multiplier_row(size, param_kd, param_n, param_alpha, param_delta) for _ in range(size-1)] + [get_array_multiplier_row(size, param_kd, param_n, param_alpha, param_delta)]

    # Prepare connections
    connections: list[tuple[grn.grn, str, grn.grn, str]] = []
    # Connect XiY0
    connections.append((multiplier, f"X0Y0", multiplier, f"Z0"))
    for j in range(size-1):
        connections.append((multiplier, f"X{j+1}Y0", rows[0], f"FA{j}_A"))
    # Connect other inputs
    for i in range(len(rows)-1):
        for j in range(size):
            connections.append((multiplier, f"X{j}Y{i+1}", rows[i], f"FA{j}_B"))
    # Add vertical connections
    for i in range(len(rows)-1):
        for j in range(size-1):
            connections.append((rows[i], f"FA{j+1}_S", rows[i+1], f"FA{j}_A"))
    # Add diagonal connections (except last row)
    for i in range(size-2):
        for j in range(size):
            connections.append((rows[i], f"FA{j}_Cout", rows[i+1], f"FA{j}_Cin"))
    # Add diagonal connection (last row)
    for j in range(size):
        connections.append((rows[-2], f"FA{j}_Cout", rows[-1], f"FA{j}_B"))
    # Connect outputs
    for i in range(len(rows)-1):
        connections.append((rows[i], f"FA0_S", multiplier, f"Z{i+1}"))
    for j in range(size):
        connections.append((rows[-1], f"FA{j}_S", multiplier, f"Z{j+len(rows)}"))

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
        param_kd=param_kd,
        param_n=param_n,
        param_alpha=param_alpha,
        param_delta=param_delta,
    )
    return multiplier

def get_array_multiplier_row(size: int, param_kd: float, param_n: float, param_alpha: float, param_delta: float) -> grn.grn:

    # Initialization
    row: grn.grn = grn.grn()
    # Inputs
    for i in range(size):
        row.add_input_species(f"FA{i}_A")
        row.add_input_species(f"FA{i}_B")

    # Add full adders
    full_adders: list[grn.grn] = [get_full_adder(param_kd, param_n, param_alpha, param_delta) for _ in range(size)]

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
        param_kd=param_kd,
        param_n=param_n,
        param_alpha=param_alpha,
        param_delta=param_delta,
    )
    return row

def get_array_multiplier(size: int, param_kd: float, param_n: float, param_alpha: float, param_delta: float) -> grn.grn:

    # Initialization
    multiplier: grn.grn = grn.grn()
    # Inputs
    for i in reversed(range(size)):
        multiplier.add_input_species(f"X{i}")
    for i in reversed(range(size)):
        multiplier.add_input_species(f"Y{i}")
    # Outputs
    for i in reversed(range(2*size)):
        multiplier.add_species(f"Z{i}", param_delta)

    # Rows
    rows: list[grn.grn] = [get_array_multiplier_row(size, param_kd, param_n, param_alpha, param_delta) for _ in range(size-1)]

    # Add AND gates
    for yi in [f"Y{i}" for i in range(size)]:
        for xj in [f"X{j}" for j in range(size)]:
            multiplier.add_species(f"{xj}{yi}", param_delta)
            regulators_list, products = get_regulators_list_and_products(
                expression=f"{xj} and {yi}",
                outputs=[f"{xj}{yi}"],
                param_kd=param_kd,
                param_n=param_n,
            )
            for regulators in regulators_list:
                multiplier.add_gene(param_alpha, regulators, products)

    # Prepare connections
    connections: list[tuple[grn.grn, str, grn.grn, str]] = []
    # First row FA{i}_A
    for i in range(size-1):
        connections.append((multiplier, f"X{i+1}Y0", rows[0], f"FA{i}_A"))
    # FA{i}_B
    for i in range(size-1):
        for j in range(size):
            connections.append((multiplier, f"X{j}Y{i+1}", rows[i], f"FA{j}_B"))
    # Row carry
    for i in range(len(rows)-1):
        connections.append((rows[i], f"FA{size-1}_Cout", rows[i+1], f"FA{size-1}_A"))
    # Row results
    for i in range(len(rows)-1):
        for j in range(size-1):
            connections.append((rows[i], f"FA{j+1}_S", rows[i+1], f"FA{j}_A"))
    # Final outputs
    connections.append((multiplier, f"X0Y0", multiplier, f"Z0"))
    for i in range(len(rows)-1):
        connections.append((rows[i], f"FA0_S", multiplier, f"Z{i+1}"))
    for i in range(size):
        connections.append((rows[-1], f"FA{i}_S", multiplier, f"Z{i+len(rows)}"))
    connections.append((rows[-1], f"FA{size-1}_Cout", multiplier, f"Z{2*size-1}"))

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
        param_kd=param_kd,
        param_n=param_n,
        param_alpha=param_alpha,
        param_delta=param_delta,
    )
    return multiplier

def get_two_bit_multiplier(param_kd: float, param_n: float, param_alpha: float, param_delta: float) -> grn.grn:

    # Initialization
    multiplier: grn.grn = grn.grn()
    # Inputs
    multiplier.add_input_species("B1")
    multiplier.add_input_species("B0")
    multiplier.add_input_species("A1")
    multiplier.add_input_species("A0")
    # Outputs
    multiplier.add_species("M3", param_delta)
    multiplier.add_species("M2", param_delta)
    multiplier.add_species("M1", param_delta)
    multiplier.add_species("M0", param_delta)
    # Internal state variables
    multiplier.add_species("A1B0", param_delta)
    multiplier.add_species("A0B1", param_delta)
    multiplier.add_species("A1B1", param_delta)

    # Half adder for M1
    half_adder_0: grn.grn = get_half_adder(param_kd, param_n, param_alpha, param_delta)
    # Half adder for M2
    half_adder_1: grn.grn = get_half_adder(param_kd, param_n, param_alpha, param_delta)

    # Add AND gates
    regulators_list, products = get_regulators_list_and_products(
        expression="""
            A1 and B0
        """,
        outputs=["A1B0"],
        param_kd=param_kd,
        param_n=param_n,
    )
    for regulators in regulators_list:
        multiplier.add_gene(param_alpha, regulators, products)
    regulators_list, products = get_regulators_list_and_products(
        expression="""
            A0 and B1
        """,
        outputs=["A0B1"],
        param_kd=param_kd,
        param_n=param_n,
    )
    for regulators in regulators_list:
        multiplier.add_gene(param_alpha, regulators, products)
    regulators_list, products = get_regulators_list_and_products(
        expression="""
            A1 and B1
        """,
        outputs=["A1B1"],
        param_kd=param_kd,
        param_n=param_n,
    )
    for regulators in regulators_list:
        multiplier.add_gene(param_alpha, regulators, products)
    regulators_list, products = get_regulators_list_and_products(
        expression="""
            A0 and B0
        """,
        outputs=["M0"],
        param_kd=param_kd,
        param_n=param_n,
    )
    for regulators in regulators_list:
        multiplier.add_gene(param_alpha, regulators, products)

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
        param_kd=param_kd,
        param_n=param_n,
        param_alpha=param_alpha,
        param_delta=param_delta,
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

def run_and_print_multiplier(size: int, multiplier: grn.grn):
    results: list[tuple[InputList, OutputList]] = run_grn(multiplier)
    structured_output_string: list[str] = to_structured_output_string(
        results,
        outputs_override=[f"M_Z{i}" for i in range(2*size)],
        pretty=True,
    )
    print("\n".join(structured_output_string))
    structured_output_string, accuracy = to_structured_output_multiplier_specific(
        simulation_results=results,
        operand_1_inputs=[f"M_X{i}" for i in reversed(range(size))],
        operand_2_inputs=[f"M_Y{i}" for i in reversed(range(size))],
        outputs=[f"M_Z{i}" for i in reversed(range(2*size))],
    )
    print("\n".join(structured_output_string))
    print(f"Accuracy: {accuracy*100:.1f}%")
    print()

def main():
    # Create & run n-bit multipliers
    for num_bits in [2, 3, 4]:
        print(f"{num_bits}-bit carry-save multiplier:")
        carry_save_multiplier: grn.grn = get_array_multiplier(size=num_bits, param_kd=5, param_n=3, param_alpha=10, param_delta=0.1)
        run_and_print_multiplier(num_bits, carry_save_multiplier)
        print(f"{num_bits}-bit array multiplier:")
        array_multiplier: grn.grn = get_carry_save_multiplier(size=num_bits, param_kd=5, param_n=3, param_alpha=10, param_delta=0.1)
        run_and_print_multiplier(num_bits, array_multiplier)

if __name__ == "__main__":
    main()

