import numpy as np
import pandas as pd
from typing import Any, Dict, List

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier


def _agrupar_por_variable_original(nombre_feature: str) -> str:
    fn_clean = nombre_feature.replace("num__", "").replace("cat__", "")
    if fn_clean.startswith("repite_materia_binaria"):
        return "repite_materia_binaria"
    if fn_clean.startswith("codigo_materia"):
        return "codigo_materia"
    if fn_clean.startswith("ppac"):
        return "ppac"
    if fn_clean.startswith("ppa"):
        return "ppa"
    if fn_clean.startswith("nivel_materia"):
        return "nivel_materia"
    if fn_clean.startswith("carrera_alumno"):
        return "carrera_alumno"
    return fn_clean


class ShapExplanationService:
    """
    Calcula la contribución de cada variable a UNA predicción individual (no global),
    reutilizando el mismo pipeline (preprocessor + classifier) ya entrenado.
    """

    def explicar_prediccion(self, pipeline: Any, datos_entrada: pd.DataFrame, top_n: int = 5) -> List[Dict]:
        try:
            import shap

            preprocessor = pipeline.named_steps["preprocessor"]
            classifier = pipeline.named_steps["classifier"]

            X_transformado = preprocessor.transform(datos_entrada)
            if hasattr(X_transformado, "toarray"):
                X_transformado = X_transformado.toarray()

            feature_names = preprocessor.get_feature_names_out()

            if isinstance(classifier, (DecisionTreeClassifier, RandomForestClassifier)):
                explainer = shap.TreeExplainer(classifier)
                shap_values = explainer.shap_values(X_transformado)
                if isinstance(shap_values, list):
                    valores = np.array(shap_values[1][0])
                else:
                    valores = np.array(shap_values[0])
                    if valores.ndim == 2:
                        valores = valores[:, 1]
            elif isinstance(classifier, LogisticRegression):
                masker = shap.maskers.Independent(np.zeros((1, X_transformado.shape[1])))
                explainer = shap.LinearExplainer(classifier, masker)
                valores = np.array(explainer.shap_values(X_transformado)[0])
            else:
                return []

            mapeo = [_agrupar_por_variable_original(fn) for fn in feature_names]
            df = pd.DataFrame({"variable": mapeo, "contribucion": valores})
            df_agrupado = df.groupby("variable")["contribucion"].sum().reset_index()
            df_agrupado["abs"] = df_agrupado["contribucion"].abs()
            df_agrupado = df_agrupado.sort_values(by="abs", ascending=False).head(top_n)

            return [
                {
                    "variable": row["variable"],
                    "contribucion": round(float(row["contribucion"]), 4),
                    "direccion": "aumenta" if row["contribucion"] > 0 else "disminuye",
                }
                for _, row in df_agrupado.iterrows()
            ]
        except Exception as e:
            print(f"Advertencia: no se pudo calcular la explicación SHAP de esta predicción: {e}")
            return []
