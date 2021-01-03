from predict import impute
from Fixtures.gams import (
    LACTATE_GAM,
    ALBUMIN_GAM,
    LACTATE_TRANSFORMER,
    ALBUMIN_TRANSFORMER,
)
from typing import List
from models import ProcessedPrediction


async def impute_lactate(missing_vars: List, n_samples: int, seed: int) -> List[List]:
    """
    Imputes lactate as per parent function
    """
    imputed_values = impute(
        features=[missing_vars],
        n_samples=n_samples,
        model=LACTATE_GAM,
        transformer=LACTATE_TRANSFORMER,
        random_seed=seed,
    )

    return imputed_values


async def impute_albumin(missing_vars: List, n_samples: int, seed: int) -> List[List]:
    """
    Imputes albumin as per parent function
    """
    imputed_values = impute(
        features=[missing_vars],
        n_samples=n_samples,
        model=ALBUMIN_GAM,
        transformer=ALBUMIN_TRANSFORMER,
        random_seed=seed,
    )

    return imputed_values


def complete_input(
    imputed: List, impute_list: List[ProcessedPrediction], Lactate: bool = True
) -> List[ProcessedPrediction]:
    """
    Takes imputed variables and adds them to inputs

    Args:
        imputed: list of imputed variables
        impute_list: Prediction object or list of objects with missing variable to be filled in
        Lactate: if true variable to be filled in is lactate, else albumin will be populated

    Returns:
        List of prediction inputs with missing lactate or albumin filled in

    """

    completed = []
    for i in imputed:
        for j in impute_list:
            if Lactate is True:
                j.Lactate = i
            else:
                j.Albumin = i
            completed.append(j.copy())

    return completed
