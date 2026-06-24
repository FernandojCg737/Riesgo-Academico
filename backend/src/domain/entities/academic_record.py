from dataclasses import dataclass
from typing import Optional

@dataclass
class AcademicRecord:
    id_estudiante: str
    carrera_alumno: str
    codigo_materia: str
    materia: str
    nivel_materia: int
    repite_materia: int
    nota_final: float
    ppa: float
    ppac: float
    fecha_inscripcion: str
    riesgo_academico: Optional[int] = None
