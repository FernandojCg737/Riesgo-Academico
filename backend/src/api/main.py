from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.config.settings import settings
from src.api.routers import (
    health,
    data_ingestion,
    academic_data,
    prediction,
    training,
    evaluation,
    charts,
    chatbot,
)

app = FastAPI(title="Academic Risk Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(data_ingestion.router)
app.include_router(academic_data.router)
app.include_router(prediction.router)
app.include_router(training.router)
app.include_router(evaluation.router)
app.include_router(charts.router)
app.include_router(chatbot.router)
