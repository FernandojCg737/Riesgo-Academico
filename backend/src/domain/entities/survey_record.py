from dataclasses import dataclass

@dataclass
class SurveyRecord:
    id_encuesta: int
    carrera: str
    semestre_num: int
    promedio_actual_orden: int
    promedio_actual_estimado: float
    materias_reprobadas_num: float
    horas_estudio_semana_num: int
    asistencia_ordinal: int
    frecuencia_uso_ia_ordinal: int
    dependencia_ia_ordinal: int
    motivacion_ordinal: int
    riesgo_academico_encuesta: str
    riesgo_academico_encuesta_binario: int
