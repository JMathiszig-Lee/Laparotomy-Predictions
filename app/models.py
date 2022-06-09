from typing import List, Optional, Union

from pydantic import BaseModel, Field


class Prediction(BaseModel):
    """model to define inputs for prediction"""

    Age: int = Field(ge=0, description="Units: years")
    ASA: int = Field(
        ge=0,
        le=4,
        title="ASA grade",
        description="Encoded as ASA grade, minus 1",
    )
    HR: int = Field(title="Heart Rate", description="Units: Beats per minute")
    SBP: int = Field(
        title="Systolic Blood Pressure", description="Units: mmHg"
    )
    WCC: float = Field(title="White Cell Count", description="Units: x 10^9/L")
    Na: int = Field(title="Sodium", description="Units: mmol/L")
    K: float = Field(title="Potassium", description="Units: mmol/L")
    Urea: float = Field(title="Urea", description="Units: mmol/L")
    Creat: int = Field(title="Creatinine", description="Units: μmol/L")
    Lactate: Optional[float] = Field(
        title="Lactate", description="Units: mmol/L"
    )
    Albumin: Optional[int] = Field(title="Albumin", description="Units: g/L")
    GCS: int = Field(title="Glasgow Coma Score", ge=3, le=15)
    Resp: int = Field(
        title="Respiratory status",
        ge=0,
        le=3,
        description=(
            "Encoded as: 0=No dyspnoea, 1=Mild COPD or dyspnoea, 2=Moderate "
            "COPD or dyspnoea, 3=Fibrosis or consolidation or severe dyspnoea"
        ),
    )
    Cardio: int = Field(
        title="Cardiovascular status",
        ge=0,
        le=3,
        description=(
            "Encoded as: 0: No cardiac failure, 1: Cardiovascular medications, "
            "2: Peripheral oedema or taking warfarin, 3: Raised jugular venous "
            "pressure or cardiomegaly"
        ),
    )
    Arrhythmia: bool = Field(
        title="Arrhythmia",
        description=(
            "Does the patient have an arrhythmia? (Excludes sinus tachycardia. "
            "Includes rate-controlled atrial fibrillation.)"
        ),
    )
    CT_performed: bool = Field(
        description=(
            "Did the patient have a CT abdomen and pelvis pre-operatively?"
        )
    )
    Indication: int = Field(
        title="Indication for surgery",
        ge=0,
        le=12,
        description=(
            "Encoded as: 0=Small bowel obstruction, 2=Perforation, 3=Large "
            "bowel obstructtion, 4=Peritonitis, 5=Ischaemia, 6=Haemorrhage, "
            "7=Colitis, 8=Other, 9=Abdominal abscess, 10=Anastamotic leak, "
            "11=Incarcerated hernia, 12=Volvulus"
        ),
    )
    Malignancy: int = Field(
        title="Does the patient have cancer? If so, to what extent?",
        ge=0,
        le=3,
        description=(
            "Encoded as: 0=None, 1=Primary only, 2=Nodal metastasis, 3=Distant "
            "metastasis"
        ),
    )
    Soiling: int = Field(
        title="Is their peritoneal soiling? If so, to what extent?",
        ge=0,
        le=3,
        description=(
            "Encoded as: 0=None, 1=Serous fluid, 2=Local pus, 3=Free bowel "
            "content, pus or blood"
        ),
    )

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
