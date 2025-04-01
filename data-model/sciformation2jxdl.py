import os
from typing import List

from generated.jxdl_data_structure import JXDLSchema, Synthesis, Reagent, StepClass, Hardware, Metadata, \
    Procedure, Reagents, Xdl, XDLClass, XMLType
from generated.sciformation_eln_cleaned_data_structure import SciformationCleanedELNSchema, RxnRole, \
    Experiment, ReactionComponent
from jxdl_utils import rxn_role_to_xdl_role
from sciformation_cleaned_utils import find_reaction_components, get_inchi, format_time, format_temperature, \
    format_mass, format_amount
from sciformation_cleaner import clean_sciformation_eln
from utils import load_json, save_json


def convert_cleaned_eln_to_jxdl(eln: SciformationCleanedELNSchema, default_code: str = "KE") -> JXDLSchema:
    synthesis_list: List[Synthesis] = []

    for experiment in eln.experiments:
        reaction_product = find_reaction_components(experiment, RxnRole.PRODUCT)[0]
        reaction_product_mass = format_mass(reaction_product.mass, reaction_product.mass_unit)
        reaction_product_inchi = get_inchi(reaction_product)
        reagents: List[Reagent] = construct_reagents(experiment.reaction_components)
        steps: List[StepClass] = construct_steps(experiment)
        # pad the experiment nr in lab journal to a length of 3 digits, adding preceding zeros
        experiment_nr = str(experiment.nr_in_lab_journal).zfill(3)
        experiment_id = (experiment.code if experiment.code else default_code) + "-" + experiment_nr

        synthesis = Synthesis(
            hardware=Hardware(text="todo"),
            metadata= Metadata(
                description= experiment_id,
                product= None,
                product_inchi= None,
                product_mass= str(reaction_product_mass)
            ),
            procedure= Procedure(
                steps
                ),
            reagents= Reagents(reagents)
        )
        synthesis_list.append(synthesis)

    return JXDLSchema(
        Xdl("1.0.0"),
        XDLClass(synthesis_list)
    )



def construct_steps(experiment: Experiment) -> List[StepClass]:
    steps = []
    # First create steps with type Add for all components that are not products
    for component in experiment.reaction_components:
        amount = format_amount(component.amount)
        if component.rxn_role != RxnRole.PRODUCT:
            steps.append(
                StepClass(XMLType.ADD, amount=amount, reagent=component.molecule_name, stir=None, temp=None, time=None)
            )

    time: str = format_time(experiment.duration, experiment.duration_unit)
    temp: str = format_temperature(experiment.temperature)
    steps.append(
        StepClass(XMLType.HEAT_CHILL, temp=temp, time=time, amount=None, reagent=None, stir=None)
    )

    return steps


def construct_reagents(reaction_components: List[ReactionComponent]) -> List[Reagent]:
    reagents = []
    for component in reaction_components:

        role = rxn_role_to_xdl_role(component.rxn_role)
        inchi = get_inchi(component)

        if component.rxn_role != RxnRole.PRODUCT:
            reagent = Reagent(
                inchi=inchi,
                name=component.molecule_name,
                role=role,
                purity=None,
                id = component.molecule_name
            )


            reagents.append(reagent)

    return reagents



if __name__ == '__main__':
    file_path = os.path.join('..', 'data', 'KE-TAPP TPA 203exp.json')
    cleaned_eln = clean_sciformation_eln(load_json(file_path))
    print("Cleaned data: " + str(cleaned_eln))
    jxdl = convert_cleaned_eln_to_jxdl(SciformationCleanedELNSchema.from_dict(cleaned_eln))
    result_file_path = os.path.join('..', 'data', 'generated', 'jxdl.json')
    result_dict = jxdl.to_dict()
    print("JXDL Result: " + str(result_dict))
    save_json(result_dict, result_file_path)



