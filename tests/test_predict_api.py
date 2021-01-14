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
    "GCS": 15,
    "Resp": 2,
    "Cardio": 1,
    "Sinus": False,
    "CT_performed": True,
    "Indication": 1,
    "Malignancy": 2,
    "Soiling": 2,
    "Lactate": 1,
}


def test_predict_api_both_impute():
    response = client.post(
        "/predict", headers={"Content-Type": "application/json"}, json=pred
    )
    assert response.status_code == 200

    body = dict(response.json())
    assert len(body["Result"]) == 1000


def test_predict_api_alb_impute():
    pred["Albumin"] = 40

    response = client.post(
        "/predict", headers={"Content-Type": "application/json"}, json=pred
    )
    assert response.status_code == 200

    body = dict(response.json())
    assert len(body["Result"]) == 1000


def test_predict_api_basic():
    pred["Lactate"] = 1

    response = client.post(
        "/predict", headers={"Content-Type": "application/json"}, json=pred
    )
    assert response.status_code == 200

    body = dict(response.json())

    assert type(body["ID"]) == str
    assert type(body["Seed"]) == int
    assert type(body["Result"]) == list
    assert len(body["Result"]) == 1000


def test_predict_api_invalid_cat():
    pred["Soiling"] = 7
    response = client.post(
        "/predict", headers={"Content-Type": "application/json"}, json=pred
    )

    assert response.status_code == 422


def test_predict_api_invalid_type():
    pred["soiling"] = 1
    pred["SBP"] = 103.4
    response = client.post(
        "/predict", headers={"Content-Type": "application/json"}, json=pred
    )

    assert response.status_code == 422
