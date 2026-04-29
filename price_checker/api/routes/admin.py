from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from price_checker.api.deps import get_db, require_admin
from price_checker.schemas.sync_schema import (
    SyncStatusResponse,
    SyncTriggerResponse,
    SyncListResponse,
)
from price_checker.domain.models.cache_status import CacheStatus
from price_checker.domain.models.usuario import Usuario
from price_checker.application.etl.pipeline import run_etl, EtlResult
from price_checker.infrastructure.db.session import SqliteSession
from price_checker.core.error_handler import sanitizar_erro, logar_erro_interno

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

executor = ThreadPoolExecutor(max_workers=1)

JOB_STORE: dict[int, dict] = {}


def _run_etl_background(job_id: int):
    JOB_STORE[job_id]["started_at"] = datetime.now(timezone.utc)
    JOB_STORE[job_id]["status"] = "em_progresso"
    logger.info("Sync job %s iniciado em background", job_id)

    try:
        result: EtlResult = run_etl()

        JOB_STORE[job_id]["status"] = "sucesso"
        JOB_STORE[job_id]["finished_at"] = datetime.now(timezone.utc)
        JOB_STORE[job_id]["produtos_count"] = result.produtos_count
        JOB_STORE[job_id]["codigos_count"] = result.codigos_count

        logger.info(
            "Sync job %s concluído | produtos=%s codigos=%s",
            job_id, result.produtos_count, result.codigos_count
        )

    except Exception as e:
        logar_erro_interno(f"Sync job {job_id} falhou", e)
        JOB_STORE[job_id]["status"] = "erro"
        JOB_STORE[job_id]["finished_at"] = datetime.now(timezone.utc)
        JOB_STORE[job_id]["error_message"] = sanitizar_erro(e)


@router.post("/sync", response_model=SyncTriggerResponse)
def trigger_sync(
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin)
):
    cache_status = CacheStatus(
        last_updated=datetime.now(timezone.utc),
        status="em_progresso"
    )
    db.add(cache_status)
    db.commit()
    db.refresh(cache_status)

    job_id = cache_status.id

    JOB_STORE[job_id] = {
        "job_id": job_id,
        "started_at": datetime.now(timezone.utc),
        "finished_at": None,
        "status": "em_progresso",
        "produtos_count": None,
        "codigos_count": None,
        "error_message": None,
    }

    executor.submit(_run_etl_background, job_id)

    logger.info("Sync triggered | job_id=%s by admin=%s", job_id, _admin.username)

    return SyncTriggerResponse(
        job_id=job_id,
        status="started",
        message="Sync iniciado em background"
    )


@router.get("/sync/{job_id}", response_model=SyncStatusResponse)
def get_sync_status(
    job_id: int,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin)
):
    stmt = select(CacheStatus).where(CacheStatus.id == job_id)
    result = db.execute(stmt).scalars().first()

    if not result:
        raise HTTPException(status_code=404, detail=f"Job {job_id} não encontrado")

    sync_data = JOB_STORE.get(job_id, {})

    return SyncStatusResponse(
        job_id=result.id,
        started_at=result.last_updated,
        finished_at=sync_data.get("finished_at"),
        status=sync_data.get("status", result.status),
        produtos_count=sync_data.get("produtos_count"),
        codigos_count=sync_data.get("codigos_count"),
        error_message=sync_data.get("error_message") or result.erro
    )


@router.get("/sync", response_model=SyncListResponse)
def list_sync_history(
    limit: int = 10,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin)
):
    stmt = (
        select(CacheStatus)
        .order_by(CacheStatus.id.desc())
        .limit(limit)
    )
    results = db.execute(stmt).scalars().all()

    jobs = []
    for r in results:
        sync_data = JOB_STORE.get(r.id, {})
        jobs.append(SyncStatusResponse(
            job_id=r.id,
            started_at=r.last_updated,
            finished_at=sync_data.get("finished_at"),
            status=sync_data.get("status", r.status),
            produtos_count=sync_data.get("produtos_count"),
            codigos_count=sync_data.get("codigos_count"),
            error_message=sync_data.get("error_message") or r.erro
        ))

    return SyncListResponse(jobs=jobs, total=len(jobs))