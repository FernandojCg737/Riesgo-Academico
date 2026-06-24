"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

interface ChartFiltersProps {
  carreras: string[];
  niveles: number[];
  carrera: string;
  nivel: string;
  onCarreraChange: (value: string) => void;
  onNivelChange: (value: string) => void;
}

export function ChartFilters({ carreras, niveles, carrera, nivel, onCarreraChange, onNivelChange }: ChartFiltersProps) {
  const hayFiltro = carrera !== "todas" || nivel !== "todos";

  return (
    <div className="flex flex-wrap items-center gap-3 mb-4 animate-in fade-in duration-500">
      <Select value={carrera} onValueChange={(value) => value && onCarreraChange(value)}>
        <SelectTrigger className="w-40">
          <SelectValue placeholder="Carrera" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="todas">Todas las carreras</SelectItem>
          {carreras.map((c) => (
            <SelectItem key={c} value={c}>{c}</SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={nivel} onValueChange={(value) => value && onNivelChange(value)}>
        <SelectTrigger className="w-40">
          <SelectValue placeholder="Nivel" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="todos">Todos los niveles</SelectItem>
          {niveles.map((n) => (
            <SelectItem key={n} value={String(n)}>Nivel {n}</SelectItem>
          ))}
        </SelectContent>
      </Select>

      {hayFiltro && (
        <Badge variant="secondary" className="animate-in fade-in">
          Filtro activo
        </Badge>
      )}
    </div>
  );
}
