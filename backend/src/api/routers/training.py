from fastapi import APIRouter, BackgroundTasks

from src.application.use_cases.train_models import TrainModels

router = APIRouter(prefix="/api/train", tags=["training"])

_estado_entrenamiento = {"status": "idle", "error": None}


def _ejecutar_entrenamiento():
    _estado_entrenamiento["status"] = "running"
    _estado_entrenamiento["error"] = None
    try:
        TrainModels().ejecutar()
        _estado_entrenamiento["status"] = "done"
    except Exception as e:
        _estado_entrenamiento["status"] = "error"
        _estado_entrenamiento["error"] = str(e)


@router.post("")
def iniciar_entrenamiento(background_tasks: BackgroundTasks):
    if _estado_entrenamiento["status"] == "running":
        return {"status": "running", "mensaje": "Ya hay un entrenamiento en curso."}

    background_tasks.add_task(_ejecutar_entrenamiento)
    return {"status": "started", "mensaje": "Entrenamiento iniciado en segundo plano."}


@router.get("/status")
def obtener_estado_entrenamiento():
    return _estado_entrenamiento
