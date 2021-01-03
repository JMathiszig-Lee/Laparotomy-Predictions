import fastapi
import uvicorn
from models import Prediction

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


@api.post("/predict", response_model=Prediction)
async def predict(prediction: Prediction):
    """ Stuff to do with prediction goes here """

    # some function to get data ready for GAM's
    # make lactate and albumin imputation calls asynchronus for speed

    # logging goes here if allowed

    # retrieve from redis que and return

    return " Not yet built!"


uvicorn.run(api, port=8000, host="127.0.0.1")
