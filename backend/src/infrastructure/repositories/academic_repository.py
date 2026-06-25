import pandas as pd
from pathlib import Path
from sqlalchemy import delete, text

from src.infrastructure.config.settings import ACADEMIC_RAW_PATH, PREDICTORES, TARGET
from src.infrastructure.db.session import SessionLocal, engine
from src.infrastructure.db.models.academic_record_model import RegistroAcademico


class AcademicRepository:
    def __init__(self, raw_path: Path = ACADEMIC_RAW_PATH):
        self.raw_path = raw_path

    def cargar_raw(self) -> pd.DataFrame:
        if not self.raw_path.exists():
            raise FileNotFoundError(f"No existe el archivo académico raw en {self.raw_path}")
        return pd.read_csv(self.raw_path)

    def persistir_registros(self, df: pd.DataFrame, dataset_id: int) -> None:
        """
        Reemplaza el contenido del dataset_id indicado dentro de registros_academicos
        (idempotente: borra solo las filas de ese dataset antes de insertar, sin tocar
        los datos de otros datasets).
        """
        columnas_tabla = [
            "id_estudiante", "carrera_alumno", "codigo_materia", "materia",
            "nivel_materia", "repite_materia", "repite_materia_binaria",
            "nota_final", "ppa", "ppac", "fecha_inscripcion", "riesgo_academico",
        ]
        df_db = df[columnas_tabla].copy()
        df_db["dataset_id"] = dataset_id

        with SessionLocal() as session:
            session.execute(delete(RegistroAcademico).where(RegistroAcademico.dataset_id == dataset_id))
            session.commit()

        df_db.to_sql(
            RegistroAcademico.__tablename__,
            con=engine,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )
        print(f"Registros académicos persistidos en Postgres (dataset {dataset_id}): {len(df_db)} filas.")

    def cargar_modelo_dataset(self, dataset_id: int) -> pd.DataFrame:
        """
        Ordena por 'id' para que el orden de filas sea determinístico (coincide con el
        orden de inserción/CSV original), ya que GroupShuffleSplit con random_state fijo
        depende del orden en que aparecen los grupos.
        """
        columnas = ["id_estudiante"] + PREDICTORES + [TARGET]
        query = text(
            f"SELECT {', '.join(columnas)} FROM {RegistroAcademico.__tablename__} "
            "WHERE dataset_id = :dataset_id ORDER BY id"
        )
        return pd.read_sql(query, con=engine, params={"dataset_id": dataset_id})

    def cargar_completo_limpio(self, dataset_id: int) -> pd.DataFrame:
        query = text(
            f"SELECT * FROM {RegistroAcademico.__tablename__} WHERE dataset_id = :dataset_id ORDER BY id"
        )
        return pd.read_sql(query, con=engine, params={"dataset_id": dataset_id})
