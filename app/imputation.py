from typing import Dict, List, Tuple, Union, Callable

import numpy as np
import pandas as pd
from progressbar import progressbar as pb
from pygam import LinearGAM
from sklearn.preprocessing import QuantileTransformer
from utils.gam import combine_mi_gams, quick_sample
from utils.impute import Imputer


class LactateAlbuminImputer(Imputer):
    """Impute missing values of lactate or albumin. There is no simple way
        to random seed GAM model fitting so imputation models will be different
        on each training iteration."""

    def __init__(
        self,
        df: pd.DataFrame,
        categorical_imputer: CategoricalImputer,
        lacalb_variable_name: str,
        imputation_model_factory: Callable[
            [pd.Index, Dict[str, Tuple], str, bool], LinearGAM],
        winsor_quantiles: Tuple[float, float],
        multi_cat_vars: Dict[str, Tuple],
        indication_var_name: str,
        mortality_as_feature: bool,
        random_seed):
        """
        Args:
            df: Must just contain the variable to impute, plus the mortality
                variable (latter needed for compatibility with Splitter).
            categorical_imputer: With pre-fit imputers for all categorical
                variables
            lacalb_variable_name: Name of lactate or albumin variable
            imputation_model_factory: Function which returns specified (but not
                yet fitted) models of the transformed imputation target
            winsor_quantiles: Lower and upper quantiles to winsorize
                continuous variables at by default
            multi_cat_vars: Keys are non-binary discrete variables, values are
                the categories (excluding null values) prior to integer encoding
            indication_var_name: Name of the indication column
            mortality_as_feature: If True, uses mortality labels as a feature
                in this lactate / albumin imputation model (providing that
                mortality is a feature in the GAM specification in
                imputation_model_factory)
            random_seed: Used for QuantileTransformer
        """
        super().__init__(
            df,
            categorical_imputer.tts,
            categorical_imputer.target_variable_name
        )
        self.cat_imputer = categorical_imputer
        self.cont_vars = NOVEL_MODEL_VARS["cont"]  # TODO: Remove if unused?
        self.lacalb_variable_name = lacalb_variable_name
        self.model_factory = imputation_model_factory
        self.winsor_quantiles = winsor_quantiles
        self.multi_cat_vars = multi_cat_vars
        self.ind_var_name = indication_var_name
        self.mortality_as_feature = mortality_as_feature
        self.random_seed = random_seed
        self.imputed = None  # Override base class. This var shouldn't be used
        self._check_df(df)
        self.winsor_thresholds: Dict[
            int,  # train-test split index
            Tuple[float, float]
        ] = {}
        self.transformers: Dict[
            int,  # train-test split index
            QuantileTransformer
        ] = {}
        self.imputers: Dict[
            int,  # train-test split index
            LinearGAM
        ] = {}

    def _check_df(self, df: pd.DataFrame):
        """Check that passed DataFrame has correct columns, and no others."""
        assert set(df.columns) == {
            self.target_variable_name,
            self.lacalb_variable_name
        }

    def fit(self):
        """Fit albumin or lactate imputation models for every train-test
            split."""
        for i in pb(range(self.tts.n_splits), prefix="Split iteration"):
            self._single_train_test_split(i)

    def _single_train_test_split(self, split_i: int):
        """Fit albumin or lactate imputation models for a single train-test
            split. lacalb_train and lacalb_test are DataFrames with a single
            column of lactate / albumin values."""
        lacalb_train, _, lacalb_test, _ = self._split(split_i)
        self._find_missing_indices(
            split_i=split_i,
            train=lacalb_train,
            test=lacalb_test,
            variable_names=[self.lacalb_variable_name]
        )
        obs_lacalb_train = self._get_observed_values(
            fold="train",
            split_i=split_i,
            X=lacalb_train
        )
        obs_lacalb_train = self._winsorize(split_i, obs_lacalb_train)
        obs_lacalb_train = self._fit_transform(split_i, obs_lacalb_train)
        self._fit_combine_gams(split_i, obs_lacalb_train)

    def _get_observed_values(
        self, fold: str, split_i: int, X: pd.DataFrame
    ) -> pd.DataFrame:
        """Note that the index of the returned DataFrame isn't reset."""
        return X.loc[X.index.difference(
            self.missing_i[fold][split_i][self.lacalb_variable_name]
        )]

    def _winsorize(
        self,
        split_i: int,
        lacalb: pd.DataFrame
    ) -> pd.DataFrame:
        """Winsorizes the only column in X. Also fits winsor_thresholds for this
            train-test split if not already fit (this fitting should happen on
            the train fold)."""
        try:
            lacalb, _ = winsorize_novel(
                df=lacalb,
                thresholds={
                    self.lacalb_variable_name: self.winsor_thresholds[split_i]
                }
            )
        except KeyError:
            lacalb, winsor_thresholds = winsorize_novel(
                df=lacalb,
                cont_vars=[self.lacalb_variable_name],
                quantiles=self.winsor_quantiles
            )
            self.winsor_thresholds[split_i] = winsor_thresholds[
                self.lacalb_variable_name
            ]
        return lacalb

    def _fit_transform(
        self,
        split_i: int,
        obs_lacalb_train: pd.DataFrame
    ) -> pd.DataFrame:
        """Note that, as lactate / albumin are effectively discretised in the
            NELA dataset (lactate is reported to 1 DP and albumin is reported
            to 0 DP), the resolution of QuantileTransformer's quantiles is
            limited despite us setting n_quantiles to a large number."""
        self.transformers[split_i] = QuantileTransformer(
            n_quantiles=10000,
            output_distribution='normal',
            random_state=self.random_seed
        )
        obs_lacalb_train[self.lacalb_variable_name] = self.transformers[
            split_i
        ].fit_transform(obs_lacalb_train.values)
        return obs_lacalb_train

    def _fit_combine_gams(
        self,
        split_i: int,
        obs_lacalb_train: pd.DataFrame
    ):
        gams = []
        for mice_imp_i in range(self.cat_imputer.swm.n_mice_imputations):
            features_train = self.cat_imputer.get_imputed_df(
                "train", split_i, mice_imp_i)
            if not self.mortality_as_feature:
                features_train = features_train.drop(
                    self.target_variable_name, axis=1)
            obs_features_train = self._get_observed_values(
                "train", split_i, features_train)
            gam = self.model_factory(
                obs_features_train.columns,
                self.multi_cat_vars,
                self.ind_var_name,
                self.mortality_as_feature)
            gam.fit(obs_features_train.values, obs_lacalb_train.values)
            gams.append(gam)
        self.imputers[split_i] = combine_mi_gams(gams)

    def impute(
        self,
        features: pd.DataFrame,
        split_i: int,
        lac_alb_imp_i: Union[int, None],
        probabilistic: bool
    ) -> np.ndarray:
        """Impute lactate / albumin values given the provided features. Don't
            need to winsorize here as transformer is fit to winsorized data. If
            probabilitic is True, the imputed value for each patient is a
            single sample from the patient-specific distribution over lactate
            or albumin. If probabilitic is False, the imputed value is the
            mean of that distribution (note that lac_alb_imp_i is ignored and
            must be None in this case)."""
        if probabilistic:
            assert isinstance(lac_alb_imp_i, int)
            lacalb_imputed_trans = quick_sample(
                gam=self.imputers[split_i],
                sample_at_X=features.values,
                quantity='y',
                n_draws=1,
                random_seed=lac_alb_imp_i
            ).flatten()
        else:
            assert lac_alb_imp_i is None
            lacalb_imputed_trans = self.imputers[split_i].predict_mu(
                X=features.values)
        return self.transformers[split_i].inverse_transform(
            lacalb_imputed_trans.reshape(-1, 1))

    def get_complete_variable_and_missingness_indicator(
        self,
        fold_name: str,
        split_i: int,
        mice_imp_i: int,
        lac_alb_imp_i: int,
        missingness_indicator: bool = True
    ) -> pd.DataFrame:
        """Impute missing albumin / lactate values, then use the observed and
            imputed values to construct a DataFrame with a single complete
            column of albumin / lactate values. Optionally, add a second column
            which is 1 where values were originally missing, otherwise 0."""
        missing_features = self._get_features_where_lacalb_missing(
            fold_name, split_i, mice_imp_i)
        lacalb_imputed = self.impute(
            missing_features, split_i, lac_alb_imp_i, probabilistic=True)
        lacalb = self._get_complete_lacalb(
            lacalb_imputed, fold_name, split_i)
        lacalb = self._winsorize(split_i, lacalb)
        if missingness_indicator:
            lacalb = self._add_missingness_indicator(lacalb, fold_name, split_i)
        return lacalb

    def get_observed_and_predicted(
        self,
        fold_name: str,
        split_i: int,
        mice_imp_i: int,
        lac_alb_imp_i: Union[int, None],
        probabilistic: bool
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Convenience function which fetches the observed lactate / albumin
            values from a given fold in a given train-test split, and the
            corresponding lactate / albumin values predicted by the imputation
            model."""
        if fold_name == 'train':
            lacalb, _, _, _ = self._split(split_i)
        elif fold_name == 'test':
            _, _, lacalb, _ = self._split(split_i)
        obs_lacalb = self._get_observed_values(
            fold=fold_name,
            split_i=split_i,
            X=lacalb
        )
        obs_lacalb = self._winsorize(split_i, obs_lacalb)
        features = self._get_features_where_lacalb_observed(
            fold_name, split_i, mice_imp_i)
        pred_lacalb = self.impute(
            features,
            split_i,
            lac_alb_imp_i,
            probabilistic=probabilistic
        ).flatten()
        return obs_lacalb[self.lacalb_variable_name].values, pred_lacalb

    def get_all_observed_and_predicted(
        self,
        fold_name: str,
        lac_alb_imp_i: Union[int, None],
        probabilistic: bool
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """Convenience function which fetches the observed lactate / albumin
            values from a given fold in EVERY given train-test split, and the
            corresponding lactate / albumin values predicted by the imputation
            model."""
        y_obs, y_preds = [], []
        for split_i in pb(range(self.tts.n_splits), prefix="Split iteration"):
            for mice_imp_i in range(self.cat_imputer.swm.n_mice_imputations):
                y_ob, y_pred = self.get_observed_and_predicted(
                    fold_name=fold_name,
                    split_i=split_i,
                    mice_imp_i=mice_imp_i,
                    lac_alb_imp_i=lac_alb_imp_i,
                    probabilistic=probabilistic
                )
                y_obs.append(y_ob)
                y_preds.append(y_pred)
        return y_obs, y_preds

    def _get_features_where_lacalb_missing(
        self,
        fold_name: str,
        split_i: int,
        mice_imp_i: int
    ) -> pd.DataFrame:
        features = self.cat_imputer.get_imputed_df(
            fold_name, split_i, mice_imp_i)
        if not self.mortality_as_feature:
            features = features.drop(self.target_variable_name, axis=1)
        return features.loc[
            self.missing_i[fold_name][split_i][self.lacalb_variable_name]]

    def _get_features_where_lacalb_observed(
        self,
        fold_name: str,
        split_i: int,
        mice_imp_i: int
    ) -> pd.DataFrame:
        features = self.cat_imputer.get_imputed_df(
            fold_name, split_i, mice_imp_i)
        if not self.mortality_as_feature:
            features = features.drop(self.target_variable_name, axis=1)
        return features.loc[features.index.difference(
            self.missing_i[fold_name][split_i][self.lacalb_variable_name])]

    def _get_complete_lacalb(
        self,
        lacalb_imputed: np.ndarray,
        fold_name: str,
        split_i: int
    ) -> pd.DataFrame:
        if fold_name == 'train':
            lacalb, _, _, _ = self._split(split_i)
        elif fold_name == 'test':
            _, _, lacalb, _ = self._split(split_i)
        lacalb.loc[
            self.missing_i[fold_name][split_i][self.lacalb_variable_name]
        ] = lacalb_imputed
        return lacalb

    def _add_missingness_indicator(
        self,
        df: pd.DataFrame,
        fold_name: str,
        split_i: int
    ) -> pd.DataFrame:
        """Adds a missingness indicator column for imputed variable."""
        missing_i_name = f"{self.lacalb_variable_name}_missing"
        df[missing_i_name] = np.zeros(df.shape[0])
        df.loc[
            self.missing_i[fold_name][split_i][self.lacalb_variable_name],
            missing_i_name
        ] = 1.0
        return df

    def get_imputed_variables(self, fold_name, split_i, imp_i):
        """Override base class method which shouldn't be used, as we don't
            store the imputed lactate / albumin values, but rather store the
            imputation models and use them to impute as and when needed."""
        raise NotImplementedError
