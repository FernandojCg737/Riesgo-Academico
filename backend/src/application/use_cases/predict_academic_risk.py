from typing import Dict, Any
from src.infrastructure.repositories.model_repository import ModelRepository
from src.application.services.prediction_service import PredictionService

class PredictAcademicRisk:
    def __init__(self, model_repo: ModelRepository = None):
        self.model_repo = model_repo or ModelRepository()
        self.prediction_service = PredictionService(self.model_repo)

    def ejecutar(
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
        Caso de uso para calcular el riesgo académico de un estudiante en una asignatura.
        Permite seleccionar el modelo alternativo sin repitencia si usar_alternativo = True.
        """
        return self.prediction_service.predecir_con_modelo(
            carrera_alumno=carrera_alumno,
            codigo_materia=codigo_materia,
            nivel_materia=nivel_materia,
            repite_materia_binaria=repite_materia_binaria,
            ppa=ppa,
            ppac=ppac,
            usar_alternativo=usar_alternativo
        )
