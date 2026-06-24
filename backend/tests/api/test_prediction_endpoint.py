import src.api.routers.prediction as prediction_router


class _PredictAcademicRiskFalso:
    def __init__(self, model_repo=None):
        pass

    def ejecutar(self, **kwargs):
        return {
            "prediccion": 1,
            "etiqueta": "Riesgo académico alto",
            "probabilidad_riesgo": 0.75,
            "alerta": "Alto",
            "interpretacion": "Situación crítica.",
            "recomendaciones": ["Seguimiento prioritario."],
            "modelo_utilizado": "Decision Tree Classifier - Modelo Base Histórico (Con Repitencia)",
        }


def test_predecir_riesgo_devuelve_200_y_persiste_historial(client, monkeypatch, db_session):
    monkeypatch.setattr(prediction_router, "PredictAcademicRisk", _PredictAcademicRiskFalso)

    payload = {
        "carrera_alumno": "INF",
        "codigo_materia": "INF110",
        "nivel_materia": 1,
        "repite_materia_binaria": 1,
        "ppa": 45.0,
        "ppac": 40.0,
        "usar_alternativo": False,
    }

    response = client.post("/api/predict", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["prediccion"] == 1
    assert body["alerta"] == "Alto"

    historial = client.get("/api/predict/historial").json()
    assert len(historial) == 1
    assert historial[0]["carrera_alumno"] == "INF"


def test_predecir_riesgo_valida_rango_nivel_materia(client):
    payload = {
        "carrera_alumno": "INF",
        "codigo_materia": "INF110",
        "nivel_materia": 15,
        "repite_materia_binaria": 1,
        "ppa": 45.0,
        "ppac": 40.0,
    }

    response = client.post("/api/predict", json=payload)
    assert response.status_code == 422
