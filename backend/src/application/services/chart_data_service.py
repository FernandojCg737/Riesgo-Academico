import numpy as np
import pandas as pd

from src.infrastructure.config import settings


def _boxplot_stats(serie: pd.Series) -> dict:
    q1, mediana, q3 = np.percentile(serie, [25, 50, 75])
    iqr = q3 - q1
    bigote_inferior = serie[serie >= q1 - 1.5 * iqr].min()
    bigote_superior = serie[serie <= q3 + 1.5 * iqr].max()
    return {
        "min": float(bigote_inferior),
        "q1": float(q1),
        "mediana": float(mediana),
        "q3": float(q3),
        "max": float(bigote_superior),
    }


class ChartDataService:
    """
    Equivalente a ChartService del proyecto original, pero cada método retorna
    estructuras JSON-serializables (dict/list) en vez de guardar imágenes PNG,
    para que el frontend las renderice con gráficos interactivos (Recharts/Plotly).
    """

    # ================= GRÁFICOS ACADÉMICOS =================

    def obtener_distribucion_notas(self, df: pd.DataFrame) -> dict:
        counts, bin_edges = np.histogram(df["nota_final"], bins=20)
        return {
            "bins": [
                {"x0": float(bin_edges[i]), "x1": float(bin_edges[i + 1]), "count": int(counts[i])}
                for i in range(len(counts))
            ],
            "umbral_aprobacion": settings.UMBRAL_APROBACION,
        }

    def obtener_cantidad_riesgo(self, df: pd.DataFrame) -> list:
        total = len(df)
        conteo = df[settings.TARGET].value_counts().sort_index()
        etiquetas = {0: "Sin Riesgo (Nota >= 51)", 1: "En Riesgo (Nota < 51)"}
        return [
            {
                "riesgo": int(riesgo),
                "etiqueta": etiquetas[riesgo],
                "cantidad": int(cantidad),
                "porcentaje": round((cantidad / total) * 100, 2),
            }
            for riesgo, cantidad in conteo.items()
        ]

    def obtener_riesgo_por_nivel(self, df: pd.DataFrame) -> list:
        counts = df["nivel_materia"].value_counts()
        riesgo = df.groupby("nivel_materia")[settings.TARGET].mean() * 100
        return [
            {"nivel_materia": int(nivel), "porcentaje_riesgo": round(float(riesgo[nivel]), 2), "n_registros": int(counts[nivel])}
            for nivel in sorted(riesgo.index)
        ]

    def obtener_riesgo_por_carrera(self, df: pd.DataFrame) -> list:
        counts = df["carrera_alumno"].value_counts()
        riesgo = (df.groupby("carrera_alumno")[settings.TARGET].mean() * 100).sort_values(ascending=False)
        return [
            {"carrera_alumno": carrera, "porcentaje_riesgo": round(float(valor), 2), "n_registros": int(counts[carrera])}
            for carrera, valor in riesgo.items()
        ]

    def obtener_top10_materias_riesgo(self, df: pd.DataFrame, min_registros: int = 30) -> list:
        counts = df["materia"].value_counts()
        materias_validas = counts[counts >= min_registros].index
        df_filtrado = df[df["materia"].isin(materias_validas)]
        riesgo = (df_filtrado.groupby("materia")[settings.TARGET].mean() * 100).sort_values(ascending=False).head(10)
        return [
            {"materia": materia, "porcentaje_riesgo": round(float(valor), 2), "n_registros": int(counts[materia])}
            for materia, valor in riesgo.items()
        ]

    def obtener_riesgo_por_repite(self, df: pd.DataFrame) -> list:
        riesgo = df.groupby("repite_materia_binaria")[settings.TARGET].mean() * 100
        etiquetas = {0: "Primera Cursada (0)", 1: "Repitiendo (1)"}
        return [
            {"repite_materia_binaria": int(valor), "etiqueta": etiquetas[valor], "porcentaje_riesgo": round(float(riesgo[valor]), 2)}
            for valor in sorted(riesgo.index)
        ]

    def obtener_ppa_vs_riesgo(self, df: pd.DataFrame) -> list:
        return [
            {"riesgo": int(riesgo), "etiqueta": "Sin Riesgo" if riesgo == 0 else "En Riesgo", **_boxplot_stats(grupo["ppa"])}
            for riesgo, grupo in df.groupby(settings.TARGET)
        ]

    def obtener_ppac_vs_riesgo(self, df: pd.DataFrame) -> list:
        return [
            {"riesgo": int(riesgo), "etiqueta": "Sin Riesgo" if riesgo == 0 else "En Riesgo", **_boxplot_stats(grupo["ppac"])}
            for riesgo, grupo in df.groupby(settings.TARGET)
        ]

    def obtener_curva_roc(self, y_test, y_prob) -> dict:
        from sklearn.metrics import roc_curve, roc_auc_score

        fpr, tpr, _ = roc_curve(y_test, y_prob)
        auc_score = roc_auc_score(y_test, y_prob)
        return {
            "puntos": [{"fpr": float(f), "tpr": float(t)} for f, t in zip(fpr, tpr)],
            "auc": float(auc_score),
        }

    # ================= GRÁFICOS DE LA ENCUESTA =================

    def obtener_riesgo_por_dependencia_ia(self, df: pd.DataFrame) -> list:
        orden = ["Ninguna", "Baja", "Media", "Alta"]
        riesgo = (df.groupby("dependencia_ia_desc")["riesgo_academico_encuesta_binario"].mean() * 100).reindex(orden).fillna(0)
        counts = df["dependencia_ia_desc"].value_counts()
        return [
            {"dependencia_ia": etiqueta, "porcentaje_riesgo": round(float(riesgo[etiqueta]), 2), "n_registros": int(counts.get(etiqueta, 0))}
            for etiqueta in orden
        ]

    def obtener_riesgo_por_asistencia(self, df: pd.DataFrame) -> list:
        orden = ["Muy Baja (<50%)", "Baja (50-70%)", "Media (70-85%)", "Alta (>85%)"]
        riesgo = (df.groupby("asistencia_desc")["riesgo_academico_encuesta_binario"].mean() * 100).reindex(orden).fillna(0)
        counts = df["asistencia_desc"].value_counts()
        return [
            {"asistencia": etiqueta, "porcentaje_riesgo": round(float(riesgo[etiqueta]), 2), "n_registros": int(counts.get(etiqueta, 0))}
            for etiqueta in orden
        ]

    def obtener_riesgo_por_motivacion(self, df: pd.DataFrame) -> list:
        orden = ["Muy Baja", "Baja", "Media", "Alta", "Muy Alta"]
        riesgo = (df.groupby("motivacion_desc")["riesgo_academico_encuesta_binario"].mean() * 100).reindex(orden).fillna(0)
        counts = df["motivacion_desc"].value_counts()
        return [
            {"motivacion": etiqueta, "porcentaje_riesgo": round(float(riesgo[etiqueta]), 2), "n_registros": int(counts.get(etiqueta, 0))}
            for etiqueta in orden
        ]

    def obtener_frecuencia_uso_ia(self, df: pd.DataFrame) -> list:
        orden = ["Nunca", "Raramente", "A veces", "Frecuentemente", "Diariamente"]
        counts = df["frecuencia_uso_ia_desc"].value_counts().reindex(orden, fill_value=0)
        return [{"frecuencia": etiqueta, "n_registros": int(counts[etiqueta])} for etiqueta in orden]

    def obtener_distribucion_dependencia(self, df: pd.DataFrame) -> list:
        orden = ["Ninguna", "Baja", "Media", "Alta"]
        counts = df["dependencia_ia_desc"].value_counts().reindex(orden, fill_value=0)
        return [{"dependencia_ia": etiqueta, "n_registros": int(counts[etiqueta])} for etiqueta in orden]

    def obtener_distribucion_motivacion(self, df: pd.DataFrame) -> list:
        orden = ["Muy Baja", "Baja", "Media", "Alta", "Muy Alta"]
        counts = df["motivacion_desc"].value_counts().reindex(orden, fill_value=0)
        return [{"motivacion": etiqueta, "n_registros": int(counts[etiqueta])} for etiqueta in orden]

    def obtener_distribucion_asistencia(self, df: pd.DataFrame) -> list:
        orden = ["Muy Baja (<50%)", "Baja (50-70%)", "Media (70-85%)", "Alta (>85%)"]
        counts = df["asistencia_desc"].value_counts().reindex(orden, fill_value=0)
        return [{"asistencia": etiqueta, "n_registros": int(counts[etiqueta])} for etiqueta in orden]

    def obtener_riesgo_por_frecuencia_ia(self, df: pd.DataFrame) -> list:
        orden = ["Nunca", "Raramente", "A veces", "Frecuentemente", "Diariamente"]
        riesgo = (df.groupby("frecuencia_uso_ia_desc")["riesgo_academico_encuesta_binario"].mean() * 100).reindex(orden).fillna(0)
        counts = df["frecuencia_uso_ia_desc"].value_counts()
        return [
            {"frecuencia": etiqueta, "porcentaje_riesgo": round(float(riesgo[etiqueta]), 2), "n_registros": int(counts.get(etiqueta, 0))}
            for etiqueta in orden
        ]

    def obtener_distribucion_promedio(self, df: pd.DataFrame) -> dict:
        counts, bin_edges = np.histogram(df["promedio_actual_estimado"], bins=15)
        return {
            "bins": [
                {"x0": float(bin_edges[i]), "x1": float(bin_edges[i + 1]), "count": int(counts[i])}
                for i in range(len(counts))
            ]
        }

    def obtener_reprobadas_vs_riesgo(self, df: pd.DataFrame) -> list:
        return [
            {
                "riesgo": int(riesgo),
                "etiqueta": "Sin Riesgo" if riesgo == 0 else "En Riesgo",
                **_boxplot_stats(grupo["materias_reprobadas_num"]),
            }
            for riesgo, grupo in df.groupby("riesgo_academico_encuesta_binario")
        ]

    def obtener_matriz_correlacion(self, df: pd.DataFrame) -> dict:
        columnas_corr = [
            "frecuencia_uso_ia_ordinal", "dependencia_ia_ordinal", "asistencia_ordinal",
            "motivacion_ordinal", "horas_estudio_semana_num", "promedio_actual_estimado", "materias_reprobadas_num",
        ]
        etiquetas = {
            "frecuencia_uso_ia_ordinal": "Frecuencia IA",
            "dependencia_ia_ordinal": "Dependencia IA",
            "asistencia_ordinal": "Asistencia",
            "motivacion_ordinal": "Motivación",
            "horas_estudio_semana_num": "Horas Estudio/Sem",
            "promedio_actual_estimado": "PPA Declarado",
            "materias_reprobadas_num": "Materias Reprobadas",
        }
        df_corr = df[columnas_corr].rename(columns=etiquetas)
        matriz = df_corr.corr(method="spearman")
        return {
            "variables": list(matriz.columns),
            "matriz": [[round(float(v), 4) for v in fila] for fila in matriz.values],
        }

    def obtener_perfil_uso_ia(self, df: pd.DataFrame) -> list:
        orden = ["Uso Bajo", "Uso Moderado Autónomo", "Uso Moderado Dependiente", "Uso Alto Autónomo", "Uso Alto Dependiente"]
        counts = df["perfil_uso_ia"].value_counts().reindex(orden, fill_value=0)
        return [{"perfil": etiqueta, "n_registros": int(counts[etiqueta])} for etiqueta in orden]

    def obtener_ia_vs_horas_estudio(self, df: pd.DataFrame) -> list:
        orden = ["Nunca", "Raramente", "A veces", "Frecuentemente", "Diariamente"]
        resultado = []
        for etiqueta in orden:
            grupo = df[df["frecuencia_uso_ia_desc"] == etiqueta]["horas_estudio_semana_num"]
            if len(grupo) == 0:
                continue
            resultado.append({"frecuencia": etiqueta, **_boxplot_stats(grupo)})
        return resultado

    def obtener_ia_vs_dependencia(self, df: pd.DataFrame) -> list:
        orden_frec = ["Nunca", "Raramente", "A veces", "Frecuentemente", "Diariamente"]
        orden_dep = ["Ninguna", "Baja", "Media", "Alta"]
        tabla = pd.crosstab(df["frecuencia_uso_ia_desc"], df["dependencia_ia_desc"], normalize="index") * 100
        tabla = tabla.reindex(orden_frec).reindex(columns=orden_dep, fill_value=0).fillna(0)
        return [
            {"frecuencia": frecuencia, **{dep: round(float(tabla.loc[frecuencia, dep]), 2) for dep in orden_dep}}
            for frecuencia in orden_frec
        ]
