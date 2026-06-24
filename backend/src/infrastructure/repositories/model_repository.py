import joblib
from pathlib import Path
from typing import Any
from src.infrastructure.config.settings import settings, MODEL_FINAL_PATH

class ModelRepository:
    def __init__(self, models_dir: Path = None):
        self.models_dir = models_dir or settings.model_storage_path
        self.final_path = MODEL_FINAL_PATH

    def guardar_modelo(self, nombre: str, pipeline: Any) -> Path:
        ruta = self.models_dir / f"modelo_{nombre}.pkl"
        joblib.dump(pipeline, ruta)
        print(f"Modelo [{nombre}] guardado en: {ruta}")
        return ruta

    def cargar_modelo(self, nombre: str) -> Any:
        ruta = self.models_dir / f"modelo_{nombre}.pkl"
        if not ruta.exists():
            raise FileNotFoundError(f"No existe el modelo {nombre} en {ruta}")
        return joblib.load(ruta)

    def guardar_modelo_final(self, pipeline: Any) -> None:
        joblib.dump(pipeline, self.final_path)
        print(f"Modelo final copiado en: {self.final_path}")

    def cargar_modelo_final(self) -> Any:
        if not self.final_path.exists():
            raise FileNotFoundError(f"No existe el modelo final serializado en {self.final_path}")
        return joblib.load(self.final_path)
