import fastapi
import uvicorn

from app.prediction import predict_api
from app.form import form

from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.middleware.cors import CORSMiddleware

templates = Jinja2Templates("templates")

api_description = """
This API will allow you to use the RUNE mortality calcultor via API


## API Encodings

### ASA
ASA is encoded -1. Therefore:
- 0 = ASA 1
- 1 = ASA 2
- 2 = ASA 3
- 3 = ASA 4
- 4 = ASA 5

### Indications
The Indication for surgery
- 0 : Small bowel obstruction
- 2 : Perforation
- 3 : Large bowel obstructtion 
- 4 : Peritonitis
- 5 : Ischaemia
- 6 : Haemorrhage
- 7 : Colitis
- 8 : Other
- 9 : Abdominal abscess
- 10 : Anastamotic leak
- 11 : Incarcerated hernia
- 12 : Volvulus

### Cardiovascular status
- 0 : None
- 1 : Diuretic, digoxin, Rx for angina or hypertension
- 2 : Peripheral oedema, warfarin, borderline cardiomegaly
- 3 : Raised JVP, cardiomegaly

### Respiratory status
- 0 : None
- 1 : Dyspnoea on exertion, mild COAD
- 2 : Limiting dyspnoea, moderate COAD
- 3 : Dyspnoea at rest, pulmonary fibrosis/consolidation

### Malignancy 
- 0 : None
- 1 : Primary only
- 2 : Nodal metastasis
- 3 : Distant metastasis

### Soiling 
- 0 : None
- 1 : Serous fluid
- 2 : Local pus
- 3 : Free bowel content, pus or blood 



"""
api = fastapi.FastAPI(
    title="RUNE Calculator",
    version="1.1.0",
    description=api_description,
    contact={
        "name": "Jakob Mathiszig-Lee",
        "email": "jakob.mathiszig-lee06@imperial.ac.uk",
    },
)

#allow cors for javascript api calls
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
