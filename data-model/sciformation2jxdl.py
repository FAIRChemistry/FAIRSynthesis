import os
from typing import List
from jsonschema import validate

from generated.jxdl_data_structure import JXDLSchema, Synthesis, Reagent, StepClass, Hardware, Metadata, \
    Procedure, Reagents, Xdl, XDLClass, XMLType, Characterization, XRaySource, SampleHolder, TypeEnum
from generated.sciformation_eln_cleaned_data_structure import SciformationCleanedELNSchema, RxnRole, \
    Experiment, ReactionComponent
from jxdl_utils import rxn_role_to_xdl_role
from sciformation_cleaned_utils import find_reaction_components, get_inchi, format_time, format_temperature, \
    format_mass, format_amount
from sciformation_cleaner import clean_sciformation_eln
from utils import load_json, save_json
from pxrd_collector import collect_pxrd_files, filter_pxrd_files


def convert_cleaned_eln_to_jxdl(eln: SciformationCleanedELNSchema, default_code: str = "KE") -> JXDLSchema:
    synthesis_list: List[Synthesis] = []
    pxrd_files = collect_pxrd_files(os.path.join('..', 'data', 'PXRD'))

    for experiment in eln.experiments:
        reaction_product = find_reaction_components(experiment, RxnRole.PRODUCT)[0]
        reaction_product_mass = format_mass(reaction_product.mass, reaction_product.mass_unit)
        reaction_product_inchi = get_inchi(reaction_product)
        reagents: List[Reagent] = construct_reagents(experiment.reaction_components)
        steps: List[StepClass] = construct_steps(experiment)
        # pad the experiment nr in lab journal to a length of 3 digits, adding preceding zeros
        experiment_nr = str(experiment.nr_in_lab_journal).zfill(3)
        experiment_id = (experiment.code if experiment.code else default_code) + "-" + experiment_nr

        product_characterizations: List[Characterization] = [Characterization(
            weight=reaction_product_mass,
            relative_file_path=None,
            sample_holder=None,
            x_ray_source=None
        )]

        experiment_pxrd_files = filter_pxrd_files(experiment_id, pxrd_files)
        if experiment_pxrd_files:
            for pxrd_file in experiment_pxrd_files:
                x_ray_source = XRaySource[pxrd_file.xray_source.replace(" ", "_").replace("-", "_").upper()]
                sample_holder: SampleHolder = SampleHolder(
                    diameter=pxrd_file.sample_holder_diameter,
                    type=TypeEnum[pxrd_file.sample_holder_shape.replace("film","KAPTON_FILMS").replace("capillary","HILGENBERG_GLASS_NO_14_CAPILLARY")]
                )
                product_characterizations.append(Characterization(
                    weight=None,
                    relative_file_path=pxrd_file.path,
                    sample_holder=sample_holder,
                    x_ray_source=x_ray_source
                ))

        synthesis = Synthesis(
            hardware=Hardware(text="todo"),
            metadata= Metadata(
                description= experiment_id,
                product= None,
                product_inchi= None
            ),
            procedure= Procedure(
                steps
                ),
            reagents= Reagents(reagents),
            product_characterization = product_characterizations
        )
        synthesis_list.append(synthesis)

    return JXDLSchema(
        xdl = Xdl("1.0.0"),
        jxdl_schema_xdl= XDLClass(synthesis_list)
    )



def construct_steps(experiment: Experiment) -> List[StepClass]:
    vessel: str = str(experiment.vessel.value)
    steps = []
    # First create steps with type Add for all components that are not products
    for component in experiment.reaction_components:
        amount = format_amount(component.amount)
        if component.rxn_role != RxnRole.PRODUCT:
            steps.append(
                StepClass(XMLType.ADD, amount=amount, reagent=component.molecule_name, stir=None, temp=None, time=None, vessel=vessel, gas=None, solvent=None)
            )

    if experiment.degassing:
        steps.append(
            StepClass(XMLType.EVACUATE_AND_REFILL, temp=None, time=None, amount=None, reagent=None, stir=None, vessel=vessel, gas=experiment.degassing.value, solvent=None)
        )

    time: str = format_time(experiment.duration, experiment.duration_unit)
    temp: str = format_temperature(experiment.temperature)
    steps.append(
        StepClass(XMLType.HEAT_CHILL, temp=temp, time=time, amount=None, reagent=None, stir=None, vessel=vessel, gas=None, solvent=None)
    )

    if experiment.rinse:
        steps.append(
            StepClass(XMLType.WASH_SOLID, temp=None, time=None, amount=None, reagent=None, stir=None, vessel=vessel, gas=None, solvent=experiment.rinse.value)
        )

    if experiment.wait_after_rinse:
        wait_time: str = format_time(str(experiment.wait_after_rinse), experiment.wait_after_rinse_unit)
        steps.append(
            StepClass(XMLType.WAIT, temp=None, time=wait_time, amount=None, reagent=None, stir=None, vessel=vessel, gas=None, solvent=None)
        )

    if experiment.wash_solid:
        steps.append(
            StepClass(XMLType.WASH_SOLID, temp=None, time=None, amount=None, reagent=None, stir=None, vessel=vessel, gas=None, solvent=experiment.wash_solid.value)
        )

    if experiment.evaporate:
        steps.append(
            StepClass(XMLType.EVAPORATE, temp=None, time=None, amount=None, reagent=None, stir=None, vessel=vessel, gas=None, solvent=None)
        )

    return steps


def construct_reagents(reaction_components: List[ReactionComponent]) -> List[Reagent]:
    reagents = []
    for component in reaction_components:

        role = rxn_role_to_xdl_role(component.rxn_role)
        inchi = get_inchi(component)
        cas = component.cas_nr

        if component.rxn_role != RxnRole.PRODUCT:
            reagent = Reagent(
                inchi=inchi,
                name=component.molecule_name,
                role=role,
                purity=None,
                id = component.molecule_name,
                cas=cas
            )


            reagents.append(reagent)

    return reagents



if __name__ == '__main__':
    file_path = os.path.join('..', 'data', 'Sciformation_KE-MOCOF_jsonRaw.json')
    cleaned_eln = clean_sciformation_eln(load_json(file_path))
    print("Cleaned data: " + str(cleaned_eln))

    # Validate data according to schema
    validate(instance=cleaned_eln, schema=load_json(os.path.join('schemas', 'sciformation_eln_cleaned.schema.json')))

    jxdl = convert_cleaned_eln_to_jxdl(SciformationCleanedELNSchema.from_dict(cleaned_eln))
    result_file_path = os.path.join('..', 'data', 'generated', 'jxdl.json')
    result_dict = jxdl.to_dict()
    print("JXDL Result: " + str(result_dict))
    save_json(result_dict, result_file_path)



