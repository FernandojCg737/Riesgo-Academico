from src.infrastructure.repositories.survey_repository import SurveyRepository

class PrepareSurveyDataset:
    def __init__(self, repository: SurveyRepository = None):
        self.repository = repository or SurveyRepository()

    def ejecutar(self) -> None:
        print("Ejecutando caso de uso: Preparar Dataset de Encuesta...")

        df = self.repository.cargar_raw()

        if "materias_reprobadas_num" in df.columns:
            median_reprobadas = df["materias_reprobadas_num"].median()
            df["materias_reprobadas_num"] = df["materias_reprobadas_num"].fillna(median_reprobadas)

        df["semestre"] = df["semestre_num"]
        df["promedio_actual"] = df["promedio_actual_estimado"]
        df["materias_reprobadas"] = df["materias_reprobadas_num"].astype(int)
        df["horas_estudio_semana"] = df["horas_estudio_semana_num"]
        df["asistencia"] = df["asistencia_ordinal"]
        df["frecuencia_uso_ia"] = df["frecuencia_uso_ia_ordinal"]
        df["dependencia_ia"] = df["dependencia_ia_ordinal"]
        df["motivacion"] = df["motivacion_ordinal"]

        df["frecuencia_uso_ia_desc"] = df["frecuencia_uso_ia_ordinal"].map({
            0: "Nunca", 1: "Raramente", 2: "A veces", 3: "Frecuentemente", 4: "Diariamente"
        })
        df["dependencia_ia_desc"] = df["dependencia_ia_ordinal"].map({
            0: "Ninguna", 1: "Baja", 2: "Media", 3: "Alta"
        })
        df["motivacion_desc"] = df["motivacion_ordinal"].map({
            1: "Muy Baja", 2: "Baja", 3: "Media", 4: "Alta", 5: "Muy Alta"
        })
        df["asistencia_desc"] = df["asistencia_ordinal"].map({
            1: "Muy Baja (<50%)", 2: "Baja (50-70%)", 3: "Media (70-85%)", 4: "Alta (>85%)"
        })

        def categorizar_perfil(row):
            frec = int(row["frecuencia_uso_ia"])
            dep = int(row["dependencia_ia"])
            if frec <= 1:
                return "Uso Bajo"
            elif frec == 2:
                if dep <= 1:
                    return "Uso Moderado Autónomo"
                else:
                    return "Uso Moderado Dependiente"
            else:
                if dep <= 1:
                    return "Uso Alto Autónomo"
                else:
                    return "Uso Alto Dependiente"

        df["perfil_uso_ia"] = df.apply(categorizar_perfil, axis=1)

        self.repository.persistir_registros(df)
        print("Procesamiento de encuesta completado de forma limpia.")
