"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface BarRiskChartProps {
  data: Record<string, string | number>[];
  xKey: string;
  yKey: string;
  yLabel?: string;
  color?: string;
  height?: number;
}

interface ChartTooltipProps {
  active?: boolean;
  label?: string;
  yLabel?: string;
  payload?: { value: number; payload: Record<string, string | number> }[];
}

function ChartTooltip({ active, payload, label, yLabel }: ChartTooltipProps) {
  if (!active || !payload?.length) return null;
  const punto = payload[0].payload;
  const valor = payload[0].value;
  const nRegistros = punto.n_registros;

  return (
    <div className="rounded-lg border bg-popover px-3 py-2 text-sm text-popover-foreground shadow-md">
      <p className="font-medium">{label}</p>
      <p className="text-muted-foreground">
        {yLabel ?? "Valor"}: <span className="font-medium text-foreground">{valor}</span>
      </p>
      {typeof nRegistros === "number" && (
        <p className="text-xs text-muted-foreground">{nRegistros.toLocaleString("es")} registros</p>
      )}
    </div>
  );
}

export function BarRiskChart({ data, xKey, yKey, yLabel, color = "var(--chart-1)", height = 320 }: BarRiskChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey={xKey} tick={{ fontSize: 12 }} interval={0} angle={-15} textAnchor="end" height={60} />
        <YAxis tick={{ fontSize: 12 }} label={yLabel ? { value: yLabel, angle: -90, position: "insideLeft", fontSize: 12 } : undefined} />
        <Tooltip content={<ChartTooltip yLabel={yLabel} />} cursor={{ fill: "var(--muted)" }} />
        <Bar dataKey={yKey} fill={color} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
