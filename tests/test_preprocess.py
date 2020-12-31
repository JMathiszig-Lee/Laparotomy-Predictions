import pandas as pd
import app.preprocess as preprocess


def test_winsorize():
    df = pd.DataFrame({
        'for_winsor': [6., 1., 20.],
        'ignore': [0., 1., 0.]
    })
    expected = preprocess.winsorize(
        df=df,
        winsor_thresholds={'for_winsor': (4., 10.)}
    )
    assert pd.DataFrame({
        'for_winsor': [6., 4., 10.],
        'ignore': [0., 1., 0.]
    }).equals(expected)
