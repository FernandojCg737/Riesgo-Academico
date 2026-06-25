"use client";

import { useState } from "react";
import Link from "next/link";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { apiClient, ApiError } from "@/lib/api-client";
import { useDataset } from "@/contexts/dataset-context";
import type { Dataset } from "@/lib/types";
import { CheckCircle2, Upload } from "lucide-react";

export function DatasetUploadForm() {
  const { setDatasetId, refetchDatasets } = useDataset();
  const [nombre, setNombre] = useState("");
  const [archivo, setArchivo] = useState<File | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultado, setResultado] = useState<Dataset | null>(null);
  const [fileInputKey, setFileInputKey] = useState(0);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!archivo || !nombre.trim()) return;

    setEnviando(true);
    setError(null);
    setResultado(null);

    const formData = new FormData();
    formData.append("nombre", nombre.trim());
    formData.append("archivo", archivo);

    try {
      const dataset = await apiClient.post<Dataset>("/api/datasets/upload", formData);
      setResultado(dataset);
      toast.success(`Dataset "${dataset.nombre}" cargado correctamente`, {
        description: `${dataset.n_registros.toLocaleString("es")} registros procesados.`,
      });
      refetchDatasets();
      setDatasetId(dataset.id);
      setNombre("");
      setArchivo(null);
      setFileInputKey((k) => k + 1);
    } catch (err) {
      const mensaje = err instanceof ApiError ? err.message : "Error de red al subir el dataset";
      setError(mensaje);
      toast.error("No se pudo procesar el dataset", { description: mensaje });
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Subir Dataset</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="nombre">Nombre del dataset</Label>
            <Input
              id="nombre"
              placeholder="ej. Universidad XYZ - Gestión 2025"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="archivo">Archivo (.csv, .xlsx o .xls)</Label>
            <Input
              key={fileInputKey}
              id="archivo"
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={(e) => setArchivo(e.target.files?.[0] ?? null)}
              required
            />
            <p className="text-xs text-muted-foreground">
              Debe tener las columnas: id_estudiante, carrera_alumno, codigo_materia, materia, nivel_materia,
              repite_materia, nota_final, ppa, ppac, fecha_inscripcion.
            </p>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertTitle>No se pudo procesar el archivo</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {resultado && (
            <Alert className="border-primary">
              <CheckCircle2 className="h-4 w-4" />
              <AlertTitle>Dataset cargado</AlertTitle>
              <AlertDescription>
                &quot;{resultado.nombre}&quot; con {resultado.n_registros.toLocaleString("es")} registros. Ya está
                seleccionado como dataset activo —{" "}
                <Link href="/entrenamiento" className="underline">
                  entrenalo ahora
                </Link>
                .
              </AlertDescription>
            </Alert>
          )}

          <Button type="submit" disabled={enviando || !archivo || !nombre.trim()} className="gap-2">
            <Upload className="h-4 w-4" />
            {enviando ? "Procesando..." : "Subir y procesar"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
