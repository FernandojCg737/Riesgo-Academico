import pandas as pd

from src.infrastructure.repositories.academic_repository import AcademicRepository
from src.infrastructure.repositories.dataset_repository import DatasetRepository
from src.infrastructure.db.models.dataset_model import Dataset
from src.application.use_cases.prepare_academic_dataset import PrepareAcademicDataset


class UploadDataset:
    def __init__(
        self,
        dataset_repo: DatasetRepository = None,
        academic_repo: AcademicRepository = None,
    ):
        self.dataset_repo = dataset_repo or DatasetRepository()
        self.academic_repo = academic_repo or AcademicRepository()

    def ejecutar(self, nombre: str, archivo_nombre: str, df_raw: pd.DataFrame) -> Dataset:
        dataset = self.dataset_repo.crear(nombre=nombre, fuente_archivo=archivo_nombre)
        try:
            n = PrepareAcademicDataset(self.academic_repo).ejecutar(dataset_id=dataset.id, df=df_raw)
        except Exception:
            self.dataset_repo.eliminar(dataset.id)
            raise

        self.dataset_repo.actualizar_n_registros(dataset.id, n)
        dataset.n_registros = n
        return dataset
