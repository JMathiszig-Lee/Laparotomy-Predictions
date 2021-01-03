import pandas as pd
import app.preprocess as preprocess


def test_winsorize():
    df = pd.DataFrame({"for_winsor": [6.0, 1.0, 20.0], "ignore": [0.0, 1.0, 0.0]})
    expected = preprocess.winsorize(
        df=df, winsor_thresholds={"for_winsor": (4.0, 10.0)}
    )
    assert pd.DataFrame(
        {"for_winsor": [6.0, 4.0, 10.0], "ignore": [0.0, 1.0, 0.0]}
    ).equals(expected)
