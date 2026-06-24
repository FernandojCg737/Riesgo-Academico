from fastapi import APIRouter, HTTPException

from src.application.use_cases.prepare_academic_dataset import PrepareAcademicDataset
from src.application.use_cases.prepare_survey_dataset import PrepareSurveyDataset

router = APIRouter(prefix="/api/data", tags=["data-ingestion"])


@router.post("/ingest/academic")
def ingest_academic():
    try:
        PrepareAcademicDataset().ejecutar()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": "ok", "mensaje": "Dataset académico ingerido correctamente."}


@router.post("/ingest/survey")
def ingest_survey():
    try:
        PrepareSurveyDataset().ejecutar()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": "ok", "mensaje": "Dataset de encuesta ingerido correctamente."}
