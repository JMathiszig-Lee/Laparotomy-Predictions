from pydantic import BaseModel, Field
from typing import Optional, List


class Prediction(BaseModel):
    """model to define inputs for prediction"""

    Age: int 
    ASA: int = Field(ge=0, le=4, default=None, title="ASA grade", description="encoded -1")
    HR: int = Field(title="Heart Rate")
    SBP: int = Field(title="Systolic Blood Pressure", description="systolic blood pressure in mmHg")
    WCC: float = Field(title="White Cell Count", description="white cell count x10^9/L")
    Na: int = Field(title="Sodium", description="units: mmol/L")
    K: float = Field(title="Potassium", description="units: mmol/L")
    Urea: float = Field(title="Urea", description="units: mmol/L")
    Creat: int = Field(title="Creatanine", description="units: umol/L")
    Lactate: Optional[float] = Field(title="Lactate", description="units: mmol/L")
    Albumin: Optional[int] = Field(title="Albumin", description="units: g/L")
    GCS: int = Field(title="Glasgow Coma Score", ge=3, le=15)
    Resp: int
    Cardio: int
    Arrhythmia: bool = Field(title="Arrythmia", description="Does the patient have an arrhytmia?")
    CT_performed: bool = Field(description="Did the patient have a CT pre-operatively?")
    Indication: int
    Malignancy: int
    Soiling: int

    class Config:
        schema_extra = {
            "example": {
                "Age": 40,
                "ASA": 3,
                "HR": 87,
                "SBP": 120,
                "WCC": 13,
                "Na": 135,
                "K": 8,
                "Urea": 2,
                "Creat": 60,
                "Lactate": 3.5,
                "Albumin": 40,
                "GCS": 15,
                "Resp": 2,
                "Cardio": 1,
                "Arrhythmia": False,
                "CT_performed": True,
                "Indication": 1,
                "Malignancy": 2,
                "Soiling": 2,
            }
        }


class ProcessedPrediction(Prediction):
    Lactate_missing: int = 1
    Albumin_missing: int = 1

    def convert_to_list(self):
        """converts object to list in correct order"""
        input_list = [
            self.CT_performed,
            self.Arrhythmia,
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


class SummaryStats(BaseModel):
    Median: float
    LowerPercentile: float
    UpperPercentie: float


class PredictionResult(BaseModel):
    ID: str
    Seed: int
    Result: List[float]
    Summary: SummaryStats


class ValidationError(Exception):
    """validation error class to return meaningful errors to users"""

    def __init__(self, error_msg: str, status_code: int):
        super().__init__(error_msg)

        self.status_code = status_code
        self.error_msg = error_msg
