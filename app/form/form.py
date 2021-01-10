import fastapi
import json

from starlette.templating import Jinja2Templates
from starlette.requests import Request

from app.models import Prediction
from app.prediction import predict_api


templates = Jinja2Templates("templates")
router = fastapi.APIRouter()


@router.get("/form", include_in_schema=False)
async def form(request: Request):
    """ form page """
    data = {"request": request}
    return templates.TemplateResponse("form.html", data)


@router.post("/form", include_in_schema=False)
async def post_form(request: Request,):
    """ form handling """
    form_data = await request.form()
    # TODO we need some logic to handle missing lactate/albumin and sliders here
    form_dict = dict(form_data)

    # sliders mean bools not passed if false
    if "CT_performed" not in form_dict:
        form_dict["CT_performed"] = False
    if "Sinus" not in form_dict:
        form_dict["Sinus"] = False

    # if lactate or albumin aren't filled they are returned as empty strings by the form
    if type(form_dict["Lactate"]) == str:
        del form_dict["Lactate"]

    if type(form_dict["Albumin"]) == str:
        del form_dict["Albumin"]

    pred = Prediction(**form_dict)
    results = await predict_api.predict(pred)

    data = {
        "request": request,
        "results": json.loads(results.body),
        "values": dict(form_data),
    }
    return templates.TemplateResponse("form.html", data)
