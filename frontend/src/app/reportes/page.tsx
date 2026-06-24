"use client";

import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useApi } from "@/hooks/use-api";
import type { MejorModelo, MetricaModelo, ResumenAcademico } from "@/lib/types";
import { Download } from "lucide-react";

function descargarCsv(metricas: MetricaModelo[]) {
  const encabezados = [
    "Modelo", "Configuracion", "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "Falsos Negativos",
  ];
  const filas = metricas.map((m) => [
    m.nombre_legible, m.configuracion, m.accuracy_test, m.precision_clase_1, m.recall_clase_1, m.f1_clase_1, m.roc_auc_test, m.falsos_negativos,
  ]);
  const csv = [encabezados, ...filas].map((fila) => fila.join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "metricas_modelos.csv";
  link.click();
  URL.revokeObjectURL(url);
}

export default function ReportesPage() {
  const resumen = useApi<ResumenAcademico>("/api/academic/summary");
  const mejorModelo = useApi<MejorModelo>("/api/evaluation/best-model");
  const metrics = useApi<MetricaModelo[]>("/api/evaluation/metrics");
  const reglas = useApi<{ reglas: string }>("/api/evaluation/decision-tree-rules");

  return (
    <div>
      <PageHeader title="Reportes" description="Resumen ejecutivo, métricas del modelo y reglas de decisión, generados a partir de los datos reales de la base." />

      <Tabs defaultValue="resumen">
        <TabsList>
          <TabsTrigger value="resumen">Resumen Ejecutivo</TabsTrigger>
          <TabsTrigger value="metricas">Métricas</TabsTrigger>
          <TabsTrigger value="reglas">Reglas del Árbol</TabsTrigger>
        </TabsList>

        <TabsContent value="resumen" className="mt-4 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Hallazgos del Dataset Académico</CardTitle>
            </CardHeader>
            <CardContent>
              {resumen.loading && <Skeleton className="h-24 w-full" />}
              {resumen.data && (
                <p className="text-sm leading-relaxed">
                  Se analizaron <strong>{resumen.data.total_registros.toLocaleString()}</strong> registros estudiante-materia
                  correspondientes a <strong>{resumen.data.estudiantes_unicos.toLocaleString()}</strong> estudiantes únicos en{" "}
                  <strong>{resumen.data.materias_unicas}</strong> materias. La tasa de riesgo académico observada es del{" "}
                  <strong>{resumen.data.tasa_riesgo_porcentaje}%</strong> ({resumen.data.registros_en_riesgo.toLocaleString()}{" "}
                  registros en riesgo).
                </p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Modelo Predictivo Seleccionado</CardTitle>
            </CardHeader>
            <CardContent>
              {mejorModelo.loading && <Skeleton className="h-24 w-full" />}
              {mejorModelo.error && (
                <Alert variant="destructive">
                  <AlertDescription>{mejorModelo.error}</AlertDescription>
                </Alert>
              )}
              {mejorModelo.data && (
                <p className="text-sm leading-relaxed">
                  El modelo seleccionado automáticamente es <strong>{mejorModelo.data.nombre_modelo}</strong>, con un Recall
                  de <strong>{(mejorModelo.data.metricas.recall_clase_1 * 100).toFixed(2)}%</strong> sobre la clase de riesgo,
                  Precision de <strong>{(mejorModelo.data.metricas.precision_clase_1 * 100).toFixed(2)}%</strong> y Accuracy
                  general de <strong>{(mejorModelo.data.metricas.accuracy * 100).toFixed(2)}%</strong>. La selección prioriza el
                  Recall para minimizar los falsos negativos (estudiantes en riesgo no detectados).
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="metricas" className="mt-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-base">Métricas Comparativas (6 modelos)</CardTitle>
              {metrics.data && (
                <Button size="sm" variant="outline" onClick={() => descargarCsv(metrics.data!)}>
                  <Download className="h-4 w-4 mr-2" /> Descargar CSV
                </Button>
              )}
            </CardHeader>
            <CardContent>
              {metrics.loading && <Skeleton className="h-48 w-full" />}
              {metrics.data && (
                <pre className="text-xs bg-muted p-4 rounded-md overflow-x-auto">
                  {JSON.stringify(metrics.data, null, 2)}
                </pre>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reglas" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Reglas de Decisión del Árbol Ganador</CardTitle>
            </CardHeader>
            <CardContent>
              {reglas.loading && <Skeleton className="h-64 w-full" />}
              {reglas.error && (
                <Alert variant="destructive">
                  <AlertDescription>{reglas.error}</AlertDescription>
                </Alert>
              )}
              {reglas.data && <pre className="text-xs bg-muted p-4 rounded-md overflow-x-auto whitespace-pre">{reglas.data.reglas}</pre>}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
