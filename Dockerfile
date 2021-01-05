FROM python:3.8.6-slim

COPY Pipfile Pipfile.lock ./
COPY production_assets.pkl /app
COPY templates /app/templates/
COPY static /app/static/
RUN pip install pipenv
RUN pipenv install --system --deploy
COPY ./app /app/app



CMD ["python", "app/main.py"]