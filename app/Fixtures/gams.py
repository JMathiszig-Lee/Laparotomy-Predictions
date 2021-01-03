import pickle

study_export = pickle.load(open("./production_assets.pkl", "rb"))

MORTALTIY_GAM = study_export["mortality"]["model"]
LACTATE_GAM = study_export["lactate"]["model"]
ALBUMIN_GAM = study_export["albumin"]["model"]

LACTATE_TRANSFORMER = study_export["lactate"]["transformer"]
ALBUMIN_TRANSFORMER = study_export["albumin"]["transformer"]
