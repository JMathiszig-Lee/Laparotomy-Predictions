from typing import Dict, List, Tuple, Callable

import numpy as np
import pandas as pd
from progressbar import progressbar as pb
from pygam import LogisticGAM
from utils.gam import combine_mi_gams, quick_sample


class NovelModel:
    """Handles the process of repeated of train-test splitting, re-fitting the
        novel mortality model using the training fold. Also allows prediction
        of mortality risk distribution for each case in the test fold."""

    def __init__(
        self,
        categorical_imputer: CategoricalImputer,
        albumin_imputer: LactateAlbuminImputer,
        lactate_imputer: LactateAlbuminImputer,
        model_factory: Callable[
            [pd.Index, Dict[str, Tuple], str], LogisticGAM],
        n_lacalb_imputations_per_mice_imp: int,
        random_seed
    ):
        self.cat_imputer = categorical_imputer
        self.alb_imputer = albumin_imputer
        self.lac_imputer = lactate_imputer
        self.model_factory = model_factory
        self.n_lacalb_imp = n_lacalb_imputations_per_mice_imp
        self.random_seed = random_seed
        self.target_variable_name = categorical_imputer.swm.target_variable_name
        self.models: Dict[
            int,  # train-test split index
            LogisticGAM
        ] = {}

    def _calculate_lac_alb_imp_i(
        self,
        mice_imp_i: int,
        lac_alb_imp_i: int
    ) -> int:
        return self.random_seed + lac_alb_imp_i + self.n_lacalb_imp * mice_imp_i

    def get_features_and_labels(
        self,
        fold_name: str,
        split_i: int,
        mice_imp_i: int,
        lac_alb_imp_i: int
    ) -> Tuple[pd.DataFrame, np.ndarray]:
        """Uses results of previous imputation to construct complete DataFrames
            of features, and corresponding mortality labels, ready for input to
            mortality risk prediction model."""
        df = self.cat_imputer.get_imputed_df(
            fold_name, split_i, mice_imp_i
        )
        target = df[self.target_variable_name].values
        features = df.drop(self.target_variable_name, axis=1)
        for imputer in (self.alb_imputer, self.lac_imputer):
            lacalb_and_indicator = (
                imputer.get_complete_variable_and_missingness_indicator(
                    fold_name=fold_name,
                    split_i=split_i,
                    mice_imp_i=mice_imp_i,
                    lac_alb_imp_i=self._calculate_lac_alb_imp_i(
                        mice_imp_i,
                        lac_alb_imp_i
                    )
                )
            )
            features = pd.concat([features, lacalb_and_indicator], axis=1)
        return features, target

    def fit(self):
        """Fit mortality risk models for every train-test split."""
        for split_i in pb(
            range(self.cat_imputer.tts.n_splits),
            prefix="Split iteration"
        ):
            self._single_train_test_split(split_i)

    def _single_train_test_split(self, split_i: int):
        """Fit combined mortality risk model for a single train-test split."""
        gams = []
        for mice_imp_i in range(self.cat_imputer.swm.n_mice_imputations):
            for lac_alb_imp_i in range(self.n_lacalb_imp):
                features, target = self.get_features_and_labels(
                    fold_name='train',
                    split_i=split_i,
                    mice_imp_i=mice_imp_i,
                    lac_alb_imp_i=self._calculate_lac_alb_imp_i(
                        mice_imp_i,
                        lac_alb_imp_i
                    )
                )
                gam = self.model_factory(
                    features.columns,
                    self.alb_imputer.multi_cat_vars,
                    self.lac_imputer.ind_var_name
                )
                gam.fit(features.values, target)
                gams.append(gam)
        self.models[split_i] = combine_mi_gams(gams)

    def get_observed_and_predicted(
        self,
        fold_name: str,
        split_i: int,
        n_samples_per_imp_i: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Sample predicted mortality risks for the train or test fold of a
        given train-test split. Also fetches the corresponding mortality
        labels (these are the same regardless of mice_imp_i and lac_alb_imp_i.

        Returns:
            Observed mortality labels in {0, 1}. Shape is (n_patients_in_fold,)
            Sampled predicted mortality risks in [0, 1]. Shape is
                (n_samples_per_patient, n_patients_in_fold,) where
                n_samples_per_patient = self.cat_imputer.swm.n_mice_imputations
                * self.n_lacalb_imp * n_samples_per_imp_i
        """
        mortality_risks = []
        for mice_imp_i in range(self.cat_imputer.swm.n_mice_imputations):
            for lac_alb_imp_i in range(self.n_lacalb_imp):
                features, labels = self.get_features_and_labels(
                    fold_name=fold_name,
                    split_i=split_i,
                    mice_imp_i=mice_imp_i,
                    lac_alb_imp_i=self._calculate_lac_alb_imp_i(
                        mice_imp_i,
                        lac_alb_imp_i
                    )
                )
                mortality_risks.append(
                    quick_sample(
                        gam=self.models[split_i],
                        sample_at_X=features.values,
                        quantity="mu",
                        n_draws=n_samples_per_imp_i,
                        random_seed=self._calculate_lac_alb_imp_i(
                            mice_imp_i,
                            lac_alb_imp_i
                        )
                    )
                )
        return labels, np.vstack(mortality_risks)

    def get_all_observed_and_median_predicted(
        self,
        fold_name: str,
        n_samples_per_imp_i: int
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Convenience function for preparing input to LogisticScorer. Fetches
        the observed mortality labels from a given fold in every train-test
        split, and the corresponding *median* mortality risks predicted by the
        novel model.

        Returns:
            Each element of this list is an ndarray of observed mortality
                labels in {0, 1}. Shape of each ndarray is (n_patients_in_fold,)
            Each element of this list is an ndarray of median mortality risks
                in [0, 1]. Shape of each ndarray is (n_patients_in_fold,)
        """
        y_obs, y_preds = [], []
        for split_i in pb(
            range(self.cat_imputer.tts.n_splits),
            prefix="Split iteration"
        ):
            y_ob, y_pred = self.get_observed_and_predicted(
                fold_name=fold_name,
                split_i=split_i,
                n_samples_per_imp_i=n_samples_per_imp_i
            )
            y_obs.append(y_ob)
            y_preds.append(np.median(y_pred, axis=0))
        return y_obs, y_preds
