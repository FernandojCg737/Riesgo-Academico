from src.domain.constants import UMBRAL_APROBACION

def calcular_riesgo_academico(nota_final: float) -> int:
    """
    Regla de negocio para determinar si un estudiante está en riesgo.
    riesgo_academico = 1 si nota_final < 51, de lo contrario 0.
    """
    return 1 if nota_final < UMBRAL_APROBACION else 0
