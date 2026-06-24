"use client";

import { Plot } from "@/components/charts/plot";
import type { MatrizCorrelacion } from "@/lib/types";

export function CorrelationHeatmapChart({ data }: { data: MatrizCorrelacion }) {
  // Margen lateral fijo (para las etiquetas de variables) + ancho mínimo por
  // celda, así en mobile el heatmap se ve completo con scroll horizontal en
  // vez de comprimirse hasta que las etiquetas se superpongan.
  const minWidth = Math.max(data.variables.length * 60 + 120, 360);

  return (
    <div className="overflow-x-auto">
      <div style={{ minWidth }}>
        <Plot
          data={[
            {
              z: data.matriz,
              x: data.variables,
              y: data.variables,
              type: "heatmap",
              colorscale: "RdBu",
              zmin: -1,
              zmax: 1,
              texttemplate: "%{z}",
              textfont: { size: 10 },
            },
          ]}
          layout={{
            autosize: true,
            margin: { t: 20, l: 120, r: 20, b: 120 },
          }}
          useResizeHandler
          style={{ width: "100%", height: "420px" }}
          config={{ displayModeBar: false }}
        />
      </div>
    </div>
  );
}
