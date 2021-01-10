import pickle

study_export = pickle.load(open("app/Fixtures/production_assets.pkl", "rb"))

MORTALTIY_GAM = study_export["mortality"]["model"]
LACTATE_GAM = study_export["lactate"]["model"]
ALBUMIN_GAM = study_export["albumin"]["model"]

LACTATE_TRANSFORMER = study_export["lactate"]["transformer"]
ALBUMIN_TRANSFORMER = study_export["albumin"]["transformer"]

CATEGORY_ENCODING = study_export["mortality"]['input_data']['unique_categories']

if __name__ == "__main__":
    print(study_export["mortality"])

    for i in study_export["mortality"]['input_data']['unique_categories']:
        print(i)
