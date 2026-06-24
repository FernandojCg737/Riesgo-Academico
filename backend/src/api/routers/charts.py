from fastapi import APIRouter, HTTPException, Query

from src.application.services.chart_data_service import ChartDataService
from src.infrastructure.repositories.academic_repository import AcademicRepository
from src.infrastructure.repositories.survey_repository import SurveyRepository
from src.infrastructure.repositories.model_repository import ModelRepository
from src.application.services.preprocessing_service import PreprocessingService
from src.infrastructure.config import settings

router = APIRouter(prefix="/api/charts", tags=["charts"])

_servicio = ChartDataService()


def _cargar_academico():
    df = AcademicRepository().cargar_completo_limpio()
    if df.empty:
        raise HTTPException(status_code=404, detail="No hay datos académicos ingeridos todavía.")
    return df


def _cargar_encuesta():
    df = SurveyRepository().cargar_modelo_dataset()
    if df.empty:
        raise HTTPException(status_code=404, detail="No hay respuestas de encuesta ingeridas todavía.")
    return df


@router.get("/academic/distribucion-notas")
def distribucion_notas():
    return _servicio.obtener_distribucion_notas(_cargar_academico())


@router.get("/academic/cantidad-riesgo")
def cantidad_riesgo():
    return _servicio.obtener_cantidad_riesgo(_cargar_academico())


@router.get("/academic/riesgo-por-nivel")
def riesgo_por_nivel():
    return _servicio.obtener_riesgo_por_nivel(_cargar_academico())


@router.get("/academic/riesgo-por-carrera")
def riesgo_por_carrera():
    return _servicio.obtener_riesgo_por_carrera(_cargar_academico())


@router.get("/academic/top10-materias")
def top10_materias(min_registros: int = Query(30, ge=1)):
    return _servicio.obtener_top10_materias_riesgo(_cargar_academico(), min_registros=min_registros)


@router.get("/academic/riesgo-por-repite")
def riesgo_por_repite():
    return _servicio.obtener_riesgo_por_repite(_cargar_academico())


@router.get("/academic/ppa-vs-riesgo")
def ppa_vs_riesgo():
    return _servicio.obtener_ppa_vs_riesgo(_cargar_academico())


@router.get("/academic/ppac-vs-riesgo")
def ppac_vs_riesgo():
    return _servicio.obtener_ppac_vs_riesgo(_cargar_academico())


@router.get("/model/roc-curve")
def roc_curve_modelo_final():
    from sklearn.model_selection import GroupShuffleSplit

    df = AcademicRepository().cargar_modelo_dataset()
    if df.empty:
        raise HTTPException(status_code=404, detail="No hay datos académicos ingeridos todavía.")

    X, y, groups = PreprocessingService().separar_predictores_y_objetivo(df)
    gss = GroupShuffleSplit(n_splits=1, test_size=settings.TEST_SIZE, random_state=settings.RANDOM_STATE)
    _, test_idx = next(gss.split(df, y, groups=groups))
    X_test, y_test = X.iloc[test_idx], y.iloc[test_idx]

    try:
        pipeline = ModelRepository().cargar_modelo_final()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    y_prob = pipeline.predict_proba(X_test)[:, 1]
    return _servicio.obtener_curva_roc(y_test, y_prob)


_SURVEY_CHARTS = {
    "riesgo-por-dependencia-ia": "obtener_riesgo_por_dependencia_ia",
    "riesgo-por-asistencia": "obtener_riesgo_por_asistencia",
    "riesgo-por-motivacion": "obtener_riesgo_por_motivacion",
    "frecuencia-uso-ia": "obtener_frecuencia_uso_ia",
    "distribucion-dependencia": "obtener_distribucion_dependencia",
    "distribucion-motivacion": "obtener_distribucion_motivacion",
    "distribucion-asistencia": "obtener_distribucion_asistencia",
    "riesgo-por-frecuencia-ia": "obtener_riesgo_por_frecuencia_ia",
    "distribucion-promedio": "obtener_distribucion_promedio",
    "reprobadas-vs-riesgo": "obtener_reprobadas_vs_riesgo",
    "matriz-correlacion": "obtener_matriz_correlacion",
    "perfil-uso-ia": "obtener_perfil_uso_ia",
    "ia-vs-horas-estudio": "obtener_ia_vs_horas_estudio",
    "ia-vs-dependencia": "obtener_ia_vs_dependencia",
}


@router.get("/survey/{slug}")
def grafico_encuesta(slug: str):
    nombre_metodo = _SURVEY_CHARTS.get(slug)
    if not nombre_metodo:
        raise HTTPException(status_code=404, detail=f"Gráfico de encuesta desconocido: {slug}")

    df = _cargar_encuesta()
    metodo = getattr(_servicio, nombre_metodo)
    return metodo(df)
