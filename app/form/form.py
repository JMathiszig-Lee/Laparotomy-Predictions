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
    """form page"""
    data = {"request": request}
    return templates.TemplateResponse("form.html", data)


@router.post("/form", include_in_schema=False)
async def post_form(
    request: Request,
):
    """form handling"""
    form_data = await request.form()
    form_dict = dict(form_data)
    print(form_dict)

    # sliders mean bools not passed if false
    if "CT_performed" not in form_dict:
        form_dict["CT_performed"] = False
    if "Arrhythmia" not in form_dict:
        form_dict["Arrhythmia"] = False

    # if lactate or albumin aren't filled they are returned as empty strings by the form
    if not form_dict["Lactate"]:
        del form_dict["Lactate"]
    if not form_dict["Albumin"]:
        del form_dict["Albumin"]

    pred = Prediction(**form_dict)
    results = await predict_api.predict(pred)

    data = {
        "request": request,
        "results": json.loads(results.body),
        "values": dict(form_data),
    }
    return templates.TemplateResponse("form.html", data)
