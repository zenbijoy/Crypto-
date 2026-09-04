"""
Autonomous Retrain Manager: Distributed Job Locks, Priority Queue, and Cost Budgets.
Phase 31, 32, 33, 34, 35, 36, 37: Training Infrastructure.
"""
from __future__ import annotations
import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

logger = logging.getLogger("CryptoScope.RetrainManager")


class JobPriority(int, Enum):
    CRITICAL_DEGRADED = 1
    MAJOR_DRIFT = 2
    SCHEDULED = 3
    RESEARCH = 4


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class RetrainJob:
    job_id: str
    asset: str
    horizon: str
    model_family: str
    priority: JobPriority
    trigger_reason: str
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: JobStatus = JobStatus.QUEUED
    error_message: Optional[str] = None
    training_duration_sec: float = 0.0
    cpu_hours: float = 0.0
    complexity_penalty_applied: bool = False


class RetrainManager:
    """Orchestrates candidate training jobs with distributed locks, priority queues, and cost budgeting."""

    def __init__(self, cooldown_seconds: float = 3600.0):
        self.cooldown_seconds = cooldown_seconds
        # Active job locks: (asset, horizon, model_family) -> job_id
        self._active_locks: Dict[str, str] = {}
        # Cooldown tracker: key -> last_success_timestamp
        self._cooldowns: Dict[str, float] = {}
        self._job_queue: List[RetrainJob] = []
        self._completed_jobs: List[RetrainJob] = []
        self._lock = asyncio.Lock()

    def _make_key(self, asset: str, horizon: str, model_family: str) -> str:
        return f"{asset.upper().replace('/', '')}:{horizon}:{model_family.lower()}"

    async def submit_job(
        self,
        asset: str,
        horizon: str,
        model_family: str,
        priority: JobPriority,
        trigger_reason: str
    ) -> RetrainJob:
        key = self._make_key(asset, horizon, model_family)
        now = time.time()

        # Cooldown check for scheduled / non-critical jobs
        if priority > JobPriority.CRITICAL_DEGRADED:
            last_run = self._cooldowns.get(key, 0.0)
            if (now - last_run) < self.cooldown_seconds:
                raise ValueError(
                    f"Job rejected: Cooldown active for {key}. "
                    f"Remaining: {int(self.cooldown_seconds - (now - last_run))}s"
                )

        async with self._lock:
            # Check for active execution lock
            if key in self._active_locks:
                raise RuntimeError(f"Concurrent training rejected: Lock already held by job {self._active_locks[key]}")

            job_id = f"job_{int(now*1000)}_{key.replace(':', '_')}"
            job = RetrainJob(
                job_id=job_id,
                asset=asset,
                horizon=horizon,
                model_family=model_family,
                priority=priority,
                trigger_reason=trigger_reason
            )

            # Insert into priority queue
            self._job_queue.append(job)
            self._job_queue.sort(key=lambda j: (j.priority.value, j.created_at))
            logger.info(f"[RetrainManager] Enqueued job {job_id} (Priority: {priority.name}) for {key}")
            return job

    async def acquire_next_job(self) -> Optional[RetrainJob]:
        async with self._lock:
            if not self._job_queue:
                return None

            job = self._job_queue.pop(0)
            key = self._make_key(job.asset, job.horizon, job.model_family)
            self._active_locks[key] = job.job_id
            job.status = JobStatus.RUNNING
            job.started_at = time.time()
            return job

    async def complete_job(
        self,
        job: RetrainJob,
        success: bool,
        error_message: Optional[str] = None,
        duration_sec: float = 0.0
    ):
        async with self._lock:
            key = self._make_key(job.asset, job.horizon, job.model_family)
            if key in self._active_locks:
                del self._active_locks[key]

            job.completed_at = time.time()
            job.training_duration_sec = duration_sec
            job.cpu_hours = duration_sec / 3600.0

            if success:
                job.status = JobStatus.SUCCESS
                self._cooldowns[key] = time.time()
                logger.info(f"[RetrainManager] Job {job.job_id} completed successfully in {duration_sec:.1f}s")
            else:
                job.status = JobStatus.FAILED
                job.error_message = error_message
                logger.error(f"[RetrainManager] Job {job.job_id} FAILED: {error_message}")

            self._completed_jobs.append(job)

    def stats(self) -> Dict[str, Any]:
        return {
            "queued_jobs": len(self._job_queue),
            "active_locks": list(self._active_locks.keys()),
            "completed_count": len(self._completed_jobs),
            "recent_completions": [
                {
                    "job_id": j.job_id,
                    "status": j.status.value,
                    "duration_sec": round(j.training_duration_sec, 2),
                    "error": j.error_message
                }
                for j in self._completed_jobs[-5:]
            ]
        }


retrain_manager = RetrainManager()
