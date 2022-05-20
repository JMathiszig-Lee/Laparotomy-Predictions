import pytest

from typing import List
from app.prediction.impute import impute_lactate
from app.models import Prediction
from app.prediction.preprocess import pre_process_input


@pytest.mark.asyncio
async def test_lactate_impute():
    input = {
        "Age": 40,
        "ASA": 3,
        "HR": 87,
        "SBP": 120,
        "WCC": 13,
        "Na": 135,
        "K": 8,
        "Urea": 2,
        "Creat": 4,
        "GCS": 15,
        "Resp": 2,
        "Cardio": 1,
        "Arrhythmia": True,
        "CT_performed": True,
        "Indication": 1,
        "Malignancy": 2,
        "Soiling": 2,
        "Albumin": 40,
    }

    input_model = Prediction(**input)
    processed = pre_process_input(input_model)
    samples = 10
    imputed = await impute_lactate(processed.convert_to_list()[:17], samples, 5)
    print(imputed)

    assert imputed.shape[0] == samples
