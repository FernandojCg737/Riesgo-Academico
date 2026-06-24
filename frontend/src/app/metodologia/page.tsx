import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

const ADVERTENCIAS = [
  "Fuga de Información (Data Leakage): nota_final se usa exclusivamente para construir el target riesgo_academico y luego se elimina del conjunto de entrenamiento.",
  "Aislamiento de id_estudiante: se usa únicamente como variable de agrupación en GroupShuffleSplit y GroupKFold, para evitar que registros del mismo alumno aparezcan en entrenamiento y prueba simultáneamente.",
  "Separación de Datasets: el dataset de encuesta de IA y el académico histórico se procesan de forma completamente independiente. No se mezclan en el entrenamiento del modelo principal.",
  "No Causalidad: el modelo identifica asociaciones estadísticas, no relaciones causales directas.",
  "Temporalidad: la encuesta refleja hábitos actuales (2025-2026), mientras que el dataset de rendimiento es histórico (2017).",
  "Carácter del Simulador: el módulo de predicción es un simulador orientativo basado en datos históricos. No reemplaza el juicio académico docente.",
];

export default function MetodologiaPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Metodología del Sistema" description="Fundamentos técnicos y arquitectónicos del proyecto." />

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Metodología de Modelado</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <p>
            Se entrenaron <strong>6 modelos</strong> (Regresión Logística, Árbol de Decisión y Random Forest, en
            configuración base y alternativa sin la variable <code>repite_materia_binaria</code>).
          </p>
          <p>
            La partición de datos usa <strong>GroupShuffleSplit</strong> (80/20) agrupando por{" "}
            <code>id_estudiante</code> para evitar fuga de información entre entrenamiento y prueba. Los árboles y Random
            Forest se ajustan con <strong>GridSearchCV</strong> optimizando <strong>Recall</strong> sobre la clase de
            riesgo, validado con <strong>GroupKFold</strong> (5 splits) para medir estabilidad.
          </p>
          <p>
            El modelo final se selecciona automáticamente ordenando por Recall Test (Riesgo) descendente, y como
            criterio de desempate, F1-Score Test (Riesgo) descendente.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Arquitectura del Sistema</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <p>
            El backend (<strong>FastAPI</strong>) sigue Clean Architecture en 4 capas: <code>domain</code> (reglas de
            negocio puras), <code>application</code> (casos de uso y servicios), <code>infrastructure</code>{" "}
            (repositorios PostgreSQL, persistencia de modelos, pipelines de scikit-learn) y <code>api</code> (routers
            REST).
          </p>
          <p>
            El frontend (<strong>Next.js</strong>) consume la API exclusivamente vía JSON — los gráficos no se
            generan como imágenes estáticas en el servidor, sino que se renderizan de forma interactiva en el
            navegador con Recharts y Plotly.js.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Advertencias Metodológicas</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {ADVERTENCIAS.map((texto, i) => (
            <Alert key={i}>
              <AlertTitle>Advertencia {i + 1}</AlertTitle>
              <AlertDescription>{texto}</AlertDescription>
            </Alert>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
