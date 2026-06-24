"use client";

import { Plot } from "@/components/charts/plot";

export function ConfusionMatrixChart({ matriz }: { matriz: number[][] }) {
  const etiquetas = ["Sin Riesgo", "En Riesgo"];
  const matrizInvertida = [...matriz].reverse();

  return (
    <Plot
      data={[
        {
          z: matrizInvertida,
          x: etiquetas,
          y: [...etiquetas].reverse(),
          type: "heatmap",
          colorscale: "Blues",
          showscale: false,
          texttemplate: "%{z}",
          textfont: { size: 16, color: "white" },
        },
      ]}
      layout={{
        autosize: true,
        margin: { t: 20, l: 90, r: 20, b: 60 },
        xaxis: { title: { text: "Clase Predicha" } },
        yaxis: { title: { text: "Clase Real" } },
      }}
      useResizeHandler
      style={{ width: "100%", height: "320px" }}
      config={{ displayModeBar: false }}
    />
  );
}
