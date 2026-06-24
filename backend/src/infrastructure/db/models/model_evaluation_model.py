from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class EvaluacionModelo(Base):
    __tablename__ = "evaluaciones_modelo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    modelo_id: Mapped[int] = mapped_column(Integer, ForeignKey("modelos_entrenados.id"), nullable=False)

    accuracy_test: Mapped[float] = mapped_column(Float, nullable=True)
    accuracy_train: Mapped[float] = mapped_column(Float, nullable=True)
    precision_clase_1: Mapped[float] = mapped_column(Float, nullable=True)
    recall_clase_1: Mapped[float] = mapped_column(Float, nullable=True)
    recall_train: Mapped[float] = mapped_column(Float, nullable=True)
    f1_clase_1: Mapped[float] = mapped_column(Float, nullable=True)
    f1_train: Mapped[float] = mapped_column(Float, nullable=True)
    roc_auc_test: Mapped[float] = mapped_column(Float, nullable=True)
    roc_auc_train: Mapped[float] = mapped_column(Float, nullable=True)
    falsos_negativos: Mapped[int] = mapped_column(Integer, nullable=True)
    matriz_confusion: Mapped[list] = mapped_column(JSON, nullable=True)
    cv_recall_mean: Mapped[float] = mapped_column(Float, nullable=True)
    cv_recall_std: Mapped[float] = mapped_column(Float, nullable=True)
    classification_report: Mapped[str] = mapped_column(Text, nullable=True)
    evaluado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
