import numpy as np
import pandas as pd
from pygam import LinearGAM
from sklearn.preprocessing import QuantileTransformer
from app.predict import quick_sample


class Imputer:
    """Impute missing values of lactate or albumin."""

    def __init__(
        self,
        model: LinearGAM,
        transformer: QuantileTransformer,
        random_seed: int
    ):
        self.model = model
        self.transformer = transformer
        self.random_seed = random_seed

    def predict(self, features: pd.DataFrame, n_samples: int) -> np.ndarray:
        """Probabilistically predict lactate or albumin values.

        Args:
            features: Input data. Columns should follow the order specified in
                IMPUTATION_INPUT_VARIABLES. Categorical variables should be
                encoded as integers. Continuous variables should be Winsorized.
            n_samples: Number of lactate / albumin vales to predict

        Returns:

        """
        y_pred = quick_sample(
            gam=self.model,
            sample_at_X=features.values,
            quantity='y',
            n_draws=n_samples,
            random_seed=self.random_seed
        ).flatten()
        return self.transformer.inverse_transform(y_pred.reshape(-1, 1))
