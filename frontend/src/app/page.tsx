"use client";

import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useAutoPolling } from "@/hooks/use-polling";
import type { ResumenAcademico } from "@/lib/types";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Database, GraduationCap, TrendingUp, BookText, RefreshCw } from "lucide-react";
import { useDataset } from "@/contexts/dataset-context";

export default function HomePage() {
  const { datasetId } = useDataset();
  const { data: resumen, loading, updatedAt, refetch } = useAutoPolling<ResumenAcademico>(
    `/api/academic/summary?dataset_id=${datasetId}`,
    15000
  );
  const error = !loading && !resumen;

  return (
    <div>
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-2 md:gap-4">
        <PageHeader
          title="Sistema Predictivo de Riesgo Académico Estudiantil"
          description='Proyecto de Ciencia de Datos: "Sistema Inteligente de Detección Temprana de Riesgo Académico Mediante Ciencia de Datos e Inteligencia Artificial en Estudiantes Universitarios"'
        />
        <Button
          variant="ghost"
          size="sm"
          onClick={refetch}
          className="gap-2 text-muted-foreground shrink-0 self-start md:self-auto -mt-2 md:mt-0"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          {updatedAt ? `Actualizado ${updatedAt.toLocaleTimeString("es")}` : "Actualizar"}
        </Button>
      </div>

      {loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
      )}

      {error && !loading && (
        <Alert variant="destructive" className="mb-8">
          <AlertTitle>Sin datos académicos ingeridos</AlertTitle>
          <AlertDescription>
            Aún no se ha ejecutado la ingesta de datos. Llama a <code>POST /api/data/ingest/academic</code> para cargar
            el dataset histórico.
          </AlertDescription>
        </Alert>
      )}

      {resumen && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Registros Totales</CardTitle>
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                <Database className="h-4 w-4 text-primary" />
              </span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{resumen.total_registros.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Estudiantes Únicos</CardTitle>
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                <GraduationCap className="h-4 w-4 text-primary" />
              </span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{resumen.estudiantes_unicos.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Materias Únicas</CardTitle>
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                <BookText className="h-4 w-4 text-primary" />
              </span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{resumen.materias_unicas.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Tasa de Riesgo</CardTitle>
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-destructive/10">
                <TrendingUp className="h-4 w-4 text-destructive" />
              </span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-destructive">{resumen.tasa_riesgo_porcentaje}%</div>
              <p className="text-xs text-muted-foreground mt-1">{resumen.registros_en_riesgo.toLocaleString()} registros en riesgo</p>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[
          { paso: "1", titulo: "Preparación de Datos", desc: "Limpieza y construcción del target riesgo_academico a partir del dataset histórico 2017." },
          { paso: "2", titulo: "Entrenamiento de Modelos", desc: "6 modelos (LR, Árbol de Decisión, Random Forest) en configuración base y alternativa." },
          { paso: "3", titulo: "Evaluación y Selección", desc: "Selección automática del modelo ganador por Recall máximo sobre la clase de riesgo." },
          { paso: "4", titulo: "Predicción Interactiva", desc: "Simulador de estimación individual de riesgo académico con recomendaciones." },
        ].map((item) => (
          <Card key={item.paso}>
            <CardContent className="pt-6 flex gap-4">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground font-semibold">
                {item.paso}
              </div>
              <div>
                <h3 className="font-semibold mb-1">{item.titulo}</h3>
                <p className="text-sm text-muted-foreground">{item.desc}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
