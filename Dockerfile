FROM python:3.8.6-slim


COPY Pipfile Pipfile.lock ./
COPY templates ./templates
COPY static ./static
RUN pip install pipenv
RUN pipenv install --system --deploy
COPY /app /app

EXPOSE ${PORT:-80}
CMD ["uvicorn", "app.main:api", "--host", "0.0.0.0", "--port", ${PORT:-80}]

