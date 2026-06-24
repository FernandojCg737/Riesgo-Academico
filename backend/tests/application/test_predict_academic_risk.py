import pytest
import numpy as np

from src.application.use_cases.predict_academic_risk import PredictAcademicRisk


class _PipelineFalso:
    """Simula un pipeline de sklearn ya entrenado, sin necesidad de un .pkl real."""

    def predict(self, X):
        return np.array([1])

    def predict_proba(self, X):
        return np.array([[0.25, 0.75]])


class _ModelRepositoryFalso:
    def cargar_modelo_final(self):
        return _PipelineFalso()

    def cargar_modelo(self, nombre):
        return _PipelineFalso()


def test_prediccion_devuelve_estructura_esperada():
    caso_uso = PredictAcademicRisk(model_repo=_ModelRepositoryFalso())

    resultado = caso_uso.ejecutar(
        carrera_alumno="INF",
        codigo_materia="INF110",
        nivel_materia=1,
        repite_materia_binaria=1,
        ppa=45.0,
        ppac=40.0,
    )

    assert resultado["prediccion"] == 1
    assert resultado["etiqueta"] == "Riesgo académico alto"
    assert resultado["probabilidad_riesgo"] == pytest.approx(0.75)
    assert resultado["alerta"] == "Alto"
    assert len(resultado["recomendaciones"]) >= 1


def test_prediccion_rechaza_ppa_fuera_de_rango():
    caso_uso = PredictAcademicRisk(model_repo=_ModelRepositoryFalso())

    with pytest.raises(ValueError):
        caso_uso.ejecutar(
            carrera_alumno="INF",
            codigo_materia="INF110",
            nivel_materia=1,
            repite_materia_binaria=0,
            ppa=150.0,
            ppac=40.0,
        )
