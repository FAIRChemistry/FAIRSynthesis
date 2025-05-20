
def process_data_use_case_specific(data):
    # Process realization text
    process_realization_text(data)

    # Somehow the sciformation export messed up the inchi code for reagend DO. Fix it.
    fix_inchi_code_for_do(data)

    # Use more detailed reagent roles
    use_more_detailed_reagent_roles(data)

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
            # Search the realizationText with "acetone", "Et3N", "MeCN", "NaCl aq", "DMF", "CHCl3", "MeOH", and "EtOH" -> If they are not in the reagent list, add "WashSolid" with corresponding solvent after HeatChill.
            # If the realizationText contains "Soxhlet" or "open to air" -> Add "Wait" with 24 h (it varies in reality, but let's approximate so) as wait_after_rinse property.
            # Else -> Nothing
            solvents = ["acetone", "et3n", "mecn", "nacl aq", "dmf", "chcl3", "meoh", "etoh"]
            for solvent in solvents:
                if solvent in realization_text.lower() and not any(solvent in component['moleculeName'].lower() for component in item['reactionComponents']):
                    if 'rinse' not in item:
                        item['rinse'] = []
                    item['rinse'].append(solvent.lower())


            if "soxhlet" in realization_text.lower() or "open to air" in realization_text.lower():
                item['wait_after_rinse'] = 24
                item['wait_after_rinse_unit'] = "h"

            # scCO2:
            # If the realizationText contains "scCO<sub>2</sub>" or "scCO2" or "supercritical CO2" -> Add "scCO2" as wash_solid property.
            # If the realizationText contains "samples under fillers" or "MeOH filled up" -> Change "scCO2" into "MeOH+scCO2"
            if any(x in realization_text.lower() for x in ["supercritical co2", "scco<sub>2</sub>", "scco2"]):
                item['wash_solid'] = "scCO2"
            if any(x in realization_text.lower() for x in ["samples under fillers", "meoh filled up"]):
                item['wash_solid'] = "MeOH+scCO2"

            # Vacuum:
            # If the realizationText contains "Vacuum" after the text occurrence of "scCO" -> Add "Evaporate" as vacuum property.
            # Split text with scCO, so that it does not pick up the vacuum operation in the reaction preparation part
            # Else -> Nothing
            realization_text_parts = realization_text.split("scCO")
            if len(realization_text_parts) > 1:
                realization_text_after_scCO = realization_text_parts[1]
            else:
                realization_text_after_scCO = "" # realization_text
            if "vacuum" in realization_text_after_scCO.lower():
                item['evaporate'] = True

def fix_inchi_code_for_do(data):
    for item in data:
        for component in item['reactionComponents']:
            moleculeName = component['moleculeName']
            if moleculeName == "DO":
                component["inchi"] = "InChI=1S/C4H8O2/c1-2-6-4-3-5-1/h1-4H2"

def use_more_detailed_reagent_roles(data):
    # Use more detailed roles for the reaction component
    # we can further categorize the 'reagent'/'solvent' into 'catalyst', 'acid'.
    # It can be categorized with the InChI sum formula:
    # Acid:
    # C2H4O2
    # C5H10O2
    # C7H6O2
    # 3CHF3O3S.Sc
    # C6H5NO3
    # C6H4N2O5
    # C6H5BrO
    # C6H4ClNO3
    # C7H5NO
    # C7H4N2O6
    # C6HF5O
    # C2HF3O2
    #
    # Catalyst:
    # H2O
    # C6H6BrN
    # C6H6N2O2
    # C4H9N
    #
    # Others stay as reagents
    for item in data:
        for component in item['reactionComponents']:
            if component['rxnRole'] == 'reagent' or component['rxnRole'] == 'solvent':
                if component['empFormula'] in ['C2H4O2', 'C5H10O2', 'C7H6O2', '3CHF3O3S.Sc', 'C6H5NO3', 'C6H4N2O5', 'C6H5BrO', 'C6H4ClNO3', 'C7H5NO', 'C7H4N2O6', 'C6HF5O', 'C2HF3O2']:
                    component['rxnRole'] = "acid"
                elif component['empFormula'] in ['H2O', 'C6H6BrN', 'C6H6N2O2', 'C4H9N']:
                    component['rxnRole'] = "catalyst"