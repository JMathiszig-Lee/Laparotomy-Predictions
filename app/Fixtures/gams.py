import pickle

study_export = pickle.load(open("app/Fixtures/production_assets.pkl", "rb"))

MORTALITY_GAM = study_export["mortality"]["model"]
LACTATE_GAM = study_export["lactate"]["model"]
ALBUMIN_GAM = study_export["albumin"]["model"]

LACTATE_TRANSFORMER = study_export["lactate"]["transformer"]
ALBUMIN_TRANSFORMER = study_export["albumin"]["transformer"]

CATEGORY_ENCODING = study_export["mortality"]["input_data"]["unique_categories"]
