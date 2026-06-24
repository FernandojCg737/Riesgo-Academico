"use client";

import { PageHeader } from "@/components/layout/page-header";
import { ChartCard } from "@/components/charts/chart-card";
import { BarRiskChart } from "@/components/charts/bar-risk-chart";
import { BoxplotChart } from "@/components/charts/boxplot-chart";
import { HistogramChart } from "@/components/charts/histogram-chart";
import { CorrelationHeatmapChart } from "@/components/charts/correlation-heatmap-chart";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import type { BoxplotStats, DistribucionNotas, MatrizCorrelacion, RiesgoPorCategoria } from "@/lib/types";

export default function EncuestaPage() {
  return (
    <div>
      <PageHeader
        title="Análisis Descriptivo de la Encuesta de IA"
        description="Hábitos de estudio, motivación y uso de Inteligencia Artificial reportados por estudiantes actuales (2025-2026)."
      />

      <Alert className="mb-6">
        <AlertTitle>Aislamiento metodológico</AlertTitle>
        <AlertDescription>
          La encuesta se analiza de forma independiente al dataset histórico 2017. No se utiliza para validar el modelo
          predictivo principal, ya que pertenecen a contextos temporales distintos.
        </AlertDescription>
      </Alert>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard<RiesgoPorCategoria[]> title="Riesgo por Dependencia de IA" path="/api/charts/survey/riesgo-por-dependencia-ia">
          {(data) => <BarRiskChart data={data} xKey="dependencia_ia" yKey="porcentaje_riesgo" yLabel="% en Riesgo" color="#9C6ADE" />}
        </ChartCard>

        <ChartCard<RiesgoPorCategoria[]> title="Riesgo por Asistencia" path="/api/charts/survey/riesgo-por-asistencia">
          {(data) => <BarRiskChart data={data} xKey="asistencia" yKey="porcentaje_riesgo" yLabel="% en Riesgo" />}
        </ChartCard>

        <ChartCard<RiesgoPorCategoria[]> title="Riesgo por Motivación" path="/api/charts/survey/riesgo-por-motivacion">
          {(data) => <BarRiskChart data={data} xKey="motivacion" yKey="porcentaje_riesgo" yLabel="% en Riesgo" color="#2A9D8F" />}
        </ChartCard>

        <ChartCard<RiesgoPorCategoria[]> title="Riesgo por Frecuencia de Uso de IA" path="/api/charts/survey/riesgo-por-frecuencia-ia">
          {(data) => <BarRiskChart data={data} xKey="frecuencia" yKey="porcentaje_riesgo" yLabel="% en Riesgo" color="#E76F51" />}
        </ChartCard>

        <ChartCard<RiesgoPorCategoria[]> title="Frecuencia de Uso de IA" path="/api/charts/survey/frecuencia-uso-ia">
          {(data) => <BarRiskChart data={data} xKey="frecuencia" yKey="n_registros" yLabel="Cantidad" color="#F4A261" />}
        </ChartCard>

        <ChartCard<RiesgoPorCategoria[]> title="Distribución de Dependencia de IA" path="/api/charts/survey/distribucion-dependencia">
          {(data) => <BarRiskChart data={data} xKey="dependencia_ia" yKey="n_registros" yLabel="Cantidad" color="#9C6ADE" />}
        </ChartCard>

        <ChartCard<RiesgoPorCategoria[]> title="Distribución de Motivación" path="/api/charts/survey/distribucion-motivacion">
          {(data) => <BarRiskChart data={data} xKey="motivacion" yKey="n_registros" yLabel="Cantidad" />}
        </ChartCard>

        <ChartCard<RiesgoPorCategoria[]> title="Distribución de Asistencia" path="/api/charts/survey/distribucion-asistencia">
          {(data) => <BarRiskChart data={data} xKey="asistencia" yKey="n_registros" yLabel="Cantidad" />}
        </ChartCard>

        <ChartCard<DistribucionNotas> title="Distribución del PPA Declarado" path="/api/charts/survey/distribucion-promedio">
          {(data) => <HistogramChart bins={data.bins} />}
        </ChartCard>

        <ChartCard<BoxplotStats[]> title="Materias Reprobadas según Riesgo" path="/api/charts/survey/reprobadas-vs-riesgo">
          {(data) => <BoxplotChart data={data} labelKey="etiqueta" color="#E76F51" />}
        </ChartCard>

        <ChartCard<RiesgoPorCategoria[]> title="Perfil de Uso de IA" path="/api/charts/survey/perfil-uso-ia">
          {(data) => <BarRiskChart data={data} xKey="perfil" yKey="n_registros" yLabel="Cantidad" color="#2A9D8F" />}
        </ChartCard>

        <ChartCard<BoxplotStats[]> title="Horas de Estudio según Frecuencia de Uso de IA" path="/api/charts/survey/ia-vs-horas-estudio">
          {(data) => <BoxplotChart data={data} labelKey="frecuencia" color="#F4A261" />}
        </ChartCard>

        <ChartCard<MatrizCorrelacion> title="Matriz de Correlación (Spearman)" path="/api/charts/survey/matriz-correlacion">
          {(data) => <CorrelationHeatmapChart data={data} />}
        </ChartCard>
      </div>
    </div>
  );
}
