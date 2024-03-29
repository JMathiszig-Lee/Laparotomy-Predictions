import fastapi
import uvicorn

from app.prediction import predict_api
from app.form import form

from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.requests import Request

templates = Jinja2Templates("templates")
api = fastapi.FastAPI(
    title="RUNE Calculator",
    version="1.0.0",
    contact={
        "name": "Jakob Mathiszig-Lee",
        "email": "jakob.mathiszig-lee06@imperial.ac.uk",
    },
)


def configure():
    configure_routing()


def configure_routing():
    api.mount("/static", StaticFiles(directory="static"), name="static")
    api.include_router(predict_api.router)
    api.include_router(form.router)


@api.get("/", include_in_schema=False)
async def index(request: Request):
    """index page"""
    data = {"request": request}
    return templates.TemplateResponse("index.html", data)


@api.get("/favicon.ico", include_in_schema=False)
def favicon():
    return fastapi.responses.RedirectResponse(url="/static/img/favicon.png")


# @api.get("/verify")
# def verify(calculation_id: str):
#     """API endpoint to verify previous calculations"""
#     message = "this isn't built yet"
#     return message


if __name__ == "__main__":
    configure()
    uvicorn.run(api, port=8000, host="127.0.0.1")
else:
    configure()
