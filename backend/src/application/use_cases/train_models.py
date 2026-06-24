from sklearn.model_selection import GroupShuffleSplit
from sqlalchemy import select

from src.infrastructure.config import settings
from src.infrastructure.repositories.academic_repository import AcademicRepository
from src.infrastructure.repositories.model_repository import ModelRepository
from src.infrastructure.db.session import SessionLocal
from src.infrastructure.db.models.trained_model_model import ModeloEntrenado
from src.application.services.preprocessing_service import PreprocessingService
from src.application.services.model_training_service import ModelTrainingService

ALGORITMOS_POR_NOMBRE = {
    "logistic_regression": "logistic_regression",
    "decision_tree": "decision_tree",
    "random_forest": "random_forest",
    "logistic_regression_alt": "logistic_regression",
    "decision_tree_alt": "decision_tree",
    "random_forest_alt": "random_forest",
}

NOMBRES_LEGIBLES = {
    "logistic_regression": "Regresión Logística",
    "decision_tree": "Árbol de Decisión",
    "random_forest": "Random Forest",
    "logistic_regression_alt": "Regresión Logística (Sin Repitencia)",
    "decision_tree_alt": "Árbol de Decisión (Sin Repitencia)",
    "random_forest_alt": "Random Forest (Sin Repitencia)",
}


def _extraer_hiperparametros(pipeline, algoritmo: str) -> dict | None:
    clasificador = pipeline.named_steps["classifier"]
    if algoritmo == "decision_tree":
        return {"max_depth": clasificador.max_depth, "min_samples_leaf": clasificador.min_samples_leaf}
    if algoritmo == "random_forest":
        return {
            "n_estimators": clasificador.n_estimators,
            "max_depth": clasificador.max_depth,
            "min_samples_leaf": clasificador.min_samples_leaf,
        }
    return None


class TrainModels:
    def __init__(
        self,
        academic_repo: AcademicRepository = None,
        model_repo: ModelRepository = None,
        preproc_service: PreprocessingService = None,
        train_service: ModelTrainingService = None
    ):
        self.academic_repo = academic_repo or AcademicRepository()
        self.model_repo = model_repo or ModelRepository()
        self.preproc_service = preproc_service or PreprocessingService()
        self.train_service = train_service or ModelTrainingService()

    def _registrar_modelo(self, nombre_interno: str, ruta_archivo: str, pipeline) -> None:
        """
        Actualiza el registro si ya existe (re-entrenamiento) o lo crea si es la primera vez.
        Se usa upsert en vez de borrar+insertar porque evaluaciones_modelo referencia
        modelos_entrenados.id mediante FK, y borrar rompería esa relación entre corridas.
        """
        algoritmo = ALGORITMOS_POR_NOMBRE[nombre_interno]
        configuracion = "alternativo" if nombre_interno.endswith("_alt") else "base"
        hiperparametros = _extraer_hiperparametros(pipeline, algoritmo)

        with SessionLocal() as session:
            modelo = session.execute(
                select(ModeloEntrenado).where(ModeloEntrenado.nombre_interno == nombre_interno)
            ).scalar_one_or_none()

            if modelo is None:
                modelo = ModeloEntrenado(nombre_interno=nombre_interno)
                session.add(modelo)

            modelo.nombre_legible = NOMBRES_LEGIBLES[nombre_interno]
            modelo.algoritmo = algoritmo
            modelo.configuracion = configuracion
            modelo.ruta_archivo_pkl = str(ruta_archivo)
            modelo.es_modelo_final = False
            modelo.hiperparametros = hiperparametros
            session.commit()

    def ejecutar(self) -> None:
        print("Ejecutando caso de uso: Entrenar Modelos...")

        df = self.academic_repo.cargar_modelo_dataset()
        print(f"  Cargados {len(df)} registros para entrenamiento.")

        X, y, groups = self.preproc_service.separar_predictores_y_objetivo(df)

        gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=settings.RANDOM_STATE)
        train_idx, test_idx = next(gss.split(df, y, groups=groups))

        X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
        groups_train = groups.iloc[train_idx]

        print("  Partición de datos mediante GroupShuffleSplit:")
        print(f"    Entrenamiento: {len(X_train)} registros (estudiantes únicos: {groups_train.nunique()})")
        print(f"    Prueba: {len(test_idx)} registros (estudiantes únicos: {groups.iloc[test_idx].nunique()})")

        print("  Entrenando Regresión Logística estándar...")
        lr_pipeline = self.train_service.entrenar_logistic_regression(X_train, y_train)
        ruta = self.model_repo.guardar_modelo("logistic_regression", lr_pipeline)
        self._registrar_modelo("logistic_regression", ruta, lr_pipeline)

        print("  Entrenando Árbol de Decisión estándar con ajuste de hiperparámetros...")
        dt_pipeline = self.train_service.entrenar_con_tuning_decision_tree(X_train, y_train, groups_train)
        ruta = self.model_repo.guardar_modelo("decision_tree", dt_pipeline)
        self._registrar_modelo("decision_tree", ruta, dt_pipeline)

        print("  Entrenando Random Forest estándar con ajuste de hiperparámetros...")
        rf_pipeline = self.train_service.entrenar_con_tuning_random_forest(X_train, y_train, groups_train)
        ruta = self.model_repo.guardar_modelo("random_forest", rf_pipeline)
        self._registrar_modelo("random_forest", ruta, rf_pipeline)

        print("  [Alternativo] Identificando variables numéricas sin repite_materia_binaria...")
        numericas_alt = [col for col in settings.NUMERICAS if col != "repite_materia_binaria"]

        print("  [Alternativo] Entrenando Regresión Logística...")
        lr_pipeline_alt = self.train_service.entrenar_logistic_regression(
            X_train, y_train, numericas=numericas_alt
        )
        ruta = self.model_repo.guardar_modelo("logistic_regression_alt", lr_pipeline_alt)
        self._registrar_modelo("logistic_regression_alt", ruta, lr_pipeline_alt)

        print("  [Alternativo] Entrenando Árbol de Decisión...")
        dt_pipeline_alt = self.train_service.entrenar_con_tuning_decision_tree(
            X_train, y_train, groups_train, numericas=numericas_alt
        )
        ruta = self.model_repo.guardar_modelo("decision_tree_alt", dt_pipeline_alt)
        self._registrar_modelo("decision_tree_alt", ruta, dt_pipeline_alt)

        print("  [Alternativo] Entrenando Random Forest...")
        rf_pipeline_alt = self.train_service.entrenar_con_tuning_random_forest(
            X_train, y_train, groups_train, numericas=numericas_alt
        )
        ruta = self.model_repo.guardar_modelo("random_forest_alt", rf_pipeline_alt)
        self._registrar_modelo("random_forest_alt", ruta, rf_pipeline_alt)

        print("Entrenamiento de todos los modelos completado de forma exitosa.")
