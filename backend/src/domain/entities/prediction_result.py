from dataclasses import dataclass
from typing import List

@dataclass
class PredictionResult:
    prediccion: int
    etiqueta: str
    probabilidad_riesgo: float
    recomendaciones: List[str]
