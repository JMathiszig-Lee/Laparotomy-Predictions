from pydantic import BaseModel
from typing import Optional


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
    Indication: int
    Malignancy: int
    Soiling: int


class ProcessedPrediction(Prediction):
    Lactate_missing: int = 1
    Albumin_missing: int = 1

    def convert_to_list(self):
        """ converts object to list in correct order """
        input_list = [
            self.CT_performed,
            self.Sinus,
            self.Age,
            self.Creat,
            self.Na,
            self.K,
            self.Urea,
            self.WCC,
            self.HR,
            self.SBP,
            self.GCS,
            self.ASA,
            self.Cardio,
            self.Resp,
            self.Malignancy,
            self.Soiling,
            self.Indication,
            self.Albumin,
            self.Albumin_missing,
            self.Lactate,
            self.Lactate_missing,
        ]
        return input_list


class ValidationError(Exception):
    """validation error class to return meaningful errors to users"""

    def __init__(self, error_msg: str, status_code: int):
        super().__init__(error_msg)

        self.status_code = status_code
        self.error_msg = error_msg
