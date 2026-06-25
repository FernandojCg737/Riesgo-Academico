from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class ModeloEntrenado(Base):
    __tablename__ = "modelos_entrenados"
    __table_args__ = (UniqueConstraint("dataset_id", "nombre_interno", name="uq_modelo_dataset_nombre"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False, index=True)
    nombre_interno: Mapped[str] = mapped_column(String, nullable=False)
    nombre_legible: Mapped[str] = mapped_column(String, nullable=False)
    algoritmo: Mapped[str] = mapped_column(String, nullable=False)
    configuracion: Mapped[str] = mapped_column(String, nullable=False)
    ruta_archivo_pkl: Mapped[str] = mapped_column(String, nullable=False)
    es_modelo_final: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    hiperparametros: Mapped[dict] = mapped_column(JSON, nullable=True)
    entrenado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
