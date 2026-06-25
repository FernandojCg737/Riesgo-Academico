from sqlalchemy import select, update

from src.infrastructure.repositories.model_repository import ModelRepository
from src.infrastructure.db.session import SessionLocal
from src.infrastructure.db.models.trained_model_model import ModeloEntrenado
from src.infrastructure.db.models.model_evaluation_model import EvaluacionModelo

NOMBRES_BASE = ["logistic_regression", "decision_tree", "random_forest"]


class SelectBestModel:
    def __init__(self, dataset_id: int, model_repo: ModelRepository = None):
        self.dataset_id = dataset_id
        self.model_repo = model_repo or ModelRepository(dataset_id=dataset_id)

    def ejecutar(self) -> str:
        print(f"Ejecutando caso de uso: Seleccionar Mejor Modelo (dataset_id={self.dataset_id})...")

        with SessionLocal() as session:
            filas = session.execute(
                select(ModeloEntrenado, EvaluacionModelo)
                .join(EvaluacionModelo, EvaluacionModelo.modelo_id == ModeloEntrenado.id)
                .where(
                    ModeloEntrenado.nombre_interno.in_(NOMBRES_BASE),
                    ModeloEntrenado.dataset_id == self.dataset_id,
                )
            ).all()

            if not filas:
                raise ValueError("No hay evaluaciones registradas. Ejecuta la evaluación primero.")

            # Prioridad: Recall Test (Riesgo) desc, F1-Score Test (Riesgo) desc
            modelo_ganador, evaluacion_ganadora = max(
                filas, key=lambda fila: (fila[1].recall_clase_1, fila[1].f1_clase_1)
            )

            mejor_id = modelo_ganador.nombre_interno
            print(f"  El mejor modelo seleccionado es: {modelo_ganador.nombre_legible} (ID: {mejor_id})")
            print(f"    Recall: {evaluacion_ganadora.recall_clase_1}")
            print(f"    F1-Score: {evaluacion_ganadora.f1_clase_1}")

            pipeline_ganador = self.model_repo.cargar_modelo(mejor_id)
            self.model_repo.guardar_modelo_final(pipeline_ganador)

            session.execute(
                update(ModeloEntrenado)
                .where(ModeloEntrenado.dataset_id == self.dataset_id)
                .values(es_modelo_final=False)
            )
            session.execute(
                update(ModeloEntrenado)
                .where(ModeloEntrenado.id == modelo_ganador.id)
                .values(es_modelo_final=True)
            )
            session.commit()

        print("Selección del mejor modelo finalizada con éxito.")
        return mejor_id
