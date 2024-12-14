from typing import TypeAlias
import grn
from src.parser import SpeciesList

ConnectionType: TypeAlias = tuple[grn.grn, str, grn.grn, str]
LabeledGRN: TypeAlias = tuple[grn.grn, str]

def synthesize(
        named_grns: list[LabeledGRN],      # source GRN, output name, destination GRN, input name
        connections: list[ConnectionType], # GRN, name
        inputs: dict[str, LabeledGRN],     # synthesized input |-> (grn, grn input)
        outputs: dict[str, LabeledGRN],    # synthesized output |-> (grn, grn output)
    ) -> grn.grn:

    synthesized: grn.grn = grn.grn()
    grn_to_name: dict[grn.grn, str] = {grn: name for grn, name in named_grns}
    regulators: SpeciesList
    products: SpeciesList
    grn_name: str

    # Replicate layout from lower level GRNs
    for grn_, grn_name in named_grns:
        # Add species
        for species_name in grn_.species_names:
            synthesized.add_species(f"{grn_name}_{species_name}", 0.1)            
        # Add genes
        for gene in grn_.genes:
            alpha: float = gene["alpha"]
            regulators = gene["regulators"]
            products = gene["products"]
            regulators = [{**regulator, "name": f"{grn_name}_{regulator['name']}"} for regulator in regulators]     # Set deltas to 0?
            products = [{**product, "name": f"{grn_name}_{product['name']}"} for product in products]
            synthesized.add_gene(alpha, regulators, products)

    # Create connections
    for src_grn, output_name, dst_grn, input_name in connections:
        src_grn_name: str = grn_to_name[src_grn]
        dst_grn_name: str = grn_to_name[dst_grn]
        regulators = [{"name": f"{src_grn_name}_{output_name}", "type": 1, "Kd": 5, "n": 2}]
        products = [{"name": f"{dst_grn_name}_{input_name}"}]
        synthesized.add_gene(10, regulators, products)

    # Create inputs and connect them to inner GRNs
    for input_name, (grn_, grn_input) in inputs.items():
        grn_name = grn_to_name[grn_]
        synthesized.add_input_species(input_name)
        regulators = [{"name": input_name, "type": 1, "Kd": 5, "n": 2}]
        products = [{"name": f"{grn_name}_{grn_input}"}]
        synthesized.add_gene(10, regulators, products)

    # Create outputs and connect them to inner GRNs
    for output_name, (grn_, grn_output) in outputs.items():
        grn_name = grn_to_name[grn_]
        synthesized.add_species(output_name, 0.1)
        regulators = [{"name": f"{grn_name}_{grn_output}", "type": 1, "Kd": 5, "n": 2}]
        products = [{"name": output_name}]
        synthesized.add_gene(10, regulators, products)

    return synthesized

