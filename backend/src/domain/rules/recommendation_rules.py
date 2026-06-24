from typing import List
from src.domain.constants import UMBRAL_APROBACION

def generar_recomendaciones(
    prediccion: int,
    repite_materia_binaria: int,
    ppa: float,
    ppac: float,
    nivel_materia: int
) -> List[str]:
    """
    Genera recomendaciones automáticas basadas en las reglas lógicas del negocio.
    """
    recomendaciones = []

    # 1. Regla de predicción de riesgo
    if prediccion == 1:
        recomendaciones.append(
            "El estudiante presenta riesgo académico en la materia seleccionada. "
            "Se recomienda seguimiento académico preventivo, refuerzo en la materia y revisión de carga académica."
        )
    else:
        recomendaciones.append(
            "El estudiante presenta un riesgo académico bajo en la materia seleccionada. "
            "Se aconseja mantener el ritmo de estudio actual, asistir a clases y participar activamente."
        )

    # 2. Regla de repetición
    if repite_materia_binaria == 1:
        recomendaciones.append(
            "El estudiante está repitiendo la materia, por lo que se recomienda aplicar "
            "acompañamiento y apoyo académico desde el inicio del periodo."
        )

    # 3. Regla de PPA bajo
    if ppa < UMBRAL_APROBACION:
        recomendaciones.append(
            "El PPA es bajo (<51), lo cual indica dificultades acumuladas en el desempeño académico. "
            "Se aconseja tutoría académica y revisión de historial."
        )

    # 4. Regla de PPAC bajo
    if ppac < UMBRAL_APROBACION:
        recomendaciones.append(
            "El PPAC es bajo (<51), por lo que se recomienda revisar el avance académico general del estudiante."
        )

    # 5. Regla de nivel inicial
    if nivel_materia <= 2:
        recomendaciones.append(
            "Al tratarse de una materia de nivel inicial, se recomienda fortalecer bases académicas, "
            "hábitos de estudio y adaptación universitaria."
        )

    # 6. Regla de nivel avanzado
    if nivel_materia >= 7:
        recomendaciones.append(
            "Al tratarse de una materia de nivel avanzado, se recomienda seguimiento específico debido a la "
            "alta complejidad de los temas."
        )

    return recomendaciones
