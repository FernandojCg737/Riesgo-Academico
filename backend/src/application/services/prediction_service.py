import pandas as pd
from typing import Dict, Any
from src.infrastructure.repositories.model_repository import ModelRepository
from src.domain.rules.risk_interpretation_rules import obtener_nivel_alerta, obtener_interpretacion
from src.domain.rules.recommendation_rules import generar_recomendaciones
from src.application.services.shap_explanation_service import ShapExplanationService

class PredictionService:
    def __init__(self, model_repo: ModelRepository = None, shap_service: ShapExplanationService = None):
        self.model_repo = model_repo or ModelRepository()
        self.shap_service = shap_service or ShapExplanationService()

    def predecir_con_modelo(
        self,
        carrera_alumno: str,
        codigo_materia: str,
        nivel_materia: int,
        repite_materia_binaria: int,
        ppa: float,
        ppac: float,
        usar_alternativo: bool = False
    ) -> Dict[str, Any]:
        """
        Calcula el riesgo académico para un estudiante.
        Valida que el PPA y PPAC estén entre 0 y 100.
        Permite seleccionar entre el modelo base (con repitencia) y el alternativo (sin repitencia).
        """
        if not (0.0 <= float(ppa) <= 100.0):
            raise ValueError(f"El PPA debe estar en el rango de 0 a 100. Valor actual: {ppa}")
        if not (0.0 <= float(ppac) <= 100.0):
            raise ValueError(f"El PPAC debe estar en el rango de 0 a 100. Valor actual: {ppac}")

        if usar_alternativo:
            pipeline = self.model_repo.cargar_modelo("decision_tree_alt")
            nombre_modelo_usado = "Decision Tree Classifier - Modelo Alternativo (Sin Repitencia)"
        else:
            pipeline = self.model_repo.cargar_modelo_final()
            nombre_modelo_usado = "Decision Tree Classifier - Modelo Base Histórico (Con Repitencia)"

        datos_entrada = pd.DataFrame([{
            "carrera_alumno": str(carrera_alumno).strip().upper(),
            "codigo_materia": str(codigo_materia).strip().upper(),
            "nivel_materia": int(nivel_materia),
            "repite_materia_binaria": int(repite_materia_binaria),
            "ppa": float(ppa),
            "ppac": float(ppac)
        }])

        prediccion = int(pipeline.predict(datos_entrada)[0])
        probabilidades = pipeline.predict_proba(datos_entrada)[0]
        probabilidad_riesgo = float(probabilidades[1])

        alerta = obtener_nivel_alerta(probabilidad_riesgo)
        interpretacion = obtener_interpretacion(probabilidad_riesgo, alerta)

        recomendaciones = generar_recomendaciones(
            prediccion=prediccion,
            repite_materia_binaria=repite_materia_binaria,
            ppa=float(ppa),
            ppac=float(ppac),
            nivel_materia=int(nivel_materia)
        )

        explicacion = self.shap_service.explicar_prediccion(pipeline, datos_entrada)

        return {
            "prediccion": prediccion,
            "etiqueta": "Riesgo académico alto" if prediccion == 1 else "Riesgo académico bajo",
            "probabilidad_riesgo": probabilidad_riesgo,
            "alerta": alerta,
            "interpretacion": interpretacion,
            "recomendaciones": recomendaciones,
            "explicacion": explicacion,
            "modelo_utilizado": nombre_modelo_usado
        }
