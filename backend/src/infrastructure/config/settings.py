from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://academic_user:academic_pass@localhost:5432/academic_risk_db"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    environment: str = "development"
    cors_origins: str = "http://localhost:3000"

    model_storage_path: Path = Path("models_storage")
    reports_storage_path: Path = Path("reports_storage")
    raw_data_path: Path = Path("data/raw")

    umbral_aprobacion: int = 51
    random_state: int = 42
    test_size: float = 0.2

    gemini_api_key: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()

# Render (y otros proveedores) entregan la cadena de conexión como "postgresql://",
# pero SQLAlchemy con el driver psycopg2 requiere el prefijo "postgresql+psycopg2://".
if settings.database_url.startswith("postgresql://"):
    settings.database_url = settings.database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

for folder in [settings.model_storage_path, settings.reports_storage_path, settings.raw_data_path]:
    folder.mkdir(parents=True, exist_ok=True)

# Alias en mayúsculas para mantener compatibilidad con la lógica de negocio portada literal
UMBRAL_APROBACION = settings.umbral_aprobacion
RANDOM_STATE = settings.random_state
TEST_SIZE = settings.test_size

# Rutas de archivos crudos
ACADEMIC_RAW_PATH = settings.raw_data_path / "dataset_2017.csv"
SURVEY_RAW_PATH = settings.raw_data_path / "dataset_encuesta_ia.csv"

# Rutas de modelos serializados
MODEL_FINAL_PATH = settings.model_storage_path / "modelo_final.pkl"

# Estructura del pipeline de modelado
CATEGORICAS = ["carrera_alumno", "codigo_materia"]
NUMERICAS = ["nivel_materia", "repite_materia_binaria", "ppa", "ppac"]
PREDICTORES = CATEGORICAS + NUMERICAS
TARGET = "riesgo_academico"

# Rejillas de Hiperparámetros para Tuning
PARAM_GRID_DT = {
    "classifier__max_depth": [4, 5, 6, 8, 10],
    "classifier__min_samples_leaf": [10, 20, 50],
}

PARAM_GRID_RF = {
    "classifier__n_estimators": [200],
    "classifier__max_depth": [None, 8, 10, 15],
    "classifier__min_samples_leaf": [5, 10, 20],
}
