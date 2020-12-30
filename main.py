import fastapi
import uvicorn

api = fastapi.FastAPI()

@api.get('/')
def test():
    return "hello world"

@api.get('/verify')
def verify(calculation_id:str):
    """
    API endpoint to verify previous calculations
    """
    message = "this isn't built yet"
    return message

@api.post('/predict')
def predict():
    """
    Stuff to do with prediction goes here
    """

    return("Not yet built!")

uvicorn.run(api, port=8000, host="127.0.0.1")
