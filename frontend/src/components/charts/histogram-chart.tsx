"use client";

import { Bar, BarChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { PuntoBin } from "@/lib/types";

interface HistogramChartProps {
  bins: PuntoBin[];
  umbral?: number;
  height?: number;
}

interface ChartTooltipProps {
  active?: boolean;
  label?: string;
  payload?: { value: number }[];
}

function ChartTooltip({ active, payload, label }: ChartTooltipProps) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border bg-popover px-3 py-2 text-sm text-popover-foreground shadow-md">
      <p className="font-medium">Nota {label}</p>
      <p className="text-muted-foreground">
        Registros: <span className="font-medium text-foreground">{payload[0].value}</span>
      </p>
    </div>
  );
}

export function HistogramChart({ bins, umbral, height = 320 }: HistogramChartProps) {
  const data = bins.map((b) => ({
    rango: `${b.x0.toFixed(0)}-${b.x1.toFixed(0)}`,
    centro: (b.x0 + b.x1) / 2,
    count: b.count,
  }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="rango" tick={{ fontSize: 11 }} interval={1} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip content={<ChartTooltip />} cursor={{ fill: "var(--muted)" }} />
        <Bar dataKey="count" fill="var(--chart-1)" radius={[3, 3, 0, 0]} />
        {umbral !== undefined && (
          <ReferenceLine x={`${Math.floor(umbral / 5) * 5}-${Math.ceil(umbral / 5) * 5 + 5}`} stroke="var(--chart-4)" strokeDasharray="4 4" />
        )}
      </BarChart>
    </ResponsiveContainer>
  );
}
