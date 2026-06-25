"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useApi } from "@/hooks/use-api";
import type { Dataset } from "@/lib/types";

const STORAGE_KEY = "dataset_activo";

interface DatasetContextValue {
  datasetId: number;
  setDatasetId: (id: number) => void;
  datasets: Dataset[];
  loading: boolean;
  refetchDatasets: () => void;
}

const DatasetContext = createContext<DatasetContextValue | null>(null);

export function DatasetProvider({ children }: { children: React.ReactNode }) {
  const [refreshKey, setRefreshKey] = useState(0);
  const { data: datasets, loading } = useApi<Dataset[]>("/api/datasets", [refreshKey]);
  const [datasetId, setDatasetIdState] = useState<number>(1);

  useEffect(() => {
    const guardado = typeof window !== "undefined" ? window.localStorage.getItem(STORAGE_KEY) : null;
    if (guardado) setDatasetIdState(Number(guardado));
  }, []);

  useEffect(() => {
    if (!datasets || datasets.length === 0) return;
    const existe = datasets.some((d) => d.id === datasetId);
    if (!existe) setDatasetIdState(datasets[0].id);
  }, [datasets, datasetId]);

  function setDatasetId(id: number) {
    setDatasetIdState(id);
    window.localStorage.setItem(STORAGE_KEY, String(id));
  }

  return (
    <DatasetContext.Provider
      value={{
        datasetId,
        setDatasetId,
        datasets: datasets ?? [],
        loading,
        refetchDatasets: () => setRefreshKey((k) => k + 1),
      }}
    >
      {children}
    </DatasetContext.Provider>
  );
}

export function useDataset(): DatasetContextValue {
  const ctx = useContext(DatasetContext);
  if (!ctx) throw new Error("useDataset debe usarse dentro de <DatasetProvider>");
  return ctx;
}
