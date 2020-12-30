from pydantic import BaseModel
from typing import Optional
from collections import namedtuple

##these should become classes of the type IntENum i think
RESP_CATS = namedtuple(
    "No dyspnea",
    "Mild COPD or dyspnoea",
    "Moderate COPD or dyspnoea",
    "Fibrosis or consolidation or severe dyspnoea",
)

CARD_CATS = namedtuple(
    "No cardiac failure",
    "Cardiovascular medications",
    "Peripheral oedema or taking warfarin",
    "Raised JVP or cardiomegaly",
)

INDICATIONS = namedtuple()

MALIGNANCY = namedtuple()

SOILING = namedtuple()


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
    Resp: RESP_CATS
    Cardio: CARD_CATS
    Sinus: bool
    CT_performed: bool
    Indication: str
    Malignancy: str
    Soiling: str
