from typing import List

from sympy import sympify

from generated.sciformation_eln_cleaned_data_structure import RxnRole, DurationUnit, Experiment, \
    ReactionComponent, MassUnit
from utils import query_compound_from_pub_chem


cached_inchis = {}

def get_inchi(reaction_component: ReactionComponent) -> str | None:
    if reaction_component.inchi:
        return reaction_component.inchi

    if reaction_component.smiles in cached_inchis:
        inchi = cached_inchis[reaction_component.smiles]
        if inchi == "None":
            return None
        return inchi

    result = "None"

    if reaction_component.smiles:
        pub_chem_compound = query_compound_from_pub_chem(reaction_component.smiles)
        if pub_chem_compound:
            result = pub_chem_compound.inchi

    cached_inchis[reaction_component.smiles] = result
    return result

def time_to_seconds(time: float, time_unit: DurationUnit) -> float:
    if time_unit == DurationUnit.S:
        return time
    elif time_unit == DurationUnit.M:
        return time * 60
    elif time_unit == DurationUnit.H:
        return time * 3600
    elif time_unit == DurationUnit.D:
        return time * 86400
    else:
        return time

def mass_to_gram(mass: float, mass_unit: MassUnit) -> float:
    if mass_unit == MassUnit.G:
        return mass
    else:
        raise ValueError("Unknown mass unit")

def find_reaction_components(experiment: Experiment, rxn_type: RxnRole) -> List[ReactionComponent]:
    results = []
    for component in experiment.reaction_components:
        if component.rxn_role.value == rxn_type.value:
            results.append(component)
    return results

def format_temperature(temp: str) -> str:
    temperature_string: str = temp.replace("RT", "25")
    if "->" in temperature_string: # if temperature is a range
        start_temp: float = float(sympify(temperature_string.split("->")[0]))
        end_temp: float = float(sympify(temperature_string.split("->")[1]))
        return str(start_temp) + " -> " + str(end_temp) + " C"
    else:
        temp: float = float(sympify(temperature_string))
        return str(temp) + " C"

def format_mass(mass: float, mass_unit: MassUnit) -> str:
    return str(mass_to_gram(mass, mass_unit)) + " g"

def format_time(time: str, time_unit: DurationUnit) -> str:
    return str(time_to_seconds(float(sympify(time)), time_unit)) + " s"