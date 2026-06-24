import pandas as pd
from typing import Tuple, Optional
from src.infrastructure.config import settings

class PreprocessingService:
    def separar_predictores_y_objetivo(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, Optional[pd.Series]]:
        """
        Separa un DataFrame en X (variables predictoras), y (variable objetivo) y grupos (id_estudiante).
        """
        X = df[settings.PREDICTORES].copy()
        y = df[settings.TARGET].copy()
        groups = df["id_estudiante"].copy() if "id_estudiante" in df.columns else None

        return X, y, groups
