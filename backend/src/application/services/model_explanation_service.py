import pandas as pd
import numpy as np
from sklearn.tree import export_text
from typing import Any

class ModelExplanationService:
    def obtener_importancia_variables(self, pipeline: Any) -> pd.DataFrame:
        """
        Extrae y ordena la importancia de las variables para clasificadores basados en árboles.
        """
        preprocessor = pipeline.named_steps["preprocessor"]
        classifier = pipeline.named_steps["classifier"]

        if not hasattr(classifier, "feature_importances_"):
            if hasattr(classifier, "coef_"):
                importances = np.abs(classifier.coef_[0])
            else:
                return pd.DataFrame(columns=["Variable", "Importancia"])
        else:
            importances = classifier.feature_importances_

        feature_names = preprocessor.get_feature_names_out()

        cleaned_feature_names = []
        for fn in feature_names:
            fn_clean = fn.replace("num__", "").replace("cat__", "")
            fn_clean = fn_clean.replace("carrera_alumno_", "Carrera: ")
            fn_clean = fn_clean.replace("codigo_materia_", "Materia: ")
            fn_clean = fn_clean.replace("repite_materia_binaria", "Materia Repetida (Sí/No)")
            cleaned_feature_names.append(fn_clean)

        df_imp = pd.DataFrame({
            "Variable": cleaned_feature_names,
            "Importancia": importances
        }).sort_values(by="Importancia", ascending=False)

        return df_imp

    def obtener_reglas_decision_tree(self, pipeline: Any) -> str:
        """
        Exporta las reglas lógicas del árbol de decisión en formato de texto.
        """
        preprocessor = pipeline.named_steps["preprocessor"]
        classifier = pipeline.named_steps["classifier"]

        from sklearn.tree import DecisionTreeClassifier
        if not isinstance(classifier, DecisionTreeClassifier):
            return "El modelo final no es un árbol de decisión."

        feature_names = preprocessor.get_feature_names_out()
        cleaned_feature_names = [fn.replace("num__", "").replace("cat__", "") for fn in feature_names]

        reglas_texto = export_text(classifier, feature_names=list(cleaned_feature_names))
        return reglas_texto

    def obtener_importancia_variables_agrupada(self, pipeline: Any) -> pd.DataFrame:
        """
        Extrae la importancia de variables y las agrupa sumando por su variable original.
        """
        preprocessor = pipeline.named_steps["preprocessor"]
        classifier = pipeline.named_steps["classifier"]

        if not hasattr(classifier, "feature_importances_"):
            if hasattr(classifier, "coef_"):
                importances = np.abs(classifier.coef_[0])
            else:
                return pd.DataFrame(columns=["Variable", "Importancia"])
        else:
            importances = classifier.feature_importances_

        feature_names = preprocessor.get_feature_names_out()

        mapeo = []
        for fn in feature_names:
            fn_clean = fn.replace("num__", "").replace("cat__", "")
            if fn_clean.startswith("repite_materia_binaria"):
                mapeo.append("repite_materia_binaria")
            elif fn_clean.startswith("codigo_materia"):
                mapeo.append("codigo_materia")
            elif fn_clean.startswith("ppac"):
                mapeo.append("ppac")
            elif fn_clean.startswith("ppa"):
                mapeo.append("ppa")
            elif fn_clean.startswith("nivel_materia"):
                mapeo.append("nivel_materia")
            elif fn_clean.startswith("carrera_alumno"):
                mapeo.append("carrera_alumno")
            else:
                mapeo.append(fn_clean)

        df_raw = pd.DataFrame({
            "VariableOriginal": mapeo,
            "Importancia": importances
        })

        df_grouped = df_raw.groupby("VariableOriginal")["Importancia"].sum().reset_index()
        df_grouped = df_grouped.rename(columns={"VariableOriginal": "Variable"})
        df_grouped = df_grouped.sort_values(by="Importancia", ascending=False)
        return df_grouped
