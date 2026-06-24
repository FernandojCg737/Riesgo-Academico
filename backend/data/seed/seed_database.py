"""
Script de ingesta inicial: lee los CSV crudos, aplica la limpieza de dominio
(PrepareAcademicDataset / PrepareSurveyDataset) y persiste en PostgreSQL.
Idempotente: cada ejecución reemplaza el contenido de las tablas correspondientes.
Uso: python -m data.seed.seed_database
"""
from src.application.use_cases.prepare_academic_dataset import PrepareAcademicDataset
from src.application.use_cases.prepare_survey_dataset import PrepareSurveyDataset


def main():
    print("Sembrando dataset académico...")
    PrepareAcademicDataset().ejecutar()
    print("Sembrando dataset de encuesta...")
    PrepareSurveyDataset().ejecutar()
    print("Ingesta completa.")


if __name__ == "__main__":
    main()
