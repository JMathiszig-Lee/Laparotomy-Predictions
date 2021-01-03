import fastapi
import uvicorn
import uuid
import sys

from typing import List
from models import Prediction, ProcessedPrediction
from preprocess import pre_process_input
from predict import predict_mortality
from impute import impute_lactate, impute_albumin, complete_input

api = fastapi.FastAPI()


@api.get("/")
def index():
    """ index page """
    return "hello world"


@api.get("/verify")
def verify(calculation_id: str):
    """ API endpoint to verify previous calculations """
    message = "this isn't built yet"
    return message


@api.post("/predict")
def predict(prediction: Prediction):
    """ Stuff to do with prediction goes here """

    predict_ID = str(uuid.uuid4())
    seed = abs(hash(predict_ID)) & 0xffffffff

    processed = pre_process_input(prediction)

    if processed.Lactate_missing == 0 and processed.Albumin_missing == 0:
        # go straight to mortality prediction
        result = predict_mortality([processed.convert_to_list()], 100, seed)
    else:
        lactates = impute_lactate(processed.convert_to_list()[:17], 50, seed)
        albumins = impute_albumin(processed.convert_to_list()[:17], 50, seed)

        filled_in: List(ProcessedPrediction) = []

        if processed.Lactate_missing == 1:
            filled_in = (
                complete_input(imputed=lactates, input_list=[processed], Lactate=True)
            )
            if processed.Albumin_missing == 1:
                filled_in = complete_input(
                    imputed=albumins, input_list=filled_in, Lactate=False
                )

        if processed.Albumin_missing == 1:
            filled_in = (
                complete_input(imputed=albumins, input_list=[processed], Lactate=False)
            )
            if processed.Lactate_missing == 1:
                filled_in = complete_input(
                    imputed=lactates, input_list=filled_in, Lactate=True
                )

        filled_lists = []
        for i in filled_in:
            filled_lists.append(i.convert_to_list())

        result = predict_mortality(
            features=filled_lists, n_samples_per_row=100, random_seed=seed
        )


    prediction_result = {"ID": predict_ID, "Seed": seed, "Result": result.tolist()}
     # logging goes here if allowed

    return fastapi.responses.JSONResponse(
        content=prediction_result,
        status_code= 200
    )


uvicorn.run(api, port=8000, host="127.0.0.1")
