from src.domain.rules.risk_interpretation_rules import obtener_nivel_alerta, obtener_interpretacion


def test_alerta_baja():
    assert obtener_nivel_alerta(0.10) == "Bajo"


def test_alerta_media():
    assert obtener_nivel_alerta(0.50) == "Medio"


def test_alerta_alta():
    assert obtener_nivel_alerta(0.85) == "Alto"


def test_interpretacion_contiene_porcentaje():
    interpretacion = obtener_interpretacion(0.85, "Alto")
    assert "85.00%" in interpretacion
