from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.infrastructure.db.models.academic_record_model import RegistroAcademico

router = APIRouter(prefix="/api/academic", tags=["academic-data"])


@router.get("/summary")
def obtener_resumen(dataset_id: int = Query(...), db: Session = Depends(get_db)):
    base = select(RegistroAcademico).where(RegistroAcademico.dataset_id == dataset_id)
    total_registros = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    estudiantes_unicos = db.scalar(
        select(func.count(func.distinct(RegistroAcademico.id_estudiante))).where(RegistroAcademico.dataset_id == dataset_id)
    ) or 0
    materias_unicas = db.scalar(
        select(func.count(func.distinct(RegistroAcademico.codigo_materia))).where(RegistroAcademico.dataset_id == dataset_id)
    ) or 0
    en_riesgo = db.scalar(
        select(func.count(RegistroAcademico.id)).where(
            RegistroAcademico.dataset_id == dataset_id, RegistroAcademico.riesgo_academico == 1
        )
    ) or 0

    tasa_riesgo = round((en_riesgo / total_registros) * 100, 2) if total_registros else 0.0

    return {
        "total_registros": total_registros,
        "estudiantes_unicos": estudiantes_unicos,
        "materias_unicas": materias_unicas,
        "registros_en_riesgo": en_riesgo,
        "tasa_riesgo_porcentaje": tasa_riesgo,
    }


@router.get("/records")
def obtener_registros(
    dataset_id: int = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=10000),
    carrera_alumno: Optional[str] = None,
    nivel_materia: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = select(RegistroAcademico).where(RegistroAcademico.dataset_id == dataset_id)
    if carrera_alumno:
        query = query.where(RegistroAcademico.carrera_alumno == carrera_alumno.strip().upper())
    if nivel_materia is not None:
        query = query.where(RegistroAcademico.nivel_materia == nivel_materia)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0

    registros = db.scalars(
        query.order_by(RegistroAcademico.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": r.id,
                "carrera_alumno": r.carrera_alumno,
                "codigo_materia": r.codigo_materia,
                "materia": r.materia,
                "nivel_materia": r.nivel_materia,
                "repite_materia_binaria": r.repite_materia_binaria,
                "nota_final": r.nota_final,
                "ppa": r.ppa,
                "ppac": r.ppac,
                "riesgo_academico": r.riesgo_academico,
            }
            for r in registros
        ],
    }
