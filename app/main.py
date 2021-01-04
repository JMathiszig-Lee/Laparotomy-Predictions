import fastapi
import uvicorn
import json

from prediction import predict_api
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.requests import Request

from models import Prediction

Form = fastapi.Form
templates = Jinja2Templates("templates")

api = fastapi.FastAPI()


def configure():
    configure_routing()


def configure_routing():
    api.mount("/static", StaticFiles(directory="static"), name="static")
    api.include_router(predict_api.router)


@api.get("/", include_in_schema=False)
async def index(request: Request):
    """ index page """
    data = {"request": request}
    return "watch this space"


@api.get("/form", include_in_schema=False)
async def form(request: Request):
    """ form page """
    data = {"request": request}
    return templates.TemplateResponse("form.html", data)


@api.post("/form", include_in_schema=False)
async def post_form(
    request: Request,
):
    """ form handling """
    print("---")
    form_data = await request.form()
    # TODO we need some logic to handle missing lactate/albumin and sliders here
    pred = Prediction(**form_data)
    print(pred)

    results = await predict_api.predict(pred)
    data = {"request": request, "results": json.loads(results.body)}
    print(data)
    return templates.TemplateResponse("form.html", data)


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
