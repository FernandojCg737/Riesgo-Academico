export interface ResumenAcademico {
  total_registros: number;
  estudiantes_unicos: number;
  materias_unicas: number;
  registros_en_riesgo: number;
  tasa_riesgo_porcentaje: number;
}

export interface RegistroAcademico {
  id: number;
  carrera_alumno: string;
  codigo_materia: string;
  materia: string;
  nivel_materia: number;
  repite_materia_binaria: number;
  nota_final: number;
  ppa: number;
  ppac: number;
  riesgo_academico: number;
}

export interface RegistrosAcademicosResponse {
  total: number;
  page: number;
  page_size: number;
  items: RegistroAcademico[];
}

export interface PrediccionRequest {
  carrera_alumno: string;
  codigo_materia: string;
  nivel_materia: number;
  repite_materia_binaria: number;
  ppa: number;
  ppac: number;
  usar_alternativo: boolean;
}

export interface ExplicacionItem {
  variable: string;
  contribucion: number;
  direccion: "aumenta" | "disminuye";
}

export interface PrediccionResponse {
  prediccion: number;
  etiqueta: string;
  probabilidad_riesgo: number;
  alerta: "Bajo" | "Medio" | "Alto";
  interpretacion: string;
  recomendaciones: string[];
  explicacion: ExplicacionItem[];
  modelo_utilizado: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface EstadoProceso {
  status: "idle" | "started" | "running" | "done" | "error";
  error: string | null;
}

export interface MetricaModelo {
  nombre_interno: string;
  nombre_legible: string;
  configuracion: "base" | "alternativo";
  es_modelo_final: boolean;
  accuracy_test: number;
  accuracy_train: number;
  precision_clase_1: number;
  recall_clase_1: number;
  recall_train: number;
  f1_clase_1: number;
  f1_train: number;
  roc_auc_test: number;
  roc_auc_train: number;
  falsos_negativos: number;
  matriz_confusion: number[][];
  cv_recall_mean: number;
  cv_recall_std: number;
}

export interface MejorModelo {
  modelo_seleccionado: string;
  nombre_modelo: string;
  hiperparametros: Record<string, unknown> | null;
  metricas: {
    recall_clase_1: number;
    f1_score_clase_1: number;
    accuracy: number;
    precision_clase_1: number;
  };
}

export interface ImportanciaVariable {
  Variable: string;
  Importancia: number;
}

export interface PuntoBin {
  x0: number;
  x1: number;
  count: number;
}

export interface DistribucionNotas {
  bins: PuntoBin[];
  umbral_aprobacion: number;
}

export interface RiesgoPorCategoria {
  porcentaje_riesgo: number;
  n_registros: number;
  [key: string]: string | number;
}

export interface BoxplotStats {
  riesgo?: number;
  etiqueta?: string;
  frecuencia?: string;
  min: number;
  q1: number;
  mediana: number;
  q3: number;
  max: number;
}

export interface CurvaRoc {
  puntos: { fpr: number; tpr: number }[];
  auc: number;
}

export interface MatrizCorrelacion {
  variables: string[];
  matriz: number[][];
}
