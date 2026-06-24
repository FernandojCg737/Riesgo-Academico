"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { apiClient, ApiError } from "@/lib/api-client";
import type { PrediccionResponse } from "@/lib/types";

const schema = z.object({
  carrera_alumno: z.string().min(1, "Requerido").max(20),
  codigo_materia: z.string().min(1, "Requerido").max(20),
  nivel_materia: z.coerce.number().int().min(1, "Debe ser entre 1 y 9").max(9, "Debe ser entre 1 y 9"),
  repite_materia_binaria: z.enum(["0", "1"]),
  ppa: z.coerce.number().min(0, "Debe ser entre 0 y 100").max(100, "Debe ser entre 0 y 100"),
  ppac: z.coerce.number().min(0, "Debe ser entre 0 y 100").max(100, "Debe ser entre 0 y 100"),
  usar_alternativo: z.enum(["false", "true"]),
});

type FormInput = z.input<typeof schema>;
type FormOutput = z.output<typeof schema>;

const ALERTA_COLOR: Record<string, string> = {
  Bajo: "border-green-500 text-green-700",
  Medio: "border-yellow-500 text-yellow-700",
  Alto: "border-destructive text-destructive",
};

export function PredictionForm() {
  const [resultado, setResultado] = useState<PrediccionResponse | null>(null);
  const [enviando, setEnviando] = useState(false);

  const form = useForm<FormInput, unknown, FormOutput>({
    resolver: zodResolver(schema),
    defaultValues: {
      carrera_alumno: "",
      codigo_materia: "",
      nivel_materia: 1,
      repite_materia_binaria: "0",
      ppa: 50,
      ppac: 50,
      usar_alternativo: "false",
    },
  });

  async function onSubmit(values: FormOutput) {
    setEnviando(true);
    setResultado(null);
    try {
      const respuesta = await apiClient.post<PrediccionResponse>("/api/predict", {
        carrera_alumno: values.carrera_alumno,
        codigo_materia: values.codigo_materia,
        nivel_materia: Number(values.nivel_materia),
        repite_materia_binaria: Number(values.repite_materia_binaria),
        ppa: Number(values.ppa),
        ppac: Number(values.ppac),
        usar_alternativo: values.usar_alternativo === "true",
      });
      setResultado(respuesta);
    } catch (err) {
      const mensaje = err instanceof ApiError ? err.message : "Error de red al consultar la API";
      toast.error("No se pudo calcular la predicción", { description: mensaje });
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Datos del Estudiante</CardTitle>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="carrera_alumno"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Carrera del Alumno</FormLabel>
                    <FormControl>
                      <Input placeholder="Ej. INF" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="codigo_materia"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Código de la Materia</FormLabel>
                    <FormControl>
                      <Input placeholder="Ej. INF110" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="nivel_materia"
                render={({ field: { value, ...field } }) => (
                  <FormItem>
                    <FormLabel>Nivel de la Materia (1-9)</FormLabel>
                    <FormControl>
                      <Input type="number" min={1} max={9} {...field} value={String(value ?? "")} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="ppa"
                render={({ field: { value, ...field } }) => (
                  <FormItem>
                    <FormLabel>PPA (Promedio Ponderado Acumulado)</FormLabel>
                    <FormControl>
                      <Input type="number" min={0} max={100} step="0.1" {...field} value={String(value ?? "")} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="ppac"
                render={({ field: { value, ...field } }) => (
                  <FormItem>
                    <FormLabel>PPAC (Promedio de Avance Académico)</FormLabel>
                    <FormControl>
                      <Input type="number" min={0} max={100} step="0.1" {...field} value={String(value ?? "")} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="repite_materia_binaria"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>¿Repite la Materia?</FormLabel>
                    <FormControl>
                      <RadioGroup onValueChange={field.onChange} value={field.value} className="flex gap-6">
                        <Label className="flex items-center gap-2 font-normal">
                          <RadioGroupItem value="0" /> No (primera cursada)
                        </Label>
                        <Label className="flex items-center gap-2 font-normal">
                          <RadioGroupItem value="1" /> Sí
                        </Label>
                      </RadioGroup>
                    </FormControl>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="usar_alternativo"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Modelo a Utilizar</FormLabel>
                    <FormControl>
                      <RadioGroup onValueChange={field.onChange} value={field.value} className="flex flex-col gap-2">
                        <Label className="flex items-center gap-2 font-normal">
                          <RadioGroupItem value="false" /> Base (con repitencia) — recomendado
                        </Label>
                        <Label className="flex items-center gap-2 font-normal">
                          <RadioGroupItem value="true" /> Alternativo (sin repitencia)
                        </Label>
                      </RadioGroup>
                    </FormControl>
                  </FormItem>
                )}
              />

              <Button type="submit" disabled={enviando} className="w-full">
                {enviando ? "Calculando..." : "Calcular Riesgo Académico"}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Resultado de la Estimación</CardTitle>
        </CardHeader>
        <CardContent>
          {!resultado && (
            <p className="text-sm text-muted-foreground">
              Completa el formulario y presiona &quot;Calcular Riesgo Académico&quot; para ver el resultado.
            </p>
          )}
          {resultado && (
            <div className="space-y-4">
              <Alert className={ALERTA_COLOR[resultado.alerta]}>
                <AlertTitle className="text-lg">{resultado.etiqueta}</AlertTitle>
                <AlertDescription>
                  Probabilidad de riesgo: <strong>{(resultado.probabilidad_riesgo * 100).toFixed(2)}%</strong> — Nivel de
                  alerta: <strong>{resultado.alerta}</strong>
                </AlertDescription>
              </Alert>

              <p className="text-sm">{resultado.interpretacion}</p>

              {resultado.explicacion.length > 0 && (
                <div>
                  <h4 className="font-semibold text-sm mb-2">Por qué (variables más influyentes)</h4>
                  <div className="space-y-2">
                    {resultado.explicacion.map((item) => {
                      const max = Math.max(...resultado.explicacion.map((e) => Math.abs(e.contribucion)));
                      const ancho = max > 0 ? (Math.abs(item.contribucion) / max) * 100 : 0;
                      return (
                        <div key={item.variable} className="text-xs">
                          <div className="flex justify-between mb-1">
                            <span className="font-medium">{item.variable}</span>
                            <span className="text-muted-foreground">
                              {item.direccion === "aumenta" ? "↑ aumenta riesgo" : "↓ disminuye riesgo"}
                            </span>
                          </div>
                          <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
                            <div
                              className={`h-full rounded-full ${item.direccion === "aumenta" ? "bg-destructive" : "bg-emerald-500"}`}
                              style={{ width: `${ancho}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              <div>
                <h4 className="font-semibold text-sm mb-2">Recomendaciones</h4>
                <ul className="space-y-2 list-disc pl-5 text-sm text-muted-foreground">
                  {resultado.recomendaciones.map((rec, i) => (
                    <li key={i}>{rec}</li>
                  ))}
                </ul>
              </div>

              <p className="text-xs text-muted-foreground border-t pt-3">Modelo utilizado: {resultado.modelo_utilizado}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
