"use client";

import { Plot } from "@/components/charts/plot";
import type { CurvaRoc } from "@/lib/types";

export function RocCurveChart({ data }: { data: CurvaRoc }) {
  return (
    <Plot
      data={[
        {
          x: data.puntos.map((p) => p.fpr),
          y: data.puntos.map((p) => p.tpr),
          type: "scatter",
          mode: "lines",
          name: `Curva ROC (AUC = ${data.auc.toFixed(4)})`,
          line: { color: "#2A9D8F", width: 2.5 },
        },
        {
          x: [0, 1],
          y: [0, 1],
          type: "scatter",
          mode: "lines",
          name: "Azar (AUC = 0.50)",
          line: { color: "#E76F51", dash: "dash" },
        },
      ]}
      layout={{
        autosize: true,
        margin: { t: 30, l: 50, r: 20, b: 50 },
        xaxis: { title: { text: "Tasa de Falsos Positivos" }, range: [0, 1] },
        yaxis: { title: { text: "Tasa de Verdaderos Positivos (Recall)" }, range: [0, 1] },
        legend: { x: 0.55, y: 0.05 },
      }}
      useResizeHandler
      style={{ width: "100%", height: "360px" }}
      config={{ displayModeBar: false }}
    />
  );
}
