from typing import TypeAlias
import grn
from src.parser import SpeciesList

ConnectionType: TypeAlias = tuple[grn.grn, str, grn.grn, str]
LabeledGRN: TypeAlias = tuple[grn.grn, str]

def synthesize(
        named_grns: list[LabeledGRN],        # GRN, name
        connections: list[ConnectionType],   # source GRN, output name, destination GRN, input name
        inputs: list[LabeledGRN],            # (grn, grn input)
    ) -> grn.grn:

    synthesized: grn.grn = grn.grn()
    grn_to_name: dict[grn.grn, str] = {grn: name for grn, name in named_grns}
    regulators: SpeciesList
    products: SpeciesList
    grn_name: str

    # Replicate layout from lower level GRNs
    # We HAVE TO add the inputs before all else
    # Necessary for correct ordering in synthesized.input_species_names and synthesized.species_names
    for grn_, input_name in inputs:
        grn_name = grn_to_name[grn_]
        synthesized.add_input_species(f"{grn_name}_{input_name}")
    # Now add the other (non-input) species
    for grn_, grn_name in named_grns:
        for species_name in grn_.species_names:
            if not (grn_, species_name) in inputs:
                synthesized.add_species(f"{grn_name}_{species_name}", 0.1)
    # Finally, add the genes
    for grn_, grn_name in named_grns:
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

    return synthesized

