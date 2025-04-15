import os
from datetime import datetime


from utils import format_to_camel_case, load_json, save_json

important_item_attributes = [
    '@id',
    'nrInLabJournal',
    'creator',
    'code',
    'modifier'
    'reactionTitle',
    'reactionStartedWhen',
    'realizationText',
    'observationText',
]

important_reaction_properties = [
    'duration',
    'reaction_mass_unit',
    'reaction_volume_unit',
    'solventAmount'
    'solvent_volume_unit',
    'temperature'
]

important_reaction_component_attributes = [
    'moleculeName',
    'casNr',
    'mw',
    'empFormula',
    'concentration',
    'concentrationUnit',
    'smiles',
    'smilesStereo',
    'inchi',
    'inchiKey',
    'density20',
    'rxnRole',
    'mass',
    'massUnit',
    'volume',
    'volumeUnit',
    'amount',
    'amountUnit',
    'measured'
    'elnReaction'
    'cdbMolecule'
    'rxnRole',
    'labNotebookEntryAndRole'
]

rxnRoleMapping = {
    1: 'reactant',
    2: 'reagent',
    3: 'solvent',
    6: 'product'
}

def clean_data(data):
    trimmed_data = []
    for item in data:
        result = clean_item(item)
        if result:
            trimmed_data.append(result)
    return trimmed_data

def clean_item(item):
    new_item = {}
    for key, value in item.items():
        if key in important_item_attributes and value is not None:
            new_item[format_to_camel_case(key)] = value

    elnReactionPropertyCollection = item.get('elnReactionPropertyCollection', [])
    if elnReactionPropertyCollection:
        for reactionProperty in elnReactionPropertyCollection:
            if reactionProperty.get('name') in important_reaction_properties and reactionProperty.get('strValue') is not None:
                new_item[format_to_camel_case(reactionProperty.get('name'))] = reactionProperty.get('strValue')

    elnReactionComponentCollection = item.get('elnReactionComponentCollection', [])
    if elnReactionComponentCollection:
        reaction_components = []
        for reactionComponent in elnReactionComponentCollection:
            new_component = {}
            for key, value in reactionComponent.items():
                if key in important_reaction_component_attributes and value is not None:
                    new_component[key] = value
            reaction_components.append(new_component)
        new_item['reactionComponents'] = reaction_components

    return new_item


def apply_conversions(data):
    # convert rxnRole int to string
    for item in data:
        for component in item['reactionComponents']:
            component['rxnRole'] = rxnRoleMapping.get(component['rxnRole'], 'unknown')
            # sciformation always exports mass in g, even if different unit is selected in the ELN
            component['massUnit'] = 'g'

        item['durationUnit'] = 'h'
        item['temperatureUnit'] = 'C'
        if 'reactionStartedWhen' in item:
            # for reaction start, convert original ms to formatted date
            start_date = datetime.fromtimestamp(item['reactionStartedWhen'] / 1000)
            item['reactionStartedWhen'] = start_date.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return data


def clean_sciformation_eln(data: dict, max_entry_length: int = -1) -> dict:
    trimmed_data = clean_data(data)
    postprocessed_data = apply_conversions(trimmed_data)

    # Process the realization text to read out additional information from the text.
    process_realization_text(postprocessed_data)

    if max_entry_length > 0:
        postprocessed_data = postprocessed_data[:min(max_entry_length, len(postprocessed_data))]

    result = {
        "experiments": postprocessed_data
    }

    return result

def process_realization_text(data):
    # Process the realization text to read out additional information from the text.
    # Use case-insensitive search for words.
    # First, use the realization text only until "XRD" to avoid getting irrelevant information.
    #

    for item in data:
        if 'realizationText' in item:
            realization_text = item['realizationText']
            # Split the realization text at "XRD" and take the first part
            realization_text = realization_text.split("XRD")[0].strip()

            # Reaction vessel:
            # If the realizationText contains "microwave vial" -> Assign "microwave vial" as vessel
            # Else if the realizationText contains "pressure tube" or "J. Young tube" or "Schlenk bomb" -> Assign "Schlenk bomb" as vessel
            # Else -> raise exception
            if "microwave vial" in realization_text.lower():
                item['vessel'] = "microwave vial"
            elif any(x in realization_text.lower() for x in ["pressure tube", "j. young tube", "schlenk bomb"]):
                item['vessel'] = "Schlenk bomb"
            else:
                raise ValueError("Unknown reaction vessel")

            # Degassing:
            # If the realizationText contains "FPT" or "Ar replace" -> Add "Ar" gas as degassing property
            # Else -> Nothing
            if "fpt" in realization_text.lower() or "ar replace" in realization_text.lower():
                item['degassing'] = "Ar"

            # Rinse:
            # Search the realizationText with "acetone", "Et3N", "MeCN", "NaCl aq", "DMF", "CHCl3", "MeOH", and "EtOH" -> If they are not in the reagent list, add "WashSolid" with corresponding solvent as rinse property
            # Add only the solvents which appear in the realizationText and are not already in the reagent list, not all solvents from the list. Raise Error if it is multiple solvents.
            # If the realizationText contains "Soxhlet" or "open to air" -> Add "Wait" with 24 h (it varies in reality, but let's approximate so) as wait_after_rinse property.
            # Else -> Nothing
            solvents = ["acetone", "et3n", "mecn", "nacl aq", "dmf", "chcl3", "meoh", "etoh"]
            for solvent in solvents:
                if solvent in realization_text.lower() and not any(solvent in component['moleculeName'].lower() for component in item['reactionComponents']):
                    if 'rinse' not in item:
                        item['rinse'] = solvent.lower()
                    else:
                        raise ValueError(f"Multiple solvents found in realization text: {item['rinse']} and {solvent}")
                    break

            if "soxhlet" in realization_text.lower() or "open to air" in realization_text.lower():
                item['wait_after_rinse'] = 24
                item['wait_after_rinse_unit'] = "h"

            # scCO2:
            # If the realizationText contains "supercritical CO2" or "scCO2" or "scCO2" -> Add "scCO2" as wash_solid property.
            # If the realizationText contains "samples under fillers" or "MeOH filled up" -> Change "scCO2" into "MeOH+scCO2"
            if any(x in realization_text.lower() for x in ["supercritical co2", "scco2"]):
                item['wash_solid'] = "scCO2"
            if any(x in realization_text.lower() for x in ["samples under fillers", "meoh filled up"]):
                item['wash_solid'] = "MeOH+scCO2"

            # Vacuum:
            # If the realizationText contains "Vacuum" after "scCO" -> Add "Evaporate" as vacuum property
            # Else -> Nothing
            if "vacuum" in realization_text.lower():
                item['evaporate'] = True


if __name__ == '__main__':
    # Can be run independently to test the function
    file_path = os.path.join('..', 'data', 'Sciformation_KE-MOCOF_jsonRaw.json')
    result_file_path = os.path.join('..', 'data', 'generated', 'sciformation_eln_cleaned.json')

    data = load_json(file_path)
    result = clean_sciformation_eln(data)
    save_json(result, result_file_path)