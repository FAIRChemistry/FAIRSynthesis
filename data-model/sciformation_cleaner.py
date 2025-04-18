import os
from datetime import datetime


from utils import format_to_camel_case, load_json, save_json
from use_case_specific.sciformation_cleaner_mocof1 import process_data_use_case_specific

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

    # Process the data according to the current use-case
    process_data_use_case_specific(postprocessed_data)

    if max_entry_length > 0:
        postprocessed_data = postprocessed_data[:min(max_entry_length, len(postprocessed_data))]

    result = {
        "experiments": postprocessed_data
    }

    return result


if __name__ == '__main__':
    # Can be run independently to test the function
    file_path = os.path.join('..', 'data', 'Sciformation_KE-MOCOF_jsonRaw.json')
    result_file_path = os.path.join('..', 'data', 'generated', 'sciformation_eln_cleaned.json')

    data = load_json(file_path)
    result = clean_sciformation_eln(data)
    save_json(result, result_file_path)