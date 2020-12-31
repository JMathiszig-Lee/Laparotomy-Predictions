import numpy as np
import pandas as pd
from numpy.random import RandomState
from sklearn.preprocessing import QuantileTransformer
from pygam import GAM, LinearGAM, LogisticGAM
from pygam.distributions import NormalDist


def quick_sample(
    gam: GAM,
    sample_at_X: np.ndarray,
    quantity: str,
    n_draws: int,
    random_seed: int
) -> np.ndarray:
    """
    Sample from the multivariate normal distribution over the GAM's
    coefficients, and use the samples to predict a distribution over the target
    quantity.

    This is a simplified version of pygam's GAM.sample() as we prespecify the
    lam (regularisation penalty) on each feature instead of fitting it with
    grid search, therefore we don't consider model uncertainty resulting from
    other values of lam.

    quantity='y' is only currently supported where gam.distribution is
    Gaussian, as is the case with LinearGAM. This is because, unlike
    GAM.sample(), we don't draw samples from the model distribution using
    gam.distribution.sample() as this method is unseeded, preventing
    reproducibility. Instead, we reimplement a seeded version of sampling from
    the model distribution inside this function, but we have only implemented
    this for a Gaussian model distribution.

    Parameters
    -----------
    gam: fitted GAM object

    sample_at_X : array of shape (n_samples, m_features)
        Input data at which to draw new samples.
        Only applies for `quantity` equal to `'y'` or to `'mu`'.

    random_seed: For input to np.random.RandomState

    quantity : {'y', 'coef', 'mu'}, default: 'y'
        What quantity to return pseudorandom samples of.

    n_draws : positive int, optional (default=100)
        The number of samples to draw from distribution over the model
            coefficients

    Returns
    -------
    draws : 2D array of length n_draws
        Simulations of the given `quantity` using samples from the
        posterior distribution of the coefficients given the response data.
        Each row is a pseudorandom sample.

        If `quantity == 'coef'`, then the number of columns of `draws` is
        the number of coefficients (`len(self.coef_)`).

        Otherwise, the number of columns of `draws` is the number of
        rows of `X`.
    """
    if quantity not in {"mu", "coef", "y"}:
        raise ValueError(
            "`quantity` must be one of 'mu', 'coef', 'y';" f" got {quantity}"
        )

    rnd = RandomState(random_seed)
    coef_draws = rnd.multivariate_normal(
        gam.coef_, gam.statistics_["cov"], size=n_draws
    )

    if quantity == "coef":
        return coef_draws

    linear_predictor = gam._modelmat(sample_at_X).dot(coef_draws.T)
    mu_shape_n_draws_by_n_samples = gam.link.mu(linear_predictor,
                                                gam.distribution).T
    if quantity == "mu":
        return mu_shape_n_draws_by_n_samples
    else:
        if isinstance(gam.distribution, NormalDist):
            scale = gam.distribution.scale
            standard_deviation = scale ** 0.5 if scale else 1.0
            return rnd.normal(
                loc=mu_shape_n_draws_by_n_samples,
                scale=standard_deviation,
                size=None
            )
        else:
            raise NotImplementedError


def impute(
    features: pd.DataFrame,
    n_samples: int,
    model: LinearGAM,
    transformer: QuantileTransformer,
    random_seed: int
) -> np.ndarray:
    """Impute distribution of missing lactate or albumin values for a single
        patient.

    Args:
        features: Input data. Will have single row. Columns should follow the
            order specified in IMPUTATION_INPUT_VARIABLES. Categorical
            variables should be encoded as integers. Continuous variables
            should be Winsorized.
        n_samples: Number of lactate / albumin values to impute
        model: Pre-fitted lactate / albumin imputation GAM
        transformer: Pre-fitted tranformer to transform Gaussian GAM output
            back to lactate / albumin space
        random_seed: Random seed

    Returns:
        Predicted lactate / albumin values of shape (n_samples,)
    """
    y_pred = quick_sample(
        gam=model,
        sample_at_X=features.values,
        quantity='y',
        n_draws=n_samples,
        random_seed=random_seed
    ).flatten()
    return transformer.inverse_transform(y_pred.reshape(-1, 1)).flatten()


def predict_mortality(
    features: pd.DataFrame,
    n_samples_per_row: int,
    model: LogisticGAM,
    random_seed: int
) -> np.ndarray:
    """Predict distribution of mortality risks for single patient.

    Args:
        features: Input data. Will have single row if both lactate and albumin
            are non-missing. Otherwise, will have multiple rows where variables 
            apart from imputed lactate / albumin are the same. Columns should 
            follow the order specified in MORTALITY_INPUT_VARIABLES
            Categorical variables should be encoded as integers. Continuous 
            variables should be Winsorized.
        n_samples_per_row: Number of mortality risks to predict for each row of
            features
        model: Pre-fitted mortality GAM
        random_seed: Random seed

    Returns:
        Predicted mortality risks of shape
            (features.shape[0] * n_samples_per_row,)
    """
    return quick_sample(
        gam=model,
        sample_at_X=features.values,
        quantity="mu",
        n_draws=n_samples_per_row,
        random_seed=random_seed
    ).flatten()
