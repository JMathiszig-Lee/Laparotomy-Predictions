import pickle
from app.predict import quick_sample

stuff = pickle.load(open("production_assets.pkl", "rb"))

mortality_gam = stuff["mortality"]["model"]
print(stuff["mortality"])

inputs = {
    "S02PreOpCTPerformed": 0,
    "S03ECG": 1,
    "S01AgeOnArrival": 70,
    "S03SerumCreatinine ": 63,
    "S03Sodium": 134,
    "S03Potassium ": 5,
    "S03Urea": 10,
    "S03WhiteCellCount ": 10,
    "S03Pulse": 60,
    "S03SystolicBloodPressure": 120,
    "S03GlasgowComaScore ": 4,
    "S03ASAScore": 4,
    "S03CardiacSigns ": 1,
    "S03RespiratorySigns": 1,
    "S03DiagnosedMalignancy  ": 1,
    "S03Pred_Peritsoil": 1,
    "Indication": 1,
    "S03PreOpLowestAlbumin": 10,
    "S03PreOpLowestAlbumin_missing": 1,
    "S03PreOpArterialBloodLactate": 1,
    "S03PreOpArterialBloodLactate_missing ": 1,
}


input_list = [
    0,
    1,
    70,
    63,
    134,
    5,
    10,
    10,
    60,
    120,
    4,
    4,
    1,
    1,
    1,
    1,
    1,
    10,
    1,
    1,
    1,
], [0, 1, 70, 63, 134, 5, 10, 10, 60, 120, 4, 4, 1, 1, 1, 1, 1, 10, 1, 1, 1]

# result = mortality_gam.sample(input_list, 0.436, quantity='y')

result = quick_sample(
    gam=mortality_gam, sample_at_X=input_list, random_seed=5, quantity="mu", n_draws=100
)

print(result)
