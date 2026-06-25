from typing import List, Optional

from sqlalchemy import select

from src.infrastructure.db.session import SessionLocal
from src.infrastructure.db.models.dataset_model import Dataset


class DatasetRepository:
    def listar(self) -> List[Dataset]:
        with SessionLocal() as session:
            return list(session.scalars(select(Dataset).order_by(Dataset.id)).all())

    def obtener(self, dataset_id: int) -> Optional[Dataset]:
        with SessionLocal() as session:
            return session.get(Dataset, dataset_id)

    def crear(self, nombre: str, fuente_archivo: str) -> Dataset:
        with SessionLocal() as session:
            dataset = Dataset(nombre=nombre, fuente_archivo=fuente_archivo, n_registros=0)
            session.add(dataset)
            session.commit()
            session.refresh(dataset)
            return dataset

    def actualizar_n_registros(self, dataset_id: int, n: int) -> None:
        with SessionLocal() as session:
            dataset = session.get(Dataset, dataset_id)
            dataset.n_registros = n
            session.commit()

    def eliminar(self, dataset_id: int) -> None:
        with SessionLocal() as session:
            dataset = session.get(Dataset, dataset_id)
            if dataset:
                session.delete(dataset)
                session.commit()
