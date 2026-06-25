from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class RegistroAcademico(Base):
    __tablename__ = "registros_academicos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False, index=True)
    id_estudiante: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    carrera_alumno: Mapped[str] = mapped_column(String, index=True, nullable=False)
    codigo_materia: Mapped[str] = mapped_column(String, index=True, nullable=False)
    materia: Mapped[str] = mapped_column(String, nullable=False)
    nivel_materia: Mapped[int] = mapped_column(Integer, nullable=False)
    repite_materia: Mapped[int] = mapped_column(Integer, nullable=False)
    repite_materia_binaria: Mapped[int] = mapped_column(Integer, nullable=False)
    nota_final: Mapped[float] = mapped_column(Float, nullable=False)
    ppa: Mapped[float] = mapped_column(Float, nullable=False)
    ppac: Mapped[float] = mapped_column(Float, nullable=False)
    fecha_inscripcion: Mapped[date] = mapped_column(Date, nullable=False)
    riesgo_academico: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
