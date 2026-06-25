import pandas as pd
import numpy as np

from src.infrastructure.config import settings
from src.infrastructure.repositories.academic_repository import AcademicRepository
from src.domain.rules import academic_risk_rules

class PrepareAcademicDataset:
    def __init__(self, repository: AcademicRepository = None):
        self.repository = repository or AcademicRepository()

    def ejecutar(self, dataset_id: int, df: pd.DataFrame = None) -> int:
        print(f"Ejecutando caso de uso: Preparar Dataset Académico (dataset_id={dataset_id})...")

        if df is None:
            df = self.repository.cargar_raw()

        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        columnas_esperadas = [
            "id_estudiante", "carrera_alumno", "codigo_materia", "materia",
            "nivel_materia", "repite_materia", "nota_final", "ppa", "ppac", "fecha_inscripcion"
        ]
        columnas_faltantes = [col for col in columnas_esperadas if col not in df.columns]
        if columnas_faltantes:
            raise ValueError(f"Faltan columnas requeridas en el dataset académico raw: {columnas_faltantes}")

        print(f"  Dataset académico raw cargado con {len(df)} registros.")

        df["id_estudiante"] = pd.factorize(df["id_estudiante"])[0] + 1

        df["nota_final"] = pd.to_numeric(df["nota_final"], errors="coerce")
        df["ppa"] = pd.to_numeric(df["ppa"], errors="coerce")
        df["ppac"] = pd.to_numeric(df["ppac"], errors="coerce")

        n_nulos = df[["nota_final", "ppa", "ppac"]].isna().any(axis=1).sum()
        if n_nulos > 0:
            print(f"  Advertencia: Eliminando {n_nulos} registros con notas o promedios nulos/inválidos.")
            df = df.dropna(subset=["nota_final", "ppa", "ppac"])

        df["repite_materia"] = pd.to_numeric(df["repite_materia"], errors="coerce").fillna(0).astype(int)
        df["repite_materia_binaria"] = np.where(df["repite_materia"] > 0, 1, 0)

        df[settings.TARGET] = df["nota_final"].apply(academic_risk_rules.calcular_riesgo_academico)

        print("\n=== VALIDACIÓN DE repite_materia_binaria ===")
        crosstab_abs = pd.crosstab(df["repite_materia_binaria"], df[settings.TARGET], margins=True)
        crosstab_pct = pd.crosstab(df["repite_materia_binaria"], df[settings.TARGET], normalize="index")

        print("Tabla Cruzada Absoluta (margins=True):")
        print(crosstab_abs)
        print("\nTabla Cruzada Porcentual (normalize='index'):")
        print(crosstab_pct)

        print("Confirmación: repite_materia_binaria = 0 representa primera cursada.")
        print("Confirmación: repite_materia_binaria = 1 representa repitente (repite_materia > 0).")
        print("============================================\n")

        n_multiples = (df["repite_materia"] > 1).sum()
        if n_multiples > 0:
            print(f"  Información: Se mapearon {n_multiples} registros con repitencia recurrente (>1) a 1 (Repitente).")

        df["nivel_materia"] = pd.to_numeric(df["nivel_materia"], errors="coerce")
        invalidos_nivel = (df["nivel_materia"] < 1) | (df["nivel_materia"] > 9) | df["nivel_materia"].isna()
        n_invalidos_nivel = invalidos_nivel.sum()
        if n_invalidos_nivel > 0:
            print(f"  Advertencia: Eliminando {n_invalidos_nivel} registros con nivel fuera de rango (1-9).")
            df = df[~invalidos_nivel]
        df["nivel_materia"] = df["nivel_materia"].astype(int)

        self.repository.persistir_registros(df, dataset_id)
        print("Procesamiento académico completado de forma limpia.")
        return len(df)
