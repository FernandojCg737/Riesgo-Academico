from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from typing import Any
from src.infrastructure.config import settings

def crear_preprocesador(escalar_numericas: bool = False, numericas: list = None, categoricas: list = None) -> ColumnTransformer:
    """
    Crea el ColumnTransformer para preprocesamiento de variables categóricas y numéricas.
    """
    if numericas is None:
        numericas = settings.NUMERICAS
    if categoricas is None:
        categoricas = settings.CATEGORICAS

    # Pipeline para variables categóricas: imputador constante + OneHotEncoder
    cat_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="DESCONOCIDO")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    # Pipeline para variables numéricas: imputador mediana (+ opcionalmente StandardScaler)
    if escalar_numericas:
        num_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])
    else:
        num_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median"))
        ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, numericas),
            ("cat", cat_transformer, categoricas)
        ]
    )

    return preprocessor

def crear_pipeline_completo(modelo: Any, escalar_numericas: bool = False, numericas: list = None, categoricas: list = None) -> Pipeline:
    """
    Ensambla el preprocesador y el modelo de clasificación en un Pipeline unificado.
    """
    preprocessor = crear_preprocesador(escalar_numericas=escalar_numericas, numericas=numericas, categoricas=categoricas)
    return Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", modelo)
    ])
