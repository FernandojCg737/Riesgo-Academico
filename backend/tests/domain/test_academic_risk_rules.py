from src.domain.rules.academic_risk_rules import calcular_riesgo_academico


def test_nota_menor_a_umbral_es_riesgo():
    assert calcular_riesgo_academico(50.9) == 1


def test_nota_igual_al_umbral_no_es_riesgo():
    assert calcular_riesgo_academico(51) == 0


def test_nota_mayor_al_umbral_no_es_riesgo():
    assert calcular_riesgo_academico(75) == 0


def test_nota_cero_es_riesgo():
    assert calcular_riesgo_academico(0) == 1
