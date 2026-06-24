"use client";

import { useEffect, useState } from "react";
import { apiClient, ApiError } from "@/lib/api-client";

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T>(path: string | null, deps: unknown[] = []): UseApiState<T> {
  const [state, setState] = useState<UseApiState<T>>({ data: null, loading: !!path, error: null });

  useEffect(() => {
    if (!path) return;
    let cancelado = false;
    setState({ data: null, loading: true, error: null });

    apiClient
      .get<T>(path)
      .then((data) => {
        if (!cancelado) setState({ data, loading: false, error: null });
      })
      .catch((err) => {
        if (!cancelado) {
          const mensaje = err instanceof ApiError ? err.message : "Error de red al consultar la API";
          setState({ data: null, loading: false, error: mensaje });
        }
      });

    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [path, ...deps]);

  return state;
}
