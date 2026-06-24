from sklearn.model_selection import GridSearchCV, GroupShuffleSplit
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from typing import Any
import pandas as pd
from src.infrastructure.config import settings
from src.infrastructure.ml import pipelines

class ModelTrainingService:
    def __init__(self, random_state: int = settings.RANDOM_STATE):
        self.random_state = random_state

    def entrenar_logistic_regression(self, X_train: pd.DataFrame, y_train: pd.Series, numericas: list = None, categoricas: list = None) -> Any:
        """
        Entrena el pipeline de Regresión Logística con escalado.
        """
        lr = LogisticRegression(
            class_weight="balanced",
            random_state=self.random_state,
            max_iter=1000
        )
        # Habilitamos escalar_numericas=True para la Regresión Logística
        pipeline = pipelines.crear_pipeline_completo(lr, escalar_numericas=True, numericas=numericas, categoricas=categoricas)
        pipeline.fit(X_train, y_train)
        return pipeline

    def entrenar_con_tuning_decision_tree(self, X_train: pd.DataFrame, y_train: pd.Series, groups_train: pd.Series, numericas: list = None, categoricas: list = None) -> Any:
        """
        Ajusta el árbol de decisión usando GridSearch con validación agrupada GroupShuffleSplit.
        """
        dt = DecisionTreeClassifier(
            class_weight="balanced",
            random_state=self.random_state
        )
        pipeline = pipelines.crear_pipeline_completo(dt, escalar_numericas=False, numericas=numericas, categoricas=categoricas)

        gss = GroupShuffleSplit(n_splits=3, test_size=0.2, random_state=self.random_state)

        grid = GridSearchCV(
            estimator=pipeline,
            param_grid=settings.PARAM_GRID_DT,
            cv=gss,
            scoring="recall",
            n_jobs=-1
        )

        grid.fit(X_train, y_train, groups=groups_train)
        print(f"Mejores parámetros para Decision Tree: {grid.best_params_}")
        return grid.best_estimator_

    def entrenar_con_tuning_random_forest(self, X_train: pd.DataFrame, y_train: pd.Series, groups_train: pd.Series, numericas: list = None, categoricas: list = None) -> Any:
        """
        Ajusta el Random Forest usando GridSearch con validación agrupada GroupShuffleSplit.
        """
        rf = RandomForestClassifier(
            class_weight="balanced",
            random_state=self.random_state,
            n_jobs=-1
        )
        pipeline = pipelines.crear_pipeline_completo(rf, escalar_numericas=False, numericas=numericas, categoricas=categoricas)

        gss = GroupShuffleSplit(n_splits=3, test_size=0.2, random_state=self.random_state)

        grid = GridSearchCV(
            estimator=pipeline,
            param_grid=settings.PARAM_GRID_RF,
            cv=gss,
            scoring="recall",
            n_jobs=-1
        )

        grid.fit(X_train, y_train, groups=groups_train)
        print(f"Mejores parámetros para Random Forest: {grid.best_params_}")
        return grid.best_estimator_
