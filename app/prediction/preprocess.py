from app.Fixtures.gams import CATEGORY_ENCODING
from app.Fixtures import constants
from app.models import Prediction, ValidationError, ProcessedPrediction
from typing import Dict, Tuple


def pre_process_input(pred_input: Prediction) -> ProcessedPrediction:
    """
    Takes API input and pre-processes ready for model prediction

    Validates categorical data are correct
    Windorizes continous data
    Adds missingness indicators for Lactate and Albumin

    Inputs:
        Prediction model
    Returns:
        ProcessedPrediction
    """
    # validate categories are correctly encoded
    validate_categories(pred_input)

    processed = dict(pred_input)

    # add missing indicators
    if pred_input.Lactate:
        processed["Lactate_missing"] = 0

    if pred_input.Albumin:
        processed["Albumin_missing"] = 0

    # windsorize continous variables
    winzored = winsorize(processed, constants.WINSOR_THRESHOLDS)

    return ProcessedPrediction(**winzored)


def validate_categories(input: Prediction):
    """
    Validates Categorical Data conforms to correct encoding

    Input:
        Prediction model

    Returns:
        Validation error if present
    """

    if input.ASA not in CATEGORY_ENCODING["S03ASAScore"]:
        error = f"Invalid ASA : {input.ASA}. Must be one of {CATEGORY_ENCODING['S03ASAScore']}"
        raise ValidationError(error_msg=error, status_code=400)

    if input.Cardio not in CATEGORY_ENCODING["S03CardiacSigns"]:
        error = f"Invalid Cardiac Status : {input.Cardio}. Must be one of {CATEGORY_ENCODING['S03CardiacSigns']}"
        raise ValidationError(error_msg=error, status_code=400)

    if input.Resp not in CATEGORY_ENCODING["S03RespiratorySigns"]:
        error = f"Invalid Respiratory Status : {input.Resp}. Must be one of {CATEGORY_ENCODING['S03RespiratorySigns']}"
        raise ValidationError(error_msg=error, status_code=400)

    if input.Malignancy not in CATEGORY_ENCODING["S03DiagnosedMalignancy"]:
        error = f"Invalid Malignancy : {input.Malignancy}. Must be one of {CATEGORY_ENCODING['S03DiagnosedMalignancy']}"
        raise ValidationError(error_msg=error, status_code=400)

    if input.Soiling not in CATEGORY_ENCODING["S03Pred_Peritsoil"]:
        error = f"Invalid Peritoneal Soiling : {input.Soiling }. Must be one of {CATEGORY_ENCODING['S03Pred_Peritsoil']}"
        raise ValidationError(error_msg=error, status_code=422)

    if input.GCS not in CATEGORY_ENCODING["S03GlasgowComaScore"]:
        error = f"Invalid GCS : {input.GCS }. Must be one of {CATEGORY_ENCODING['S03GlasgowComaScore']}"
        raise ValidationError(error_msg=error, status_code=400)

    if input.Indication not in CATEGORY_ENCODING["Indication"]:
        error = f"Invalid indication : {input.Indication }. Must be one of {CATEGORY_ENCODING['Indication']}"
        raise ValidationError(error_msg=error, status_code=400)


def winsorize(df: Dict, winsor_thresholds: Dict[str, Tuple[float, float]]) -> Dict:
    """Winsorize continuous input variables, according to present thresholds.

    Args:
        df: Input variables
        winsor_thresholds: Keys are a subset of the column names in df, values
            are (lower_threshold, upper_threshold)

    Returns:
        df: Same as input df, except with Winsorized continuous variables
    """
    for v, threshold in winsor_thresholds.items():
        if df[v]:
            if df[v] < threshold[0]:
                df[v] = threshold[0]
            elif df[v] > threshold[1]:
                df[v] = threshold[1]
    return df
