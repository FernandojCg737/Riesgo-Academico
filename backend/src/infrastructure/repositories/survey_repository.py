import pandas as pd
from pathlib import Path
from sqlalchemy import delete

from src.infrastructure.config.settings import SURVEY_RAW_PATH
from src.infrastructure.db.session import SessionLocal, engine
from src.infrastructure.db.models.survey_response_model import RespuestaEncuesta


class SurveyRepository:
    def __init__(self, raw_path: Path = SURVEY_RAW_PATH):
        self.raw_path = raw_path

    def cargar_raw(self) -> pd.DataFrame:
        if not self.raw_path.exists():
            raise FileNotFoundError(f"No existe el archivo de encuesta raw en {self.raw_path}")
        return pd.read_csv(self.raw_path)

    def persistir_registros(self, df: pd.DataFrame) -> None:
        """
        Reemplaza el contenido de la tabla respuestas_encuesta con el DataFrame procesado
        (idempotente: trunca antes de insertar para permitir re-ejecutar la ingesta).
        """
        columnas_tabla = [
            "id_encuesta", "carrera", "semestre_num", "promedio_actual_orden",
            "promedio_actual_estimado", "materias_reprobadas_num", "horas_estudio_semana_num",
            "asistencia_ordinal", "frecuencia_uso_ia_ordinal", "dependencia_ia_ordinal",
            "motivacion_ordinal", "riesgo_academico_encuesta", "riesgo_academico_encuesta_binario",
            "frecuencia_uso_ia_desc", "dependencia_ia_desc", "motivacion_desc",
            "asistencia_desc", "perfil_uso_ia",
        ]
        df_db = df[columnas_tabla].copy()

        with SessionLocal() as session:
            session.execute(delete(RespuestaEncuesta))
            session.commit()

        df_db.to_sql(
            RespuestaEncuesta.__tablename__,
            con=engine,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )
        print(f"Respuestas de encuesta persistidas en Postgres: {len(df_db)} filas.")

    def cargar_modelo_dataset(self) -> pd.DataFrame:
        return pd.read_sql(f"SELECT * FROM {RespuestaEncuesta.__tablename__}", con=engine)
