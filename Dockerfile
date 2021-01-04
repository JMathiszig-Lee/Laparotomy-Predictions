FROM python:3.8.6-slim

COPY Pipfile Pipfile.lock ./
RUN pip install pipenv
RUN pipenv install --system --deploy
COPY ./app /app