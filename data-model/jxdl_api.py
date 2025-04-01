import json

from generated.jxdl_data_structure import JXDLSchema, Reagent, Synthesis, Role

class Product:
    def __init__(self, name: str, inchi: str|None, mass: str|None):
        self.name = name
        self.inchi = inchi
        self.mass = mass


def load_jxdl(file_path: str) -> JXDLSchema:
    with open(file_path, 'r') as f:
        data = json.load(f)
    return JXDLSchema.from_dict(data)


def get_synthesis_list(jxdl: JXDLSchema) -> list[Synthesis]:
    return jxdl.jxdl_schema_xdl.synthesis


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
    if not synthesis.metadata.product:
        return None
    return Product(synthesis.metadata.product, synthesis.metadata.product_inchi, synthesis.metadata.product_mass)


def find_corresponding_pxrd_file(synthesis: Synthesis, pxrd_file_folder: str) -> str | None:
    experiment_id = synthesis.metadata.description
    # todo
    return None
