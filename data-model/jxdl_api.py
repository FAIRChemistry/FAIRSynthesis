import json
from typing import List

from generated.jxdl_data_structure import JXDLSchema, Reagent, Synthesis, Role
from pxrd_collector import PXRDFile

class Product:
    def __init__(self, name: str, mass: str|None, pxrd_files: List[PXRDFile]):
        self.name = name
        self.mass = mass
        self.pxrd_files = pxrd_files


def load_jxdl(file_path: str) -> JXDLSchema:
    with open(file_path, 'r') as f:
        data = json.load(f)
    return JXDLSchema.from_dict(data)


def get_synthesis_list(jxdl: JXDLSchema) -> list[Synthesis]:
    return jxdl.jxdl_schema_xdl.synthesis


def get_synthesis_by_experiment_id(jxdl: JXDLSchema, experiment_id: str) -> Synthesis | None:
    for synthesis in jxdl.jxdl_schema_xdl.synthesis:
        if synthesis.metadata.description == experiment_id:
            return synthesis
    return None

def find_reagent_by_name(synthesis: Synthesis, reagent_name: str) -> Reagent | None:
    for reagent in synthesis.reagents.reagent:
        if reagent.name == reagent_name:
            return reagent
    return None


def find_reagents_by_role(synthesis: Synthesis, role: Role) -> list[Reagent]:
    results = []
    for reagent in synthesis.reagents.reagent:
        if reagent.role.value == role.value:
            results.append(reagent)
    return results


def find_product(synthesis: Synthesis) -> Product | None:
    product_name = synthesis.metadata.product if synthesis.metadata.product else "unknown"
    product_mass = find_product_mass(synthesis)
    pxrd_files = find_corresponding_pxrd_files(synthesis)
    return Product(product_name, product_mass, pxrd_files)


def find_corresponding_pxrd_files(synthesis: Synthesis) -> List[PXRDFile]:
    result = []
    for characterization in synthesis.product_characterization:
        if characterization.relative_file_path and characterization.x_ray_source and characterization.sample_holder and synthesis.metadata.description:
                result.append(PXRDFile(
                    characterization.relative_file_path
                ))
    return result


def find_product_mass(synthesis: Synthesis) -> str | None:
    # Filter characterizations by whether they have the weight attribute
    mass_characterizations = [c for c in synthesis.product_characterization if c.weight]
    if mass_characterizations:
        # Return the weight of the first characterization that has it
        return mass_characterizations[0].weight
    return None


def print_synthesis_data(synthesis: Synthesis):
    print(f"Synthesis ID: {synthesis.metadata.description}")
    print_reagents(synthesis)
    print_procedure(synthesis)
    product = find_product(synthesis)
    if product:
        print_product(product)

def print_reagents(synthesis: Synthesis):
    print("Reagents:")
    for reagent in synthesis.reagents.reagent:
        print(f" - {reagent.name} (Role: {reagent.role.value})")

def print_procedure(synthesis: Synthesis):
    print("Procedure:")
    # The procedure either has all steps in the "step" array, or it is split into "prep", "reaction", and "workup"
    if synthesis.procedure.step:
        for step in synthesis.procedure.step:
            print(f" -(Type: {step.xml_type}, Amount: {step.amount}, Reagent: {step.reagent}, Stir: {step.stir}, Temp: {step.temp}, Time: {step.time})")
    else:
        if synthesis.procedure.prep:
            print("Prep Steps:")
            for step in synthesis.procedure.prep:
                print(f" -(Type: {step.xml_type}, Amount: {step.amount}, Reagent: {step.reagent}, Stir: {step.stir}, Temp: {step.temp}, Time: {step.time})")
        if synthesis.procedure.reaction:
            print("Reaction Steps:")
            for step in synthesis.procedure.reaction:
                print(f" -(Type: {step.xml_type}, Amount: {step.amount}, Reagent: {step.reagent}, Stir: {step.stir}, Temp: {step.temp}, Time: {step.time})")
        if synthesis.procedure.workup:
            print("Workup Steps:")
            for step in synthesis.procedure.workup:
                print(f" -(Type: {step.xml_type}, Amount: {step.amount}, Reagent: {step.reagent}, Stir: {step.stir}, Temp: {step.temp}, Time: {step.time})")

def print_product(product: Product):
    if product:
        print(f"Product Name: {product.name}")
        print(f"Product Mass: {product.mass}")
        print("PXRD Files:")
        for pxrd_file in product.pxrd_files:
            print(f" - {pxrd_file.path}")
            print(f"   Experiment ID: {pxrd_file.experiment_id}")
            print(f"   X-ray Source: {pxrd_file.xray_source}")
            print(f"   Sample Holder Shape: {pxrd_file.sample_holder_shape}")
            print(f"   Sample Holder Diameter: {pxrd_file.sample_holder_diameter}")
