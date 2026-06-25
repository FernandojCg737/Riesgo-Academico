from fastapi import APIRouter, BackgroundTasks, Body, Query

from src.application.use_cases.train_models import TrainModels

router = APIRouter(prefix="/api/train", tags=["training"])

_estados_entrenamiento: dict[int, dict] = {}


def _estado_de(dataset_id: int) -> dict:
    return _estados_entrenamiento.setdefault(dataset_id, {"status": "idle", "error": None})


def _ejecutar_entrenamiento(dataset_id: int):
    estado = _estado_de(dataset_id)
    estado["status"] = "running"
    estado["error"] = None
    try:
        TrainModels(dataset_id=dataset_id).ejecutar()
        estado["status"] = "done"
    except Exception as e:
        estado["status"] = "error"
        estado["error"] = str(e)


@router.post("")
def iniciar_entrenamiento(background_tasks: BackgroundTasks, dataset_id: int = Body(..., embed=True)):
    estado = _estado_de(dataset_id)
    if estado["status"] == "running":
        return {"status": "running", "mensaje": "Ya hay un entrenamiento en curso."}

    background_tasks.add_task(_ejecutar_entrenamiento, dataset_id)
    return {"status": "started", "mensaje": "Entrenamiento iniciado en segundo plano."}


@router.get("/status")
def obtener_estado_entrenamiento(dataset_id: int = Query(...)):
    return _estado_de(dataset_id)
