
from generated.jxdl_data_structure import Role, JXDLSchema, Reagent, Synthesis
from generated.sciformation_eln_cleaned_data_structure import RxnRole


def rxn_role_to_xdl_role(rnx_role: RxnRole) -> Role | None:
    if rnx_role == RxnRole.REACTANT:
        return Role.SUBSTRATE
    elif rnx_role == RxnRole.SOLVENT:
        return Role.SOLVENT
    elif rnx_role == RxnRole.PRODUCT:
        return None
    elif rnx_role == RxnRole.REAGENT:
        return Role.REAGENT
    elif rnx_role == RxnRole.CATALYST:
        return Role.CATALYST
    elif rnx_role == RxnRole.ACID:
        return Role.ACID
    else:
        raise ValueError(f"Unknown reaction role: {rnx_role}")
