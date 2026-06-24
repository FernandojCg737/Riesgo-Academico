from typing import Dict, List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.infrastructure.config.settings import settings
from src.infrastructure.db.models.academic_record_model import RegistroAcademico
from src.infrastructure.db.models.trained_model_model import ModeloEntrenado
from src.infrastructure.db.models.model_evaluation_model import EvaluacionModelo

SYSTEM_PROMPT_BASE = """Eres el asistente analítico del "Sistema Predictivo de Riesgo Académico Estudiantil",
un proyecto de ciencia de datos universitario. Respondes en español, de forma breve y clara,
únicamente sobre el dominio de este proyecto (los datos académicos, la encuesta de IA, el modelo
predictivo, sus métricas y la metodología). Si te preguntan algo fuera de ese dominio, indícalo
amablemente y redirige la conversación al proyecto. Usa los datos reales del contexto a continuación,
no inventes cifras.

Contexto actual del sistema:
{contexto}
"""


class ChatbotService:
    def construir_contexto(self, db: Session) -> str:
        total_registros = db.scalar(select(func.count(RegistroAcademico.id))) or 0
        en_riesgo = db.scalar(
            select(func.count(RegistroAcademico.id)).where(RegistroAcademico.riesgo_academico == 1)
        ) or 0
        tasa_riesgo = round((en_riesgo / total_registros) * 100, 2) if total_registros else 0.0

        fila_modelo = db.execute(
            select(ModeloEntrenado, EvaluacionModelo)
            .join(EvaluacionModelo, EvaluacionModelo.modelo_id == ModeloEntrenado.id)
            .where(ModeloEntrenado.es_modelo_final.is_(True))
        ).first()

        if fila_modelo:
            modelo, evaluacion = fila_modelo
            info_modelo = (
                f"- Modelo ganador: {modelo.nombre_legible} ({modelo.configuracion}). "
                f"Recall: {evaluacion.recall_clase_1:.2%}, F1: {evaluacion.f1_clase_1:.4f}, "
                f"Accuracy: {evaluacion.accuracy_test:.2%}, ROC-AUC: {evaluacion.roc_auc_test:.4f}."
            )
        else:
            info_modelo = "- Aún no se ha entrenado/seleccionado un modelo final."

        return (
            f"- Total de registros académicos (dataset histórico 2017): {total_registros}.\n"
            f"- Registros en riesgo académico: {en_riesgo} ({tasa_riesgo}%).\n"
            f"{info_modelo}"
        )

    def responder(self, db: Session, mensajes: List[Dict[str, str]]) -> str:
        api_keys = [k for k in (settings.gemini_api_key, settings.gemini_api_key_backup) if k]
        if not api_keys:
            raise RuntimeError("Chatbot no configurado: falta GEMINI_API_KEY")

        from google import genai
        from google.genai import errors as genai_errors
        from google.genai import types

        contexto = self.construir_contexto(db)
        contenidos = [
            types.Content(
                role="model" if m["role"] == "assistant" else "user",
                parts=[types.Part(text=m["content"])],
            )
            for m in mensajes
        ]

        # Si la key principal agotó su cuota gratuita diaria (429), reintenta
        # automáticamente con la key de respaldo antes de fallar.
        for indice, api_key in enumerate(api_keys):
            es_ultima = indice == len(api_keys) - 1
            cliente = genai.Client(api_key=api_key)
            try:
                respuesta = cliente.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contenidos,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT_BASE.format(contexto=contexto),
                        max_output_tokens=512,
                    ),
                )
                return respuesta.text or ""
            except genai_errors.ClientError as e:
                if e.code == 429 and not es_ultima:
                    continue
                if e.code == 429:
                    raise RuntimeError(
                        "El chatbot alcanzó el límite de consultas gratuitas de la IA por ahora. "
                        "Esperá unos minutos e intentá de nuevo."
                    ) from e
                raise RuntimeError(f"El servicio de IA rechazó la consulta ({e.status}).") from e
            except genai_errors.APIError as e:
                raise RuntimeError(f"El servicio de IA no está disponible en este momento ({e.status}).") from e

        raise RuntimeError("El chatbot no pudo responder en este momento.")
