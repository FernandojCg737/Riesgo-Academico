from src.infrastructure.db.models.academic_record_model import RegistroAcademico
from src.infrastructure.db.models.survey_response_model import RespuestaEncuesta
from src.infrastructure.db.models.trained_model_model import ModeloEntrenado
from src.infrastructure.db.models.model_evaluation_model import EvaluacionModelo
from src.infrastructure.db.models.prediction_log_model import HistorialPrediccion

__all__ = [
    "RegistroAcademico",
    "RespuestaEncuesta",
    "ModeloEntrenado",
    "EvaluacionModelo",
    "HistorialPrediccion",
]
