import { PageHeader } from "@/components/layout/page-header";
import { PredictionForm } from "@/components/forms/prediction-form";

export default function PrediccionPage() {
  return (
    <div>
      <PageHeader
        title="Simulador de Predicción de Riesgo Académico"
        description="Estimación orientativa basada en el modelo Decision Tree entrenado con datos históricos 2017. No reemplaza el juicio académico docente."
      />
      <PredictionForm />
    </div>
  );
}
