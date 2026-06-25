"use client";

import { useMemo, useState } from "react";
import { PageHeader } from "@/components/layout/page-header";
import { ChartCard } from "@/components/charts/chart-card";
import { ChartFilters } from "@/components/charts/chart-filters";
import { HistogramChart } from "@/components/charts/histogram-chart";
import { BarRiskChart } from "@/components/charts/bar-risk-chart";
import { BoxplotChart } from "@/components/charts/boxplot-chart";
import { useApi } from "@/hooks/use-api";
import { riesgoPorCarrera, riesgoPorNivel, top10Materias } from "@/lib/chart-aggregations";
import type { BoxplotStats, DistribucionNotas, RegistrosAcademicosResponse, RiesgoPorCategoria } from "@/lib/types";
import { useDataset } from "@/contexts/dataset-context";

export default function DatosAcademicosPage() {
  const { datasetId } = useDataset();
  const [carrera, setCarrera] = useState("todas");
  const [nivel, setNivel] = useState("todos");

  const { data: opcionesCarrera } = useApi<RiesgoPorCategoria[]>(
    `/api/charts/academic/riesgo-por-carrera?dataset_id=${datasetId}`,
    [datasetId]
  );
  const { data: opcionesNivel } = useApi<RiesgoPorCategoria[]>(
    `/api/charts/academic/riesgo-por-nivel?dataset_id=${datasetId}`,
    [datasetId]
  );

  const carreras = useMemo(() => (opcionesCarrera ?? []).map((d) => String(d.carrera_alumno)), [opcionesCarrera]);
  const niveles = useMemo(
    () => (opcionesNivel ?? []).map((d) => Number(d.nivel_materia)).sort((a, b) => a - b),
    [opcionesNivel]
  );

  const hayFiltro = carrera !== "todas" || nivel !== "todos";
  const recordsPath = useMemo(() => {
    const params = new URLSearchParams({ page_size: "10000", dataset_id: String(datasetId) });
    if (carrera !== "todas") params.set("carrera_alumno", carrera);
    if (nivel !== "todos") params.set("nivel_materia", nivel);
    return `/api/academic/records?${params.toString()}`;
  }, [carrera, nivel, datasetId]);

  return (
    <div>
      <PageHeader
        title="Datos Académicos 2017"
        description="Análisis exploratorio del dataset histórico de registros estudiante-materia."
      />

      <ChartFilters
        carreras={carreras}
        niveles={niveles}
        carrera={carrera}
        nivel={nivel}
        onCarreraChange={setCarrera}
        onNivelChange={setNivel}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard<DistribucionNotas> title="Distribución de la Nota Final" path={`/api/charts/academic/distribucion-notas?dataset_id=${datasetId}`}>
          {(data) => <HistogramChart bins={data.bins} umbral={data.umbral_aprobacion} />}
        </ChartCard>

        <ChartCard<RiesgoPorCategoria[]> title="Cantidad por Estado de Riesgo" path={`/api/charts/academic/cantidad-riesgo?dataset_id=${datasetId}`}>
          {(data) => <BarRiskChart data={data} xKey="etiqueta" yKey="cantidad" yLabel="Cantidad" />}
        </ChartCard>

        {!hayFiltro ? (
          <ChartCard<RiesgoPorCategoria[]> key="nivel-agg" title="Riesgo por Nivel de Materia" path={`/api/charts/academic/riesgo-por-nivel?dataset_id=${datasetId}`}>
            {(data) => <BarRiskChart data={data} xKey="nivel_materia" yKey="porcentaje_riesgo" yLabel="% en Riesgo" />}
          </ChartCard>
        ) : (
          <ChartCard<RegistrosAcademicosResponse> key="nivel-filtrado" title="Riesgo por Nivel de Materia (filtrado)" path={recordsPath}>
            {(data) => <BarRiskChart data={riesgoPorNivel(data.items)} xKey="nivel_materia" yKey="porcentaje_riesgo" yLabel="% en Riesgo" />}
          </ChartCard>
        )}

        {!hayFiltro ? (
          <ChartCard<RiesgoPorCategoria[]> key="carrera-agg" title="Riesgo por Carrera" path={`/api/charts/academic/riesgo-por-carrera?dataset_id=${datasetId}`}>
            {(data) => <BarRiskChart data={data} xKey="carrera_alumno" yKey="porcentaje_riesgo" yLabel="% en Riesgo" color="var(--chart-3)" />}
          </ChartCard>
        ) : (
          <ChartCard<RegistrosAcademicosResponse> key="carrera-filtrado" title="Riesgo por Carrera (filtrado)" path={recordsPath}>
            {(data) => <BarRiskChart data={riesgoPorCarrera(data.items)} xKey="carrera_alumno" yKey="porcentaje_riesgo" yLabel="% en Riesgo" color="var(--chart-3)" />}
          </ChartCard>
        )}

        {!hayFiltro ? (
          <ChartCard<RiesgoPorCategoria[]> key="top10-agg" title="Top 10 Materias con Mayor Riesgo" path={`/api/charts/academic/top10-materias?dataset_id=${datasetId}`}>
            {(data) => <BarRiskChart data={data} xKey="materia" yKey="porcentaje_riesgo" yLabel="% en Riesgo" color="var(--chart-4)" />}
          </ChartCard>
        ) : (
          <ChartCard<RegistrosAcademicosResponse> key="top10-filtrado" title="Top 10 Materias con Mayor Riesgo (filtrado)" path={recordsPath}>
            {(data) => <BarRiskChart data={top10Materias(data.items)} xKey="materia" yKey="porcentaje_riesgo" yLabel="% en Riesgo" color="var(--chart-4)" />}
          </ChartCard>
        )}

        <ChartCard<RiesgoPorCategoria[]> title="Riesgo según Condición de Repetición" path={`/api/charts/academic/riesgo-por-repite?dataset_id=${datasetId}`}>
          {(data) => <BarRiskChart data={data} xKey="etiqueta" yKey="porcentaje_riesgo" yLabel="% en Riesgo" />}
        </ChartCard>

        <ChartCard<BoxplotStats[]> title="PPA según Riesgo" path={`/api/charts/academic/ppa-vs-riesgo?dataset_id=${datasetId}`}>
          {(data) => <BoxplotChart data={data} labelKey="etiqueta" />}
        </ChartCard>

        <ChartCard<BoxplotStats[]> title="PPAC según Riesgo" path={`/api/charts/academic/ppac-vs-riesgo?dataset_id=${datasetId}`}>
          {(data) => <BoxplotChart data={data} labelKey="etiqueta" color="var(--chart-3)" />}
        </ChartCard>
      </div>
    </div>
  );
}
