FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY Pipfile Pipfile.lock ./
COPY production_assets.pkl /app/app
COPY templates ./templates
COPY static ./static
RUN pip install pipenv
RUN pipenv install --system --deploy
COPY /app /app

