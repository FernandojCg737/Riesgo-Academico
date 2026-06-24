# Sistema Predictivo de Riesgo Académico Estudiantil — Versión Profesional

Reconstrucción del proyecto original (Python + Streamlit) en un stack desacoplado backend/frontend:

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL + scikit-learn
- **Frontend**: Next.js (App Router) + TypeScript + Tailwind CSS + shadcn/ui + Recharts + Plotly.js
- **Infraestructura**: Docker + docker-compose

La lógica de negocio (reglas de riesgo, hiperparámetros, selección de modelo) es una migración literal del proyecto fuente `academic-risk-predictor`, preservando reproducibilidad (mismo `RANDOM_STATE=42`, mismas métricas).

## Requisitos

- Docker Desktop

## Puesta en marcha

1. Copiar variables de entorno (ya incluidas por defecto para desarrollo local):
   ```bash
   cp .env.example .env
   ```

2. Levantar los 3 servicios (PostgreSQL, API, frontend):
   ```bash
   docker compose up --build -d
   ```

3. Ejecutar la ingesta inicial de datos (lee los CSV en `backend/data/raw/` y los carga a PostgreSQL):
   ```bash
   docker compose exec backend python -m data.seed.seed_database
   ```

4. Entrenar los modelos y seleccionar el mejor:
   ```bash
   curl -X POST http://localhost:8000/api/train
   # Espera a que /api/train/status reporte "done", luego:
   curl -X POST http://localhost:8000/api/evaluation/run
   ```

5. Abrir el dashboard: **http://localhost:3000**
   Documentación interactiva de la API: **http://localhost:8000/docs**

## Tests

```bash
docker compose exec backend pytest -v
```

## Estructura

```
backend/    API FastAPI (Clean Architecture: domain/application/infrastructure/api)
frontend/   Dashboard Next.js (8 páginas: inicio, datos académicos, predicción,
            entrenamiento, evaluación, encuesta de IA, reportes, metodología)
```

Ver `backend/README` (carpetas `src/domain`, `src/application`, `src/infrastructure`, `src/api`) para el detalle de capas.
