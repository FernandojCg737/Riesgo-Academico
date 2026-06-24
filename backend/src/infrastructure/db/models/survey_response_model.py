from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class RespuestaEncuesta(Base):
    __tablename__ = "respuestas_encuesta"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_encuesta: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    carrera: Mapped[str] = mapped_column(String, nullable=False)
    semestre_num: Mapped[int] = mapped_column(Integer)
    promedio_actual_orden: Mapped[int] = mapped_column(Integer)
    promedio_actual_estimado: Mapped[float] = mapped_column(Float)
    materias_reprobadas_num: Mapped[float] = mapped_column(Float)
    horas_estudio_semana_num: Mapped[int] = mapped_column(Integer)
    asistencia_ordinal: Mapped[int] = mapped_column(Integer)
    frecuencia_uso_ia_ordinal: Mapped[int] = mapped_column(Integer)
    dependencia_ia_ordinal: Mapped[int] = mapped_column(Integer)
    motivacion_ordinal: Mapped[int] = mapped_column(Integer)
    riesgo_academico_encuesta: Mapped[str] = mapped_column(String)
    riesgo_academico_encuesta_binario: Mapped[int] = mapped_column(Integer, index=True)

    # Columnas descriptivas calculadas en ingesta
    frecuencia_uso_ia_desc: Mapped[str] = mapped_column(String)
    dependencia_ia_desc: Mapped[str] = mapped_column(String)
    motivacion_desc: Mapped[str] = mapped_column(String)
    asistencia_desc: Mapped[str] = mapped_column(String)
    perfil_uso_ia: Mapped[str] = mapped_column(String)
