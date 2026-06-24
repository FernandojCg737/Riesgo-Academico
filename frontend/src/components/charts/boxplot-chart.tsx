"use client";

import { Plot } from "@/components/charts/plot";
import type { BoxplotStats } from "@/lib/types";

interface BoxplotChartProps {
  data: BoxplotStats[];
  labelKey: "etiqueta" | "frecuencia";
  color?: string;
}

export function BoxplotChart({ data, labelKey, color = "#2A9D8F" }: BoxplotChartProps) {
  const minWidth = Math.max(data.length * 80, 320);

  return (
    <div className="overflow-x-auto">
      <div style={{ minWidth }}>
        <Plot
          data={[
            {
              type: "box",
              x: data.map((d) => String(d[labelKey])),
              q1: data.map((d) => d.q1),
              median: data.map((d) => d.mediana),
              q3: data.map((d) => d.q3),
              lowerfence: data.map((d) => d.min),
              upperfence: data.map((d) => d.max),
              marker: { color },
            } as never,
          ]}
          layout={{
            autosize: true,
            margin: { t: 20, l: 50, r: 20, b: 60 },
          }}
          useResizeHandler
          style={{ width: "100%", height: "340px" }}
          config={{ displayModeBar: false }}
        />
      </div>
    </div>
  );
}
