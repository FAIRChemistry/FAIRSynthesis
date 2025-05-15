from typing import Optional, Any, List, Union, TypeVar, Type, Callable, cast
from enum import Enum


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


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


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_float(x: Any) -> float:
    assert isinstance(x, (int, float))
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class Metadata:
    description: str
    product: Optional[str]
    product_inchi: Optional[str]

    def __init__(self, description: str, product: Optional[str], product_inchi: Optional[str]) -> None:
        self.description = description
        self.product = product
        self.product_inchi = product_inchi

    @staticmethod
    def from_dict(obj: Any) -> 'Metadata':
        assert isinstance(obj, dict)
        description = from_str(obj.get("_description"))
        product = from_union([from_str, from_none], obj.get("_product"))
        product_inchi = from_union([from_str, from_none], obj.get("_product_inchi"))
        return Metadata(description, product, product_inchi)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_description"] = from_str(self.description)
        if self.product is not None:
            result["_product"] = from_union([from_str, from_none], self.product)
        if self.product_inchi is not None:
            result["_product_inchi"] = from_union([from_str, from_none], self.product_inchi)
        return result


class XMLType(Enum):
    ADD = "Add"
    EVACUATE_AND_REFILL = "EvacuateAndRefill"
    EVAPORATE = "Evaporate"
    HEAT_CHILL = "HeatChill"
    WAIT = "Wait"
    WASH_SOLID = "WashSolid"


class StepEntryClass:
    xml_type: Optional[XMLType]
    amount: Optional[str]
    gas: Optional[str]
    reagent: Optional[str]
    solvent: Optional[str]
    stir: Optional[str]
    temp: Optional[str]
    time: Optional[str]
    vessel: Optional[str]

    def __init__(self, xml_type: Optional[XMLType], amount: Optional[str], gas: Optional[str], reagent: Optional[str], solvent: Optional[str], stir: Optional[str], temp: Optional[str], time: Optional[str], vessel: Optional[str]) -> None:
        self.xml_type = xml_type
        self.amount = amount
        self.gas = gas
        self.reagent = reagent
        self.solvent = solvent
        self.stir = stir
        self.temp = temp
        self.time = time
        self.vessel = vessel

    @staticmethod
    def from_dict(obj: Any) -> 'StepEntryClass':
        assert isinstance(obj, dict)
        xml_type = from_union([XMLType, from_none], obj.get("$xml_type"))
        amount = from_union([from_str, from_none], obj.get("_amount"))
        gas = from_union([from_str, from_none], obj.get("_gas"))
        reagent = from_union([from_str, from_none], obj.get("_reagent"))
        solvent = from_union([from_str, from_none], obj.get("_solvent"))
        stir = from_union([from_str, from_none], obj.get("_stir"))
        temp = from_union([from_str, from_none], obj.get("_temp"))
        time = from_union([from_str, from_none], obj.get("_time"))
        vessel = from_union([from_str, from_none], obj.get("_vessel"))
        return StepEntryClass(xml_type, amount, gas, reagent, solvent, stir, temp, time, vessel)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.xml_type is not None:
            result["$xml_type"] = from_union([lambda x: to_enum(XMLType, x), from_none], self.xml_type)
        if self.amount is not None:
            result["_amount"] = from_union([from_str, from_none], self.amount)
        if self.gas is not None:
            result["_gas"] = from_union([from_str, from_none], self.gas)
        if self.reagent is not None:
            result["_reagent"] = from_union([from_str, from_none], self.reagent)
        if self.solvent is not None:
            result["_solvent"] = from_union([from_str, from_none], self.solvent)
        if self.stir is not None:
            result["_stir"] = from_union([from_str, from_none], self.stir)
        if self.temp is not None:
            result["_temp"] = from_union([from_str, from_none], self.temp)
        if self.time is not None:
            result["_time"] = from_union([from_str, from_none], self.time)
        if self.vessel is not None:
            result["_vessel"] = from_union([from_str, from_none], self.vessel)
        return result


class FlatProcedureClass:
    step: Optional[List[Optional[Union[float, int, bool, str, List[Any], StepEntryClass]]]]

    def __init__(self, step: Optional[List[Optional[Union[float, int, bool, str, List[Any], StepEntryClass]]]]) -> None:
        self.step = step

    @staticmethod
    def from_dict(obj: Any) -> 'FlatProcedureClass':
        assert isinstance(obj, dict)
        step = from_union([lambda x: from_list(lambda x: from_union([from_none, from_float, from_int, from_bool, from_str, lambda x: from_list(lambda x: x, x), StepEntryClass.from_dict], x), x), from_none], obj.get("Step"))
        return FlatProcedureClass(step)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.step is not None:
            result["Step"] = from_union([lambda x: from_list(lambda x: from_union([from_none, to_float, from_int, from_bool, from_str, lambda x: from_list(lambda x: x, x), lambda x: to_class(StepEntryClass, x)], x), x), from_none], self.step)
        return result


class Procedure:
    step: Optional[List[Optional[Union[float, int, bool, str, List[Any], StepEntryClass]]]]
    prep: Optional[Union[float, int, bool, str, List[Any], FlatProcedureClass]]
    reaction: Optional[Union[float, int, bool, str, List[Any], FlatProcedureClass]]
    workup: Optional[Union[float, int, bool, str, List[Any], FlatProcedureClass]]

    def __init__(self, step: Optional[List[Optional[Union[float, int, bool, str, List[Any], StepEntryClass]]]], prep: Optional[Union[float, int, bool, str, List[Any], FlatProcedureClass]], reaction: Optional[Union[float, int, bool, str, List[Any], FlatProcedureClass]], workup: Optional[Union[float, int, bool, str, List[Any], FlatProcedureClass]]) -> None:
        self.step = step
        self.prep = prep
        self.reaction = reaction
        self.workup = workup

    @staticmethod
    def from_dict(obj: Any) -> 'Procedure':
        assert isinstance(obj, dict)
        step = from_union([lambda x: from_list(lambda x: from_union([from_none, from_float, from_int, from_bool, from_str, lambda x: from_list(lambda x: x, x), StepEntryClass.from_dict], x), x), from_none], obj.get("Step"))
        prep = from_union([from_none, from_float, from_int, from_bool, from_str, lambda x: from_list(lambda x: x, x), FlatProcedureClass.from_dict], obj.get("Prep"))
        reaction = from_union([from_none, from_float, from_int, from_bool, from_str, lambda x: from_list(lambda x: x, x), FlatProcedureClass.from_dict], obj.get("Reaction"))
        workup = from_union([from_none, from_float, from_int, from_bool, from_str, lambda x: from_list(lambda x: x, x), FlatProcedureClass.from_dict], obj.get("Workup"))
        return Procedure(step, prep, reaction, workup)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.step is not None:
            result["Step"] = from_union([lambda x: from_list(lambda x: from_union([from_none, to_float, from_int, from_bool, from_str, lambda x: from_list(lambda x: x, x), lambda x: to_class(StepEntryClass, x)], x), x), from_none], self.step)
        if self.prep is not None:
            result["Prep"] = from_union([from_none, to_float, from_int, from_bool, from_str, lambda x: from_list(lambda x: x, x), lambda x: to_class(FlatProcedureClass, x)], self.prep)
        if self.reaction is not None:
            result["Reaction"] = from_union([from_none, to_float, from_int, from_bool, from_str, lambda x: from_list(lambda x: x, x), lambda x: to_class(FlatProcedureClass, x)], self.reaction)
        if self.workup is not None:
            result["Workup"] = from_union([from_none, to_float, from_int, from_bool, from_str, lambda x: from_list(lambda x: x, x), lambda x: to_class(FlatProcedureClass, x)], self.workup)
        return result


class SampleHolder:
    diameter: Optional[str]
    type: Optional[str]

    def __init__(self, diameter: Optional[str], type: Optional[str]) -> None:
        self.diameter = diameter
        self.type = type

    @staticmethod
    def from_dict(obj: Any) -> 'SampleHolder':
        assert isinstance(obj, dict)
        diameter = from_union([from_str, from_none], obj.get("_diameter"))
        type = from_union([from_str, from_none], obj.get("_type"))
        return SampleHolder(diameter, type)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.diameter is not None:
            result["_diameter"] = from_union([from_str, from_none], self.diameter)
        if self.type is not None:
            result["_type"] = from_union([from_str, from_none], self.type)
        return result


class XRaySource(Enum):
    CO_KΑ1 = "Co Kα1"
    CU_KΑ1 = "Cu Kα1"


class Characterization:
    relative_file_path: Optional[str]
    x_ray_source: Optional[XRaySource]
    sample_holder: Optional[SampleHolder]
    weight: Optional[str]

    def __init__(self, relative_file_path: Optional[str], x_ray_source: Optional[XRaySource], sample_holder: Optional[SampleHolder], weight: Optional[str]) -> None:
        self.relative_file_path = relative_file_path
        self.x_ray_source = x_ray_source
        self.sample_holder = sample_holder
        self.weight = weight

    @staticmethod
    def from_dict(obj: Any) -> 'Characterization':
        assert isinstance(obj, dict)
        relative_file_path = from_union([from_str, from_none], obj.get("_relative_file_path"))
        x_ray_source = from_union([XRaySource, from_none], obj.get("_x-ray_source"))
        sample_holder = from_union([SampleHolder.from_dict, from_none], obj.get("sample_holder"))
        weight = from_union([from_str, from_none], obj.get("_weight"))
        return Characterization(relative_file_path, x_ray_source, sample_holder, weight)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.relative_file_path is not None:
            result["_relative_file_path"] = from_union([from_str, from_none], self.relative_file_path)
        if self.x_ray_source is not None:
            result["_x-ray_source"] = from_union([lambda x: to_enum(XRaySource, x), from_none], self.x_ray_source)
        if self.sample_holder is not None:
            result["sample_holder"] = from_union([lambda x: to_class(SampleHolder, x), from_none], self.sample_holder)
        if self.weight is not None:
            result["_weight"] = from_union([from_str, from_none], self.weight)
        return result


class Role(Enum):
    ACID = "acid"
    ACTIVATING_AGENT = "activating-agent"
    BASE = "base"
    CATALYST = "catalyst"
    LIGAND = "ligand"
    QUENCHING_AGENT = "quenching-agent"
    REAGENT = "reagent"
    SOLVENT = "solvent"
    SUBSTRATE = "substrate"


class Reagent:
    cas: Optional[str]
    id: Optional[str]
    inchi: Optional[str]
    name: Optional[str]
    purity: Optional[str]
    role: Optional[Role]

    def __init__(self, cas: Optional[str], id: Optional[str], inchi: Optional[str], name: Optional[str], purity: Optional[str], role: Optional[Role]) -> None:
        self.cas = cas
        self.id = id
        self.inchi = inchi
        self.name = name
        self.purity = purity
        self.role = role

    @staticmethod
    def from_dict(obj: Any) -> 'Reagent':
        assert isinstance(obj, dict)
        cas = from_union([from_str, from_none], obj.get("_cas"))
        id = from_union([from_str, from_none], obj.get("_id"))
        inchi = from_union([from_str, from_none], obj.get("_inchi"))
        name = from_union([from_str, from_none], obj.get("_name"))
        purity = from_union([from_str, from_none], obj.get("_purity"))
        role = from_union([Role, from_none], obj.get("_role"))
        return Reagent(cas, id, inchi, name, purity, role)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.cas is not None:
            result["_cas"] = from_union([from_str, from_none], self.cas)
        if self.id is not None:
            result["_id"] = from_union([from_str, from_none], self.id)
        if self.inchi is not None:
            result["_inchi"] = from_union([from_str, from_none], self.inchi)
        if self.name is not None:
            result["_name"] = from_union([from_str, from_none], self.name)
        if self.purity is not None:
            result["_purity"] = from_union([from_str, from_none], self.purity)
        if self.role is not None:
            result["_role"] = from_union([lambda x: to_enum(Role, x), from_none], self.role)
        return result


class Reagents:
    reagent: List[Reagent]

    def __init__(self, reagent: List[Reagent]) -> None:
        self.reagent = reagent

    @staticmethod
    def from_dict(obj: Any) -> 'Reagents':
        assert isinstance(obj, dict)
        reagent = from_list(Reagent.from_dict, obj.get("Reagent"))
        return Reagents(reagent)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Reagent"] = from_list(lambda x: to_class(Reagent, x), self.reagent)
        return result


class Synthesis:
    metadata: Metadata
    procedure: Procedure
    product_characterization: List[Characterization]
    reagents: Reagents

    def __init__(self, metadata: Metadata, procedure: Procedure, product_characterization: List[Characterization], reagents: Reagents) -> None:
        self.metadata = metadata
        self.procedure = procedure
        self.product_characterization = product_characterization
        self.reagents = reagents

    @staticmethod
    def from_dict(obj: Any) -> 'Synthesis':
        assert isinstance(obj, dict)
        metadata = Metadata.from_dict(obj.get("Metadata"))
        procedure = Procedure.from_dict(obj.get("Procedure"))
        product_characterization = from_list(Characterization.from_dict, obj.get("Product_characterization"))
        reagents = Reagents.from_dict(obj.get("Reagents"))
        return Synthesis(metadata, procedure, product_characterization, reagents)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Metadata"] = to_class(Metadata, self.metadata)
        result["Procedure"] = to_class(Procedure, self.procedure)
        result["Product_characterization"] = from_list(lambda x: to_class(Characterization, x), self.product_characterization)
        result["Reagents"] = to_class(Reagents, self.reagents)
        return result


class Xdl:
    synthesis: List[Synthesis]

    def __init__(self, synthesis: List[Synthesis]) -> None:
        self.synthesis = synthesis

    @staticmethod
    def from_dict(obj: Any) -> 'Xdl':
        assert isinstance(obj, dict)
        synthesis = from_list(Synthesis.from_dict, obj.get("Synthesis"))
        return Xdl(synthesis)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Synthesis"] = from_list(lambda x: to_class(Synthesis, x), self.synthesis)
        return result


class JXDLSchema:
    xdl: Xdl

    def __init__(self, xdl: Xdl) -> None:
        self.xdl = xdl

    @staticmethod
    def from_dict(obj: Any) -> 'JXDLSchema':
        assert isinstance(obj, dict)
        xdl = Xdl.from_dict(obj.get("XDL"))
        return JXDLSchema(xdl)

    def to_dict(self) -> dict:
        result: dict = {}
        result["XDL"] = to_class(Xdl, self.xdl)
        return result


def jxdl_schema_from_dict(s: Any) -> JXDLSchema:
    return JXDLSchema.from_dict(s)


def jxdl_schema_to_dict(x: JXDLSchema) -> Any:
    return to_class(JXDLSchema, x)
