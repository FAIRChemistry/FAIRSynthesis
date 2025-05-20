from enum import Enum
from typing import Optional, Any, List, TypeVar, Type, Callable, cast
from datetime import datetime
import dateutil.parser


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def to_float(x: Any) -> float:
    assert isinstance(x, (int, float))
    return x


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class Degassing(Enum):
    AR = "Ar"


class Unit(Enum):
    D = "d"
    H = "h"
    M = "m"
    S = "s"


class AmountUnit(Enum):
    MMOL = "mmol"
    MOL = "mol"
    ΜMOL = "µmol"


class ConcentrationUnit(Enum):
    EMPTY = "%"
    G_L = "g/l"
    MG_L = "mg/l"
    MMOL_L = "mmol/l"
    MOL_L = "mol/l"
    NMOL_L = "nmol/l"
    ΜG_L = "µg/l"
    ΜMOL_L = "µmol/l"


class MassUnit(Enum):
    G = "g"


class RxnRole(Enum):
    ACID = "acid"
    CATALYST = "catalyst"
    PRODUCT = "product"
    REACTANT = "reactant"
    REAGENT = "reagent"
    SOLVENT = "solvent"


class VolumeUnit(Enum):
    CM = "cm³"
    DM = "dm³"
    L = "l"
    ML = "ml"
    ΜL = "µl"


class ReactionComponent:
    amount: Optional[float]
    amount_unit: Optional[AmountUnit]
    cas_nr: Optional[str]
    concentration: Optional[float]
    concentration_unit: Optional[ConcentrationUnit]
    density20: Optional[float]
    emp_formula: str
    inchi: Optional[str]
    inchi_key: Optional[str]
    lab_notebook_entry_and_role: Optional[str]
    mass: Optional[float]
    mass_unit: Optional[MassUnit]
    molecule_name: str
    mw: Optional[float]
    rxn_role: RxnRole
    smiles: str
    smiles_stereo: Optional[str]
    volume: Optional[float]
    volume_unit: Optional[VolumeUnit]

    def __init__(self, amount: Optional[float], amount_unit: Optional[AmountUnit], cas_nr: Optional[str], concentration: Optional[float], concentration_unit: Optional[ConcentrationUnit], density20: Optional[float], emp_formula: str, inchi: Optional[str], inchi_key: Optional[str], lab_notebook_entry_and_role: Optional[str], mass: Optional[float], mass_unit: Optional[MassUnit], molecule_name: str, mw: Optional[float], rxn_role: RxnRole, smiles: str, smiles_stereo: Optional[str], volume: Optional[float], volume_unit: Optional[VolumeUnit]) -> None:
        self.amount = amount
        self.amount_unit = amount_unit
        self.cas_nr = cas_nr
        self.concentration = concentration
        self.concentration_unit = concentration_unit
        self.density20 = density20
        self.emp_formula = emp_formula
        self.inchi = inchi
        self.inchi_key = inchi_key
        self.lab_notebook_entry_and_role = lab_notebook_entry_and_role
        self.mass = mass
        self.mass_unit = mass_unit
        self.molecule_name = molecule_name
        self.mw = mw
        self.rxn_role = rxn_role
        self.smiles = smiles
        self.smiles_stereo = smiles_stereo
        self.volume = volume
        self.volume_unit = volume_unit

    @staticmethod
    def from_dict(obj: Any) -> 'ReactionComponent':
        assert isinstance(obj, dict)
        amount = from_union([from_float, from_none], obj.get("amount"))
        amount_unit = from_union([AmountUnit, from_none], obj.get("amountUnit"))
        cas_nr = from_union([from_str, from_none], obj.get("casNr"))
        concentration = from_union([from_float, from_none], obj.get("concentration"))
        concentration_unit = from_union([ConcentrationUnit, from_none], obj.get("concentrationUnit"))
        density20 = from_union([from_float, from_none], obj.get("density20"))
        emp_formula = from_str(obj.get("empFormula"))
        inchi = from_union([from_str, from_none], obj.get("inchi"))
        inchi_key = from_union([from_str, from_none], obj.get("inchiKey"))
        lab_notebook_entry_and_role = from_union([from_str, from_none], obj.get("labNotebookEntryAndRole"))
        mass = from_union([from_float, from_none], obj.get("mass"))
        mass_unit = from_union([MassUnit, from_none], obj.get("massUnit"))
        molecule_name = from_str(obj.get("moleculeName"))
        mw = from_union([from_float, from_none], obj.get("mw"))
        rxn_role = RxnRole(obj.get("rxnRole"))
        smiles = from_str(obj.get("smiles"))
        smiles_stereo = from_union([from_str, from_none], obj.get("smilesStereo"))
        volume = from_union([from_float, from_none], obj.get("volume"))
        volume_unit = from_union([VolumeUnit, from_none], obj.get("volumeUnit"))
        return ReactionComponent(amount, amount_unit, cas_nr, concentration, concentration_unit, density20, emp_formula, inchi, inchi_key, lab_notebook_entry_and_role, mass, mass_unit, molecule_name, mw, rxn_role, smiles, smiles_stereo, volume, volume_unit)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.amount is not None:
            result["amount"] = from_union([to_float, from_none], self.amount)
        if self.amount_unit is not None:
            result["amountUnit"] = from_union([lambda x: to_enum(AmountUnit, x), from_none], self.amount_unit)
        if self.cas_nr is not None:
            result["casNr"] = from_union([from_str, from_none], self.cas_nr)
        if self.concentration is not None:
            result["concentration"] = from_union([to_float, from_none], self.concentration)
        if self.concentration_unit is not None:
            result["concentrationUnit"] = from_union([lambda x: to_enum(ConcentrationUnit, x), from_none], self.concentration_unit)
        if self.density20 is not None:
            result["density20"] = from_union([to_float, from_none], self.density20)
        result["empFormula"] = from_str(self.emp_formula)
        if self.inchi is not None:
            result["inchi"] = from_union([from_str, from_none], self.inchi)
        if self.inchi_key is not None:
            result["inchiKey"] = from_union([from_str, from_none], self.inchi_key)
        if self.lab_notebook_entry_and_role is not None:
            result["labNotebookEntryAndRole"] = from_union([from_str, from_none], self.lab_notebook_entry_and_role)
        if self.mass is not None:
            result["mass"] = from_union([to_float, from_none], self.mass)
        if self.mass_unit is not None:
            result["massUnit"] = from_union([lambda x: to_enum(MassUnit, x), from_none], self.mass_unit)
        result["moleculeName"] = from_str(self.molecule_name)
        if self.mw is not None:
            result["mw"] = from_union([to_float, from_none], self.mw)
        result["rxnRole"] = to_enum(RxnRole, self.rxn_role)
        result["smiles"] = from_str(self.smiles)
        if self.smiles_stereo is not None:
            result["smilesStereo"] = from_union([from_str, from_none], self.smiles_stereo)
        if self.volume is not None:
            result["volume"] = from_union([to_float, from_none], self.volume)
        if self.volume_unit is not None:
            result["volumeUnit"] = from_union([lambda x: to_enum(VolumeUnit, x), from_none], self.volume_unit)
        return result


class TemperatureUnit(Enum):
    C = "C"


class Vessel(Enum):
    MICROWAVE_VIAL = "microwave vial"
    SCHLENK_BOMB = "Schlenk bomb"


class Experiment:
    id: Optional[int]
    code: Optional[str]
    creator: str
    degassing: Optional[Degassing]
    duration: str
    duration_unit: Optional[Unit]
    evaporate: Optional[bool]
    nr_in_lab_journal: int
    observation_text: str
    reaction_components: List[ReactionComponent]
    reaction_started_when: Optional[datetime]
    realization_text: str
    rinse: Optional[List[str]]
    temperature: str
    temperature_unit: Optional[TemperatureUnit]
    vessel: Optional[Vessel]
    wait_after_rinse: Optional[int]
    wait_after_rinse_unit: Optional[Unit]
    wash_solid: Optional[str]

    def __init__(self, id: Optional[int], code: Optional[str], creator: str, degassing: Optional[Degassing], duration: str, duration_unit: Optional[Unit], evaporate: Optional[bool], nr_in_lab_journal: int, observation_text: str, reaction_components: List[ReactionComponent], reaction_started_when: Optional[datetime], realization_text: str, rinse: Optional[List[str]], temperature: str, temperature_unit: Optional[TemperatureUnit], vessel: Optional[Vessel], wait_after_rinse: Optional[int], wait_after_rinse_unit: Optional[Unit], wash_solid: Optional[str]) -> None:
        self.id = id
        self.code = code
        self.creator = creator
        self.degassing = degassing
        self.duration = duration
        self.duration_unit = duration_unit
        self.evaporate = evaporate
        self.nr_in_lab_journal = nr_in_lab_journal
        self.observation_text = observation_text
        self.reaction_components = reaction_components
        self.reaction_started_when = reaction_started_when
        self.realization_text = realization_text
        self.rinse = rinse
        self.temperature = temperature
        self.temperature_unit = temperature_unit
        self.vessel = vessel
        self.wait_after_rinse = wait_after_rinse
        self.wait_after_rinse_unit = wait_after_rinse_unit
        self.wash_solid = wash_solid

    @staticmethod
    def from_dict(obj: Any) -> 'Experiment':
        assert isinstance(obj, dict)
        id = from_union([from_int, from_none], obj.get("@id"))
        code = from_union([from_str, from_none], obj.get("code"))
        creator = from_str(obj.get("creator"))
        degassing = from_union([Degassing, from_none], obj.get("degassing"))
        duration = from_str(obj.get("duration"))
        duration_unit = from_union([Unit, from_none], obj.get("durationUnit"))
        evaporate = from_union([from_bool, from_none], obj.get("evaporate"))
        nr_in_lab_journal = from_int(obj.get("nrInLabJournal"))
        observation_text = from_str(obj.get("observationText"))
        reaction_components = from_list(ReactionComponent.from_dict, obj.get("reactionComponents"))
        reaction_started_when = from_union([from_datetime, from_none], obj.get("reactionStartedWhen"))
        realization_text = from_str(obj.get("realizationText"))
        rinse = from_union([lambda x: from_list(from_str, x), from_none], obj.get("rinse"))
        temperature = from_str(obj.get("temperature"))
        temperature_unit = from_union([TemperatureUnit, from_none], obj.get("temperatureUnit"))
        vessel = from_union([Vessel, from_none], obj.get("vessel"))
        wait_after_rinse = from_union([from_int, from_none], obj.get("wait_after_rinse"))
        wait_after_rinse_unit = from_union([Unit, from_none], obj.get("wait_after_rinse_unit"))
        wash_solid = from_union([from_str, from_none], obj.get("wash_solid"))
        return Experiment(id, code, creator, degassing, duration, duration_unit, evaporate, nr_in_lab_journal, observation_text, reaction_components, reaction_started_when, realization_text, rinse, temperature, temperature_unit, vessel, wait_after_rinse, wait_after_rinse_unit, wash_solid)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.id is not None:
            result["@id"] = from_union([from_int, from_none], self.id)
        if self.code is not None:
            result["code"] = from_union([from_str, from_none], self.code)
        result["creator"] = from_str(self.creator)
        if self.degassing is not None:
            result["degassing"] = from_union([lambda x: to_enum(Degassing, x), from_none], self.degassing)
        result["duration"] = from_str(self.duration)
        if self.duration_unit is not None:
            result["durationUnit"] = from_union([lambda x: to_enum(Unit, x), from_none], self.duration_unit)
        if self.evaporate is not None:
            result["evaporate"] = from_union([from_bool, from_none], self.evaporate)
        result["nrInLabJournal"] = from_int(self.nr_in_lab_journal)
        result["observationText"] = from_str(self.observation_text)
        result["reactionComponents"] = from_list(lambda x: to_class(ReactionComponent, x), self.reaction_components)
        if self.reaction_started_when is not None:
            result["reactionStartedWhen"] = from_union([lambda x: x.isoformat(), from_none], self.reaction_started_when)
        result["realizationText"] = from_str(self.realization_text)
        if self.rinse is not None:
            result["rinse"] = from_union([lambda x: from_list(from_str, x), from_none], self.rinse)
        result["temperature"] = from_str(self.temperature)
        if self.temperature_unit is not None:
            result["temperatureUnit"] = from_union([lambda x: to_enum(TemperatureUnit, x), from_none], self.temperature_unit)
        if self.vessel is not None:
            result["vessel"] = from_union([lambda x: to_enum(Vessel, x), from_none], self.vessel)
        if self.wait_after_rinse is not None:
            result["wait_after_rinse"] = from_union([from_int, from_none], self.wait_after_rinse)
        if self.wait_after_rinse_unit is not None:
            result["wait_after_rinse_unit"] = from_union([lambda x: to_enum(Unit, x), from_none], self.wait_after_rinse_unit)
        if self.wash_solid is not None:
            result["wash_solid"] = from_union([from_str, from_none], self.wash_solid)
        return result


class SciformationCleanedELNSchema:
    experiments: List[Experiment]

    def __init__(self, experiments: List[Experiment]) -> None:
        self.experiments = experiments

    @staticmethod
    def from_dict(obj: Any) -> 'SciformationCleanedELNSchema':
        assert isinstance(obj, dict)
        experiments = from_list(Experiment.from_dict, obj.get("experiments"))
        return SciformationCleanedELNSchema(experiments)

    def to_dict(self) -> dict:
        result: dict = {}
        result["experiments"] = from_list(lambda x: to_class(Experiment, x), self.experiments)
        return result


def sciformation_cleaned_eln_schema_from_dict(s: Any) -> SciformationCleanedELNSchema:
    return SciformationCleanedELNSchema.from_dict(s)


def sciformation_cleaned_eln_schema_to_dict(x: SciformationCleanedELNSchema) -> Any:
    return to_class(SciformationCleanedELNSchema, x)
