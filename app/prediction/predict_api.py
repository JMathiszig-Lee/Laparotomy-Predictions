import fastapi
import uuid
import numpy as np

from app.models import (
    Prediction,
    ProcessedPrediction,
    PredictionResult,
    ValidationError,
)
from app.prediction.preprocess import pre_process_input
from app.prediction.predict import predict_mortality
from app.prediction.impute import impute_lactate, impute_albumin, complete_input
from app.Fixtures.constants import RANDOM_SEED

from typing import List

router = fastapi.APIRouter()


@router.post("/predict", response_model=PredictionResult)
async def predict(prediction: Prediction):
    """
    Rune model API endpoint

    See above for encoding
    """
    predict_ID = str(uuid.uuid4())
    # seed = abs(hash(predict_ID)) & 0xFFFFFFFF

    try:
        processed = pre_process_input(prediction)
    except ValidationError as ve:
        raise fastapi.HTTPException(status_code=ve.status_code, detail=ve.error_msg)

    if processed.Lactate_missing == 0 and processed.Albumin_missing == 0:
        # go straight to mortality prediction
        result = predict_mortality([processed.convert_to_list()], 10000, RANDOM_SEED)
    else:
        lactates = await impute_lactate(
            processed.convert_to_list()[:17], 10, RANDOM_SEED
        )
        albumins = await impute_albumin(
            processed.convert_to_list()[:17], 10, RANDOM_SEED
        )

        filled_in: List[ProcessedPrediction] = []

        if processed.Lactate_missing == 1:
            filled_in = complete_input(
                imputed=lactates, impute_list=[processed], Lactate=True
            )

            if processed.Albumin_missing == 1:
                filled_in = complete_input(
                    imputed=albumins, impute_list=filled_in, Lactate=False
                )

        elif processed.Albumin_missing == 1:
            filled_in = complete_input(
                imputed=albumins, impute_list=[processed], Lactate=False
            )

            if processed.Lactate_missing == 1:
                filled_in = complete_input(
                    imputed=lactates, impute_list=filled_in, Lactate=True
                )

        filled_lists = []
        for i in filled_in:
            filled_lists.append(i.convert_to_list())

        result = predict_mortality(
            features=filled_lists, n_samples_per_row=100, random_seed=RANDOM_SEED
        )

    median = np.median(result)
    lower_percentile = np.percentile(result, 2.5)
    upper_percentile = np.percentile(result, 97.5)

    prediction_result = {
        "ID": predict_ID,
        "Seed": RANDOM_SEED,
        "Result": result.tolist(),
        "Summary": {
            "Median": f"{median:4f}",
            "LowerPercentile": f"{lower_percentile:4f}",
            "UpperPercentile": f"{upper_percentile:4f}",
        },
        "Inputs": prediction.__dict__,
    }

    # logging goes here if allowed

    return fastapi.responses.JSONResponse(content=prediction_result, status_code=200)
