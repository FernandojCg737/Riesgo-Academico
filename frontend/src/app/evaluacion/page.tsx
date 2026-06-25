"use client";

import { useEffect, useRef, useState } from "react";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { ConfusionMatrixChart } from "@/components/charts/confusion-matrix-chart";
import { RocCurveChart } from "@/components/charts/roc-curve-chart";
import { BarRiskChart } from "@/components/charts/bar-risk-chart";
import { useApi } from "@/hooks/use-api";
import { useProcesoConPolling } from "@/hooks/use-polling";
import type { CurvaRoc, ImportanciaVariable, MejorModelo, MetricaModelo } from "@/lib/types";
import { Loader2 } from "lucide-react";
import { useDataset } from "@/contexts/dataset-context";

export default function EvaluacionPage() {
  const { datasetId } = useDataset();
  const proceso = useProcesoConPolling(`/api/evaluation/status?dataset_id=${datasetId}`);
  const enCurso = proceso.estado.status === "running" || proceso.estado.status === "started";

  // Solo se refresca cuando el proceso transiciona de "en curso" a "done",
  // nunca en el montaje inicial (evita un doble fetch y un parpadeo de los gráficos).
  const estadoAnterior = useRef(proceso.estado.status);
  const [refreshKey, setRefreshKey] = useState(0);
  useEffect(() => {
    const eraEnCurso = estadoAnterior.current === "running" || estadoAnterior.current === "started";
    if (eraEnCurso && proceso.estado.status === "done") {
      setRefreshKey((k) => k + 1);
    }
    estadoAnterior.current = proceso.estado.status;
  }, [proceso.estado.status]);

  const metrics = useApi<MetricaModelo[]>(`/api/evaluation/metrics?dataset_id=${datasetId}`, [refreshKey, datasetId]);
  const mejorModelo = useApi<MejorModelo>(`/api/evaluation/best-model?dataset_id=${datasetId}`, [refreshKey, datasetId]);
  const importancia = useApi<ImportanciaVariable[]>(
    `/api/evaluation/feature-importance?grouped=true&dataset_id=${datasetId}`,
    [refreshKey, datasetId]
  );
  const roc = useApi<CurvaRoc>(`/api/charts/model/roc-curve?dataset_id=${datasetId}`, [refreshKey, datasetId]);

  const modeloFinal = metrics.data?.find((m) => m.es_modelo_final);

  return (
    <div>
      <PageHeader
        title="Evaluación y Comparación de Modelos"
        description="Métricas de los 6 modelos entrenados (3 algoritmos × 2 configuraciones) y diagnóstico del modelo seleccionado."
      />

      {enCurso && (
        <div className="mb-6 flex items-center gap-2 rounded-lg border bg-muted/50 px-4 py-3 text-sm text-muted-foreground animate-in fade-in">
          <Loader2 className="h-4 w-4 animate-spin" />
          Evaluación en curso — esta página se actualizará automáticamente al finalizar.
        </div>
      )}

      {mejorModelo.data && (
        <Alert className="mb-6 border-primary">
          <AlertTitle>Modelo Ganador: {mejorModelo.data.nombre_modelo}</AlertTitle>
          <AlertDescription>
            Recall: <strong>{(mejorModelo.data.metricas.recall_clase_1 * 100).toFixed(2)}%</strong> — F1-Score:{" "}
            <strong>{mejorModelo.data.metricas.f1_score_clase_1.toFixed(4)}</strong> — Accuracy:{" "}
            <strong>{(mejorModelo.data.metricas.accuracy * 100).toFixed(2)}%</strong>
          </AlertDescription>
        </Alert>
      )}

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Tabla Comparativa de Métricas</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          {metrics.loading && <Skeleton className="h-64 w-full" />}
          {metrics.error && (
            <Alert variant="destructive">
              <AlertDescription>{metrics.error}</AlertDescription>
            </Alert>
          )}
          {metrics.data && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Modelo</TableHead>
                  <TableHead>Config.</TableHead>
                  <TableHead>Accuracy</TableHead>
                  <TableHead>Precision</TableHead>
                  <TableHead>Recall</TableHead>
                  <TableHead>F1-Score</TableHead>
                  <TableHead>ROC-AUC</TableHead>
                  <TableHead>FN</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {metrics.data.map((m) => (
                  <TableRow key={m.nombre_interno} className={m.es_modelo_final ? "bg-primary/5" : undefined}>
                    <TableCell className="font-medium flex items-center gap-2">
                      {m.nombre_legible}
                      {m.es_modelo_final && <Badge>Ganador</Badge>}
                    </TableCell>
                    <TableCell className="capitalize text-muted-foreground">{m.configuracion}</TableCell>
                    <TableCell>{(m.accuracy_test * 100).toFixed(2)}%</TableCell>
                    <TableCell>{(m.precision_clase_1 * 100).toFixed(2)}%</TableCell>
                    <TableCell>{(m.recall_clase_1 * 100).toFixed(2)}%</TableCell>
                    <TableCell>{m.f1_clase_1.toFixed(4)}</TableCell>
                    <TableCell>{m.roc_auc_test.toFixed(4)}</TableCell>
                    <TableCell>{m.falsos_negativos}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Matriz de Confusión — Modelo Final</CardTitle>
          </CardHeader>
          <CardContent>
            {modeloFinal ? (
              <ConfusionMatrixChart matriz={modeloFinal.matriz_confusion} />
            ) : (
              <Skeleton className="h-[320px] w-full" />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Curva ROC — Modelo Final</CardTitle>
          </CardHeader>
          <CardContent>
            {roc.loading && <Skeleton className="h-[360px] w-full" />}
            {roc.error && (
              <Alert variant="destructive">
                <AlertDescription>{roc.error}</AlertDescription>
              </Alert>
            )}
            {roc.data && <RocCurveChart data={roc.data} />}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Importancia de Variables (Agrupada)</CardTitle>
        </CardHeader>
        <CardContent>
          {importancia.loading && <Skeleton className="h-[320px] w-full" />}
          {importancia.error && (
            <Alert variant="destructive">
              <AlertDescription>{importancia.error}</AlertDescription>
            </Alert>
          )}
          {importancia.data && (
            <BarRiskChart
              data={importancia.data.map((d) => ({ variable: d.Variable, importancia: Number((d.Importancia * 100).toFixed(2)) }))}
              xKey="variable"
              yKey="importancia"
              yLabel="Importancia (%)"
              color="#9C6ADE"
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
