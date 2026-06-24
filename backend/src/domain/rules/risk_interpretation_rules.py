def obtener_nivel_alerta(probabilidad: float) -> str:
    """
    Determina el nivel de alerta según la probabilidad de riesgo.
    - Bajo: probabilidad < 30%
    - Medio: 30% <= probabilidad < 70%
    - Alto: probabilidad >= 70%
    """
    if probabilidad < 0.30:
        return "Bajo"
    elif probabilidad < 0.70:
        return "Medio"
    else:
        return "Alto"

def obtener_interpretacion(probabilidad: float, alerta: str) -> str:
    """
    Retorna una interpretación cualitativa del estado de riesgo del estudiante.
    """
    if alerta == "Bajo":
        return (
            f"El estudiante muestra un comportamiento académico estable. Su probabilidad estimada de "
            f"riesgo es baja ({probabilidad:.2%}), lo cual sugiere condiciones favorables para la aprobación."
        )
    elif alerta == "Medio":
        return (
            f"El estudiante se encuentra en un estado de vulnerabilidad moderado. Su probabilidad estimada "
            f"de riesgo es del {probabilidad:.2%}. Se aconseja seguimiento preventivo para evitar el rezago académico."
        )
    else:
        return (
            f"El estudiante presenta una situación crítica. Su probabilidad estimada de riesgo de reprobación "
            f"es del {probabilidad:.2%}. Se requiere de forma prioritaria la activación de mecanismos "
            f"de acompañamiento académico inmediato."
        )
