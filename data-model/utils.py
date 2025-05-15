import json
import re
import pubchempy as pcp

# Partially copied and adapted from https://github.com/FAIRChemistry/substance-query/blob/main/substancewidget
# /substancewidget.py

# Regular expressions to differentiate between smiles code, inchi, and inchikey
RE_SMILES = re.compile(r"/^([^J][a-z0-9@+\-\[\]\(\)\\\/%=#$]{6,})$/ig")
RE_INCHI = re.compile(
    r"/^((InChI=)?[^J][0-9BCOHNSOPrIFla+\-\(\)\\\/,pqbtmsih]{6,})$/ig"
)
RE_INCHIKEY = re.compile(r"/^([0-9A-Z\-]+)$/")

# This data structure will store the PubChem compounds that have been queried, so that we don't have to query them again
cached_compounds = {}


def query_compound_from_pub_chem(query: str) -> pcp.Compound | None:
    """
    Query a compound using the PubChemPy library. The query can be a CID, SMILES, InChI, or InChIKey.
    :param query: The query string
    """
    if query in cached_compounds:
        return cached_compounds[query]

    match query:
        case query if query.isdigit():
            compound_options = [(pcp.Compound.from_cid(query))]
        case query if RE_SMILES.match(query):
            compound_options = pcp.get_compounds(query, "smiles")
        case query if RE_INCHI.match(query):
            compound_options = pcp.get_compounds(query, "inchi")
        case query if RE_INCHIKEY.match(query):
            compound_options = pcp.get_compounds(query, "inchikey")
        case _:
            compound_options = pcp.get_compounds(query, "name")

    # for now by default select first option
    if len(compound_options) > 0:
        compound = compound_options[0]
        cached_compounds[query] = compound
        return compound

    # Cache the compound
    cached_compounds[query] = None
    return None




def load_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def save_string_as_file(data: str, file_path):
    with open(file_path, 'wb') as f:
        f.write(data.encode('utf-8'))


def format_to_camel_case(text: str):
    if "_" in text or "-" in text:
        s = re.sub(r"(_|-)+", " ", text).title().replace(" ", "")
        return ''.join([s[0].lower(), s[1:]])
    else:
        return text

