from pydantic import BaseModel
from typing import Optional
from collections import namedtuple
from enum import Enum, IntEnum


# these should become classes of the type IntENum i think
class RespCats(str, Enum):
    nodyspneoa = "NoDyspneoa"
    mild = "Mild COPD or dyspnoea"
    moderate = "Moderate COPD or dyspnoea"
    fibrosis = "Fibrosis or consolidation or severe dyspnoea"


class CardiacCats(str, Enum):
    none = "No cardiac failure"
    meds = "Cardiovascular medications"
    oedema = "Peripheral oedema or taking warfarin"
    cardiomegaly = "Raised JVP or cardiomegaly"


class Prediction(BaseModel):
    """model to define inputs for prediction"""

    Age: int
    ASA: int
    HR: int
    SBP: int
    WCC: float
    Na: int
    K: float
    Urea: float
    Creat: int
    Lactate: Optional[float]
    Albumin: Optional[int]
    GCS: int
    Resp: int
    Cardio: int
    Sinus: bool
    CT_performed: bool
    Indication: str
    Malignancy: str
    Soiling: str


class ValidationError(Exception):
    """validation error class to return meaningul errors to users"""

    def __init__(self, error_msg: str, status_code: int):
        super().__init__(error_msg)

        self.status_code = status_code
        self.error_msg = error_msg
