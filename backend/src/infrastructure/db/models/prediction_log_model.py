from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class HistorialPrediccion(Base):
    __tablename__ = "historial_predicciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    carrera_alumno: Mapped[str] = mapped_column(String, nullable=False)
    codigo_materia: Mapped[str] = mapped_column(String, nullable=False)
    nivel_materia: Mapped[int] = mapped_column(Integer, nullable=False)
    repite_materia_binaria: Mapped[int] = mapped_column(Integer, nullable=False)
    ppa: Mapped[float] = mapped_column(Float, nullable=False)
    ppac: Mapped[float] = mapped_column(Float, nullable=False)
    usar_alternativo: Mapped[bool] = mapped_column(Boolean, default=False)
    prediccion: Mapped[int] = mapped_column(Integer, nullable=False)
    probabilidad_riesgo: Mapped[float] = mapped_column(Float, nullable=False)
    nivel_alerta: Mapped[str] = mapped_column(String, nullable=False)
    modelo_utilizado: Mapped[str] = mapped_column(String, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
