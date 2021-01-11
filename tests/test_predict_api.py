import json

from fastapi.testclient import TestClient
from app.main import api

client = TestClient(api)


def test_index():
    response = client.get("/")
    assert response.status_code == 200


pred = {
    "Age": 40,
    "ASA": 3,
    "HR": 87,
    "SBP": 120,
    "WCC": 13,
    "Na": 135,
    "K": 8,
    "Urea": 2,
    "Creat": 4,
    "Lactate": 3.5,
    "GCS": 15,
    "Resp": 2,
    "Cardio": 1,
    "Sinus": False,
    "CT_performed": True,
    "Indication": 1,
    "Malignancy": 2,
    "Soiling": 2,
}


def test_predict_api_basic():
    response = client.post(
        "/predict", headers={"Content-Type": "application/json"}, json=pred
    )
    assert response.status_code == 200

    body = dict(response.json())

    assert type(body["ID"]) == str
    assert type(body["Seed"]) == int
    assert type(body["Result"]) == list
