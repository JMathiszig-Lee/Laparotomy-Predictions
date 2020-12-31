from typing import Dict, Tuple
import pandas as pd


def winsorize(
    df: pd.DataFrame,
    winsor_thresholds: Dict[str, Tuple[float, float]]
) -> pd.DataFrame:
    """Winsorize continuous input variables, according to present thresholds.

    Args:
        df: Input variables
        winsor_thresholds: Keys are a subset of the column names in df, values
            are (lower_threshold, upper_threshold)

    Returns:
        df: Same as input df, except with Winsorized continuous variables
    """
    for v, threshold in winsor_thresholds.items():
        df.loc[df[v] < threshold[0], v] = threshold[0]
        df.loc[df[v] > threshold[1], v] = threshold[1]
    return df
