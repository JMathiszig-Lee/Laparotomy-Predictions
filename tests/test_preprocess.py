import pytest
import app.preprocess as preprocess
from app.models import Prediction, ValidationError

pred = {
    "Age": 40,
    "ASA": 3,
    "HR": 87,
    "SBP": 120,
    "WCC": 13,
    "Na": 135,
    "K": 8,
    "Urea": 2,
    "Creat": 4,
    "Lactate": 3.5,
    "GCS": 15,
    "Resp": 2,
    "Cardio": 1,
    "Sinus": False,
    "CT_performed": True,
    "Indication": 1,
    "Malignancy": 2,
    "Soiling": 2,
}


def test_winsorize():
    pre_model = Prediction(**pred)
    processed = preprocess.pre_process_input(pre_model)

    assert processed.K == 7
    assert processed.Creat == 20


def test_indications_added():
    pre_model = Prediction(**pred)
    validated = preprocess.pre_process_input(pre_model)

    assert validated.Lactate_missing == 0
    assert validated.Albumin_missing == 1


def test_processed_list_order():
    pre_model = Prediction(**pred)
    validated = preprocess.pre_process_input(pre_model)

    pred_list = validated.convert_to_list()

    assert validated.Age == pred_list[2]
    assert validated.GCS == pred_list[10]
    assert validated.Lactate_missing == pred_list[20]


def test_validate_cats():
    pred_model = Prediction(**pred)

    # Respiratory error
    pred_model.Resp = 7
    with pytest.raises(ValidationError):
        preprocess.validate_categories(pred_model)

    pred_model.Resp = 2
    pred_model.Soiling = 3
    # tests soiling
    with pytest.raises(ValidationError):
        preprocess.validate_categories(pred_model)

    pred_model.Soiling = 1

    # cardiac
    pred_model.Cardio = 9
    with pytest.raises(ValidationError):
        preprocess.validate_categories(pred_model)

    pred_model.Cardio = 8
    pred_model.Malignancy = "bad"
    with pytest.raises(ValidationError):
        preprocess.validate_categories(pred_model)

    pred_model.Malignancy = 1
    pred_model.ASA = 10
    with pytest.raises(ValidationError):
        preprocess.validate_categories(pred_model)
