"""Application FastAPI exécutée dans chaque victime Docker."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response

from .health import health_payload
from .metrics import metrics_snapshot, record_error, record_request
from .workload import cpu_workload, light_workload


app = FastAPI(
    title="Carpet Bombing V5.3 Victim Service",
    version="1.0.0",
)


@app.middleware("http")
async def collect_metrics(request: Request, call_next) -> Response:
    """Compte les requêtes et les erreurs sans dépendance externe."""

    record_request(request.url.path)

    try:
        response = await call_next(request)
    except Exception:
        record_error()
        raise

    if response.status_code >= 400:
        record_error()

    return response


@app.get("/health")
def health() -> dict[str, object]:
    """Retourne l'état de santé du service."""

    return health_payload()


@app.get("/workload/light")
def workload_light() -> dict[str, object]:
    """Exécute une charge très légère."""

    return light_workload()


@app.get("/workload/cpu")
def workload_cpu(duration_ms: int = 50) -> dict[str, object]:
    """Exécute une charge CPU contrôlée et bornée."""

    try:
        return cpu_workload(duration_ms)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/metrics")
def metrics() -> dict[str, object]:
    """Retourne les compteurs conservés en mémoire."""

    return metrics_snapshot()
