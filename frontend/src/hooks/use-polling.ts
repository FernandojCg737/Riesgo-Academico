"use client";

import { useEffect, useRef, useState } from "react";
import { apiClient } from "@/lib/api-client";
import type { EstadoProceso } from "@/lib/types";

/**
 * Sigue el estado de un proceso asíncrono del backend (entrenamiento, evaluación).
 * Verifica el estado una vez al montar (útil si el proceso ya estaba corriendo) y
 * expone `iniciarPolling` para reiniciar el intervalo manualmente justo después de
 * lanzar el proceso (POST /api/train, POST /api/evaluation/run).
 */
export function useProcesoConPolling(statusPath: string, intervalMs = 2500) {
  const [estado, setEstado] = useState<EstadoProceso>({ status: "idle", error: null });
  const intervalo = useRef<ReturnType<typeof setInterval> | null>(null);

  function detenerPolling() {
    if (intervalo.current) {
      clearInterval(intervalo.current);
      intervalo.current = null;
    }
  }

  function iniciarPolling() {
    detenerPolling();
    intervalo.current = setInterval(async () => {
      try {
        const data = await apiClient.get<EstadoProceso>(statusPath);
        setEstado(data);
        if (data.status === "done" || data.status === "error") detenerPolling();
      } catch {
        detenerPolling();
      }
    }, intervalMs);
  }

  useEffect(() => {
    let cancelado = false;
    apiClient
      .get<EstadoProceso>(statusPath)
      .then((data) => {
        if (cancelado) return;
        setEstado(data);
        if (data.status === "running" || data.status === "started") iniciarPolling();
      })
      .catch(() => {});

    return () => {
      cancelado = true;
      detenerPolling();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusPath]);

  return { estado, setEstado, iniciarPolling };
}

/**
 * Refresca un endpoint periódicamente mientras el componente esté montado.
 * Pensado para KPIs livianos (agregados), no para datasets completos.
 */
export function useAutoPolling<T>(path: string, intervalMs: number) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);

  async function fetchOnce() {
    try {
      const result = await apiClient.get<T>(path);
      setData(result);
      setUpdatedAt(new Date());
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchOnce();
    const id = setInterval(fetchOnce, intervalMs);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [path, intervalMs]);

  return { data, loading, updatedAt, refetch: fetchOnce };
}
