"use client";

import { PageHeader } from "@/components/layout/page-header";
import { DatasetUploadForm } from "@/components/forms/dataset-upload-form";

export default function CargarDatasetPage() {
  return (
    <div>
      <PageHeader
        title="Cargar Dataset"
        description="Subí un dataset académico nuevo (otra gestión o universidad) para analizarlo por separado, sin afectar los datos existentes."
      />
      <DatasetUploadForm />
    </div>
  );
}
