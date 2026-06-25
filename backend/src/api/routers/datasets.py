import io

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from src.application.use_cases.upload_dataset import UploadDataset
from src.infrastructure.repositories.dataset_repository import DatasetRepository

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.get("")
def listar_datasets():
    datasets = DatasetRepository().listar()
    return [
        {
            "id": d.id,
            "nombre": d.nombre,
            "fuente_archivo": d.fuente_archivo,
            "n_registros": d.n_registros,
            "creado_en": d.creado_en.isoformat() if d.creado_en else None,
        }
        for d in datasets
    ]


@router.post("/upload")
def subir_dataset(nombre: str = Form(...), archivo: UploadFile = File(...)):
    extension = (archivo.filename or "").lower().rsplit(".", 1)[-1]
    contenido = archivo.file.read()

    try:
        if extension == "csv":
            df_raw = pd.read_csv(io.BytesIO(contenido))
        elif extension in ("xlsx", "xls"):
            df_raw = pd.read_excel(io.BytesIO(contenido))
        else:
            raise HTTPException(status_code=400, detail="Formato no soportado. Usá un archivo .csv, .xlsx o .xls.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo leer el archivo: {e}")

    try:
        dataset = UploadDataset().ejecutar(nombre=nombre, archivo_nombre=archivo.filename, df_raw=df_raw)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {
        "id": dataset.id,
        "nombre": dataset.nombre,
        "fuente_archivo": dataset.fuente_archivo,
        "n_registros": dataset.n_registros,
    }
