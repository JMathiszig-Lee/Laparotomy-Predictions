from app.prediction.predict import predict_mortality
from app.models import Prediction
from app.prediction.preprocess import pre_process_input

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
    "Lactate": 1,
    "Albumin": 40,
}


def test_predict_mortality():
    input_model = Prediction(**input)
    processed = pre_process_input(input_model)
    samples = 100

    prediction = predict_mortality([processed.convert_to_list()], samples, 1)

    assert prediction.shape[0] == samples
