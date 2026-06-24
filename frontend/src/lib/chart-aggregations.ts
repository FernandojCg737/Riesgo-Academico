import type { RegistroAcademico, RiesgoPorCategoria } from "@/lib/types";

function porcentajeRiesgo(registros: RegistroAcademico[]): number {
  if (registros.length === 0) return 0;
  const enRiesgo = registros.filter((r) => r.riesgo_academico === 1).length;
  return Math.round((enRiesgo / registros.length) * 10000) / 100;
}

export function riesgoPorCarrera(registros: RegistroAcademico[]): RiesgoPorCategoria[] {
  const grupos = new Map<string, RegistroAcademico[]>();
  for (const r of registros) {
    grupos.set(r.carrera_alumno, [...(grupos.get(r.carrera_alumno) ?? []), r]);
  }
  return [...grupos.entries()]
    .map(([carrera_alumno, items]) => ({
      carrera_alumno,
      porcentaje_riesgo: porcentajeRiesgo(items),
      n_registros: items.length,
    }))
    .sort((a, b) => b.porcentaje_riesgo - a.porcentaje_riesgo);
}

export function riesgoPorNivel(registros: RegistroAcademico[]): RiesgoPorCategoria[] {
  const grupos = new Map<number, RegistroAcademico[]>();
  for (const r of registros) {
    grupos.set(r.nivel_materia, [...(grupos.get(r.nivel_materia) ?? []), r]);
  }
  return [...grupos.entries()]
    .map(([nivel_materia, items]) => ({
      nivel_materia,
      porcentaje_riesgo: porcentajeRiesgo(items),
      n_registros: items.length,
    }))
    .sort((a, b) => (a.nivel_materia as number) - (b.nivel_materia as number));
}

export function top10Materias(registros: RegistroAcademico[], minRegistros = 30): RiesgoPorCategoria[] {
  const grupos = new Map<string, RegistroAcademico[]>();
  for (const r of registros) {
    grupos.set(r.materia, [...(grupos.get(r.materia) ?? []), r]);
  }
  return [...grupos.entries()]
    .filter(([, items]) => items.length >= minRegistros)
    .map(([materia, items]) => ({
      materia,
      porcentaje_riesgo: porcentajeRiesgo(items),
      n_registros: items.length,
    }))
    .sort((a, b) => b.porcentaje_riesgo - a.porcentaje_riesgo)
    .slice(0, 10);
}
