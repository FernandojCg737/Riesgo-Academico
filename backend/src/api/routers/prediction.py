from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.application.use_cases.predict_academic_risk import PredictAcademicRisk
from src.infrastructure.db.models.prediction_log_model import HistorialPrediccion

router = APIRouter(prefix="/api/predict", tags=["prediction"])


class PrediccionRequest(BaseModel):
    dataset_id: int = 1
    carrera_alumno: str
    codigo_materia: str
    nivel_materia: int = Field(ge=1, le=9)
    repite_materia_binaria: int = Field(ge=0, le=1)
    ppa: float = Field(ge=0.0, le=100.0)
    ppac: float = Field(ge=0.0, le=100.0)
    usar_alternativo: bool = False


class ExplicacionItem(BaseModel):
    variable: str
    contribucion: float
    direccion: str


class PrediccionResponse(BaseModel):
    prediccion: int
    etiqueta: str
    probabilidad_riesgo: float
    alerta: str
    interpretacion: str
    recomendaciones: List[str]
    explicacion: List[ExplicacionItem] = []
    modelo_utilizado: str


@router.post("", response_model=PrediccionResponse)
def predecir_riesgo(payload: PrediccionRequest, db: Session = Depends(get_db)):
    try:
        resultado = PredictAcademicRisk(dataset_id=payload.dataset_id).ejecutar(
            carrera_alumno=payload.carrera_alumno,
            codigo_materia=payload.codigo_materia,
            nivel_materia=payload.nivel_materia,
            repite_materia_binaria=payload.repite_materia_binaria,
            ppa=payload.ppa,
            ppac=payload.ppac,
            usar_alternativo=payload.usar_alternativo,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=409, detail=f"El modelo aún no ha sido entrenado: {e}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    db.add(HistorialPrediccion(
        carrera_alumno=payload.carrera_alumno,
        codigo_materia=payload.codigo_materia,
        nivel_materia=payload.nivel_materia,
        repite_materia_binaria=payload.repite_materia_binaria,
        ppa=payload.ppa,
        ppac=payload.ppac,
        usar_alternativo=payload.usar_alternativo,
        prediccion=resultado["prediccion"],
        probabilidad_riesgo=resultado["probabilidad_riesgo"],
        nivel_alerta=resultado["alerta"],
        modelo_utilizado=resultado["modelo_utilizado"],
    ))
    db.commit()

    return resultado


@router.get("/historial")
def obtener_historial(limit: int = 20, db: Session = Depends(get_db)):
    registros = (
        db.query(HistorialPrediccion)
        .order_by(HistorialPrediccion.creado_en.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "carrera_alumno": r.carrera_alumno,
            "codigo_materia": r.codigo_materia,
            "prediccion": r.prediccion,
            "probabilidad_riesgo": r.probabilidad_riesgo,
            "nivel_alerta": r.nivel_alerta,
            "modelo_utilizado": r.modelo_utilizado,
            "creado_en": r.creado_en.isoformat(),
        }
        for r in registros
    ]
