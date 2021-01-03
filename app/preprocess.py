from typing import Dict, Tuple
import pandas as pd
from models import Prediction, ValidationError
import constants


def pre_process_input(pred_input: Prediction):
    """
    Takes API input and pre-processes ready for model prediction

    Validates categorical data are correct
    Windorizes continous data
    Adds missingness indicators for Lactate and Albumin

    Inputs:
        Prediction model
    Returns:
        Updates preditiction mode? extension? list? df?
    """
    # validate categories are correctly encoded
    validate_categories(pred_input)

    # add missing indicators
    if pred_input.Lactate:
        pred_input.Lactate_missing = 0
    else:
        pred_input.Lactate_missing = 1

    if pred_input.Albumin:
        pred_input.Albumin_missing = 0
    else:
        pred_input.Albumin_missing = 1

    # windsorize continous variables

    return pred_input


def validate_categories(input: Prediction):
    """
    Validates Categorical Data conforms to correct encoding

    Input:
        Prediction model

    Returns:
        Validation error if present
    """

    if input.ASA not in constants.LABEL_ENCODING["S03ASAScore"]:
        error = f"Invalid ASA : {input.ASA}. Must be one of {constants.LABEL_ENCODING['S03ASAScore']}"
        raise ValidationError(error_msg=error, status_code=400)
    if input.Cardio not in constants.LABEL_ENCODING["S03CardiacSigns"]:
        error = f"Invalid ASA : {input.Cardio}. Must be one of {constants.LABEL_ENCODING['S03CardiacSigns']}"
        raise ValidationError(error_msg=error, status_code=400)
    if input.Resp not in constants.LABEL_ENCODING["S03RespiratorySigns"]:
        error = f"Invalid ASA : {input.Resp}. Must be one of {constants.LABEL_ENCODING['S03RespiratorySigns']}"
        raise ValidationError(error_msg=error, status_code=400)
    if input.Malignancy not in constants.LABEL_ENCODING["S03DiagnosedMalignancy"]:
        error = f"Invalid ASA : {input.Malignancy}. Must be one of {constants.LABEL_ENCODING['S03DiagnosedMalignancy']}"
        raise ValidationError(error_msg=error, status_code=400)
    if input.Soiling not in constants.LABEL_ENCODING["S03Pred_Peritsoil"]:
        error = f"Invalid ASA : {input.Soiling }. Must be one of {constants.LABEL_ENCODING['S03Pred_Peritsoil']}"
        raise ValidationError(error_msg=error, status_code=400)


def winsorize(
    df: pd.DataFrame, winsor_thresholds: Dict[str, Tuple[float, float]]
) -> pd.DataFrame:
    """Winsorize continuous input variables, according to present thresholds.

    Args:
        df: Input variables
        winsor_thresholds: Keys are a subset of the column names in df, values
            are (lower_threshold, upper_threshold)

    Returns:
        df: Same as input df, except with Winsorized continuous variables
    """
    for v, threshold in winsor_thresholds.items():
        df.loc[df[v] < threshold[0], v] = threshold[0]
        df.loc[df[v] > threshold[1], v] = threshold[1]
    return df
