"use client";

import { useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { apiClient, ApiError } from "@/lib/api-client";
import { useProcesoConPolling } from "@/hooks/use-polling";
import type { EstadoProceso } from "@/lib/types";
import { BrainCircuit, LineChart, Loader2 } from "lucide-react";
import { useDataset } from "@/contexts/dataset-context";

function EstadoBadge({ status }: { status: EstadoProceso["status"] }) {
  const variantes: Record<EstadoProceso["status"], string> = {
    idle: "bg-muted text-muted-foreground",
    started: "bg-blue-100 text-blue-700",
    running: "bg-blue-100 text-blue-700",
    done: "bg-green-100 text-green-700",
    error: "bg-red-100 text-red-700",
  };
  return <Badge className={variantes[status]}>{status}</Badge>;
}

export default function EntrenamientoPage() {
  const { datasetId } = useDataset();
  const entrenamiento = useProcesoConPolling(`/api/train/status?dataset_id=${datasetId}`);
  const evaluacion = useProcesoConPolling(`/api/evaluation/status?dataset_id=${datasetId}`);
  const [lanzandoEntrenamiento, setLanzandoEntrenamiento] = useState(false);
  const [lanzandoEvaluacion, setLanzandoEvaluacion] = useState(false);

  async function lanzarEntrenamiento() {
    setLanzandoEntrenamiento(true);
    try {
      await apiClient.post("/api/train", { dataset_id: datasetId });
      entrenamiento.setEstado({ status: "running", error: null });
      entrenamiento.iniciarPolling();
      toast.success("Entrenamiento iniciado en segundo plano.");
    } catch (err) {
      const mensaje = err instanceof ApiError ? err.message : "Error de red";
      toast.error("No se pudo iniciar el entrenamiento", { description: mensaje });
    } finally {
      setLanzandoEntrenamiento(false);
    }
  }

  async function lanzarEvaluacion() {
    setLanzandoEvaluacion(true);
    try {
      await apiClient.post("/api/evaluation/run", { dataset_id: datasetId });
      evaluacion.setEstado({ status: "running", error: null });
      evaluacion.iniciarPolling();
      toast.success("Evaluación y selección del mejor modelo iniciadas.");
    } catch (err) {
      const mensaje = err instanceof ApiError ? err.message : "Error de red";
      toast.error("No se pudo iniciar la evaluación", { description: mensaje });
    } finally {
      setLanzandoEvaluacion(false);
    }
  }

  const entrenamientoEnCurso = entrenamiento.estado.status === "running" || lanzandoEntrenamiento;
  const evaluacionEnCurso = evaluacion.estado.status === "running" || lanzandoEvaluacion;

  return (
    <div>
      <PageHeader
        title="Entrenamiento y Evaluación de Modelos"
        description="Ejecuta el pipeline de Machine Learning: entrena los 6 modelos (LR, Árbol de Decisión, Random Forest) y selecciona automáticamente el mejor por Recall."
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BrainCircuit className="h-5 w-5" /> 1. Entrenar Modelos
            </CardTitle>
            <CardDescription>
              GridSearchCV con GroupShuffleSplit para los modelos base y alternativos (sin repitencia). Puede tardar varios
              minutos.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Estado:</span>
              <EstadoBadge status={entrenamiento.estado.status} />
            </div>
            {entrenamiento.estado.error && <p className="text-sm text-destructive">{entrenamiento.estado.error}</p>}
            <Button onClick={lanzarEntrenamiento} disabled={entrenamientoEnCurso} className="w-full">
              {entrenamientoEnCurso && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Iniciar Entrenamiento
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <LineChart className="h-5 w-5" /> 2. Evaluar y Seleccionar Mejor Modelo
            </CardTitle>
            <CardDescription>
              Calcula métricas de los 6 modelos y selecciona automáticamente el de mayor Recall sobre la clase de riesgo.
              Ejecutar después de entrenar.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Estado:</span>
              <EstadoBadge status={evaluacion.estado.status} />
            </div>
            {evaluacion.estado.error && <p className="text-sm text-destructive">{evaluacion.estado.error}</p>}
            <Button onClick={lanzarEvaluacion} disabled={evaluacionEnCurso} variant="secondary" className="w-full">
              {evaluacionEnCurso && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Iniciar Evaluación
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
