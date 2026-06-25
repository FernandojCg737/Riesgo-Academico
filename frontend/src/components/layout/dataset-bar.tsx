"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Database } from "lucide-react";
import { useDataset } from "@/contexts/dataset-context";

export function DatasetBar() {
  const { datasetId, setDatasetId, datasets, loading } = useDataset();

  if (loading || datasets.length === 0) return null;

  return (
    <div className="flex items-center gap-2 mb-4 text-sm">
      <Database className="h-4 w-4 text-muted-foreground shrink-0" />
      <span className="text-muted-foreground shrink-0">Dataset activo:</span>
      <Select value={String(datasetId)} onValueChange={(value) => value && setDatasetId(Number(value))}>
        <SelectTrigger className="w-auto min-w-48">
          <SelectValue>
            {() => {
              const activo = datasets.find((d) => d.id === datasetId);
              return activo ? `${activo.nombre} (${activo.n_registros.toLocaleString("es")} registros)` : "";
            }}
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {datasets.map((d) => (
            <SelectItem key={d.id} value={String(d.id)}>
              {d.nombre} ({d.n_registros.toLocaleString("es")} registros)
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
