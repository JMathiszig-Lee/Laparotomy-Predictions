import fastapi
import uvicorn

from app.prediction import predict_api
from app.form import form
from starlette.staticfiles import StaticFiles
from starlette.requests import Request

Form = fastapi.Form

api = fastapi.FastAPI()


def configure():
    configure_routing()


def configure_routing():
    api.mount("/static", StaticFiles(directory="static"), name="static")
    api.include_router(predict_api.router)
    api.include_router(form.router)


@api.get("/", include_in_schema=False)
async def index(request: Request):
    """ index page """
    return "watch this space"


@api.get("/verify")
def verify(calculation_id: str):
    """ API endpoint to verify previous calculations """
    message = "this isn't built yet"
    return message


if __name__ == "__main__":
    configure()
    uvicorn.run(api, port=8000, host="127.0.0.1")
else:
    configure()
