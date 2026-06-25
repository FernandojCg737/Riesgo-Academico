from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.application.use_cases.evaluate_models import EvaluateModels
from src.application.use_cases.select_best_model import SelectBestModel
from src.application.services.model_explanation_service import ModelExplanationService
from src.infrastructure.db.models.trained_model_model import ModeloEntrenado
from src.infrastructure.db.models.model_evaluation_model import EvaluacionModelo
from src.infrastructure.repositories.model_repository import ModelRepository

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])

_estados_evaluacion: dict[int, dict] = {}


def _estado_de(dataset_id: int) -> dict:
    return _estados_evaluacion.setdefault(dataset_id, {"status": "idle", "error": None})


def _ejecutar_evaluacion_y_seleccion(dataset_id: int):
    estado = _estado_de(dataset_id)
    estado["status"] = "running"
    estado["error"] = None
    try:
        EvaluateModels(dataset_id=dataset_id).ejecutar()
        SelectBestModel(dataset_id=dataset_id).ejecutar()
        estado["status"] = "done"
    except Exception as e:
        estado["status"] = "error"
        estado["error"] = str(e)


@router.post("/run")
def ejecutar_evaluacion(background_tasks: BackgroundTasks, dataset_id: int = Body(..., embed=True)):
    estado = _estado_de(dataset_id)
    if estado["status"] == "running":
        return {"status": "running", "mensaje": "Ya hay una evaluación en curso."}

    background_tasks.add_task(_ejecutar_evaluacion_y_seleccion, dataset_id)
    return {"status": "started", "mensaje": "Evaluación y selección iniciadas en segundo plano."}


@router.get("/status")
def obtener_estado_evaluacion(dataset_id: int = Query(...)):
    return _estado_de(dataset_id)


@router.get("/metrics")
def obtener_metricas(dataset_id: int = Query(...), db: Session = Depends(get_db)):
    filas = db.execute(
        select(ModeloEntrenado, EvaluacionModelo)
        .join(EvaluacionModelo, EvaluacionModelo.modelo_id == ModeloEntrenado.id)
        .where(ModeloEntrenado.dataset_id == dataset_id)
        .order_by(ModeloEntrenado.id)
    ).all()

    return [
        {
            "nombre_interno": modelo.nombre_interno,
            "nombre_legible": modelo.nombre_legible,
            "configuracion": modelo.configuracion,
            "es_modelo_final": modelo.es_modelo_final,
            "accuracy_test": evaluacion.accuracy_test,
            "accuracy_train": evaluacion.accuracy_train,
            "precision_clase_1": evaluacion.precision_clase_1,
            "recall_clase_1": evaluacion.recall_clase_1,
            "recall_train": evaluacion.recall_train,
            "f1_clase_1": evaluacion.f1_clase_1,
            "f1_train": evaluacion.f1_train,
            "roc_auc_test": evaluacion.roc_auc_test,
            "roc_auc_train": evaluacion.roc_auc_train,
            "falsos_negativos": evaluacion.falsos_negativos,
            "matriz_confusion": evaluacion.matriz_confusion,
            "cv_recall_mean": evaluacion.cv_recall_mean,
            "cv_recall_std": evaluacion.cv_recall_std,
        }
        for modelo, evaluacion in filas
    ]


@router.get("/best-model")
def obtener_mejor_modelo(dataset_id: int = Query(...), db: Session = Depends(get_db)):
    fila = db.execute(
        select(ModeloEntrenado, EvaluacionModelo)
        .join(EvaluacionModelo, EvaluacionModelo.modelo_id == ModeloEntrenado.id)
        .where(ModeloEntrenado.dataset_id == dataset_id, ModeloEntrenado.es_modelo_final.is_(True))
    ).first()

    if not fila:
        raise HTTPException(status_code=404, detail="Aún no se ha seleccionado un modelo final.")

    modelo, evaluacion = fila
    return {
        "modelo_seleccionado": modelo.nombre_interno,
        "nombre_modelo": modelo.nombre_legible,
        "hiperparametros": modelo.hiperparametros,
        "metricas": {
            "recall_clase_1": evaluacion.recall_clase_1,
            "f1_score_clase_1": evaluacion.f1_clase_1,
            "accuracy": evaluacion.accuracy_test,
            "precision_clase_1": evaluacion.precision_clase_1,
        },
    }


@router.get("/feature-importance")
def obtener_importancia_variables(dataset_id: int = Query(...), grouped: bool = False):
    try:
        pipeline = ModelRepository(dataset_id=dataset_id).cargar_modelo_final()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    servicio = ModelExplanationService()
    df = (
        servicio.obtener_importancia_variables_agrupada(pipeline)
        if grouped
        else servicio.obtener_importancia_variables(pipeline)
    )
    return df.to_dict(orient="records")


@router.get("/decision-tree-rules")
def obtener_reglas_decision_tree(dataset_id: int = Query(...)):
    try:
        pipeline = ModelRepository(dataset_id=dataset_id).cargar_modelo_final()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    reglas = ModelExplanationService().obtener_reglas_decision_tree(pipeline)
    return {"reglas": reglas}
