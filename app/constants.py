RANDOM_SEED = 1

WINSOR_THRESHOLDS = {
    'S01AgeOnArrival': [18.0, 96.0],
    'S03SerumCreatinine': [20.0, 758.7750000000087],
    'S03Sodium': [115.0, 157.0],
    'S03Potassium': [2.3, 7.0],
    'S03Urea': [1.0, 49.44520000000193],
    'S03WhiteCellCount': [0.7, 143.0],
    'S03Pulse': [45.0, 173.25900000002002],
    'S03SystolicBloodPressure': [60.0, 214.0],
    'S03PreOpLowestAlbumin': [3.9712000000000005, 73.0],
    'S03PreOpArterialBloodLactate': [0.3, 19.0]
}

LABEL_ENCODING = {
    'S03ASAScore': (1.0, 2.0, 3.0, 4.0, 5.0),
    'S03CardiacSigns': (1.0, 2.0, 4.0, 8.0),
    'S03RespiratorySigns': (1.0, 2.0, 4.0, 8.0),
    'S03DiagnosedMalignancy': (1.0, 2.0, 4.0, 8.0),
    'S03Pred_Peritsoil': (1.0, 2.0, 4.0, 8.0),
    'Indication': (
        'S05Ind_SmallBowelObstruction',
        'S05Ind_IntestinalObstruction',
        'S05Ind_Perforation',
        'S05Ind_LargeBowelObstruction',
        'S05Ind_Peritonitis',
        'S05Ind_Ischaemia',
        'S05Ind_Haemorrhage',
        'S05Ind_Colitis',
        'S05Ind_Other',
        'S05Ind_AbdominalAbscess',
        'S05Ind_AnastomoticLeak',
        'S05Ind_IncarceratedHernia',
        'S05Ind_Volvulus',
        'S05Ind_Missing'
    )
}

IMPUTATION_INPUT_VARIABLES = (
    'S02PreOpCTPerformed',
    'S03ECG',
    'S01AgeOnArrival',
    'S03SerumCreatinine',
    'S03Sodium',
    'S03Potassium',
    'S03Urea',
    'S03WhiteCellCount',
    'S03Pulse',
    'S03SystolicBloodPressure',
    'S03GlasgowComaScore',
    'S03ASAScore',
    'S03CardiacSigns',
    'S03RespiratorySigns',
    'S03DiagnosedMalignancy',
    'S03Pred_Peritsoil',
    'Indication'
)

MORTALITY_INPUT_VARIABLES = IMPUTATION_INPUT_VARIABLES + (
    'S03PreOpLowestAlbumin',
    'S03PreOpLowestAlbumin_missing',
    'S03PreOpArterialBloodLactate',
    'S03PreOpArterialBloodLactate_missing'
)
