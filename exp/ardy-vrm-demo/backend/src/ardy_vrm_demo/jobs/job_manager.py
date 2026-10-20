"""Async Job Manager and WebSocket pub/sub for ARDY generation jobs."""

import asyncio
import uuid
from typing import Dict, Optional, Set
from ..schemas import JobStatusResponse, UnifiedMotionPayload
from ..ardy_runtime.model_engine import ArdyEngine


class JobManager:
    """Manages asynchronous generation jobs, progress tracking, and WebSocket subscriptions."""

    def __init__(self, engine: ArdyEngine):
        self.engine = engine
        self.jobs: Dict[str, JobStatusResponse] = {}
        self.listeners: Dict[str, Set[asyncio.Queue]] = {}
        self.lock = asyncio.Lock()
        self.active_job_count = 0

    def create_job(self, prompt: str, duration_seconds: float, seed: Optional[int] = None) -> str:
        job_id = str(uuid.uuid4())[:8]
        job = JobStatusResponse(
            job_id=job_id,
            status="queued",
            progress=0.0,
            error=None,
            telemetry=None,
            result=None,
        )
        self.jobs[job_id] = job
        self.listeners[job_id] = set()

        # Launch background execution task
        asyncio.create_task(self._execute_job(job_id, prompt, duration_seconds, seed))
        return job_id

    def get_job(self, job_id: str) -> Optional[JobStatusResponse]:
        return self.jobs.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        job = self.jobs.get(job_id)
        if not job:
            return False
        if job.status in ("completed", "failed", "cancelled"):
            return False
        job.status = "cancelled"
        job.error = "Generation cancelled by user request"
        self._notify_listeners(job_id, job)
        return True

    def subscribe(self, job_id: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        if job_id not in self.listeners:
            self.listeners[job_id] = set()
        self.listeners[job_id].add(queue)
        return queue

    def unsubscribe(self, job_id: str, queue: asyncio.Queue) -> None:
        if job_id in self.listeners:
            self.listeners[job_id].discard(queue)
            if not self.listeners[job_id]:
                del self.listeners[job_id]

    def _notify_listeners(self, job_id: str, job: JobStatusResponse) -> None:
        if job_id in self.listeners:
            for q in list(self.listeners[job_id]):
                try:
                    q.put_nowait(job.model_dump())
                except asyncio.QueueFull:
                    pass

    async def _execute_job(self, job_id: str, prompt: str, duration_seconds: float, seed: Optional[int]) -> None:
        async with self.lock:
            job = self.jobs[job_id]
            if job.status == "cancelled":
                return

            self.active_job_count += 1
            try:
                # 1. Loading model
                job.status = "loading_model"
                job.progress = 0.1
                self._notify_listeners(job_id, job)
                await asyncio.sleep(0.01)

                # 2. Generating diffusion pass
                job.status = "generating"
                job.progress = 0.3
                self._notify_listeners(job_id, job)
                await asyncio.sleep(0.01)

                # Execute synchronous PyTorch diffusion in threadpool to avoid blocking event loop
                loop = asyncio.get_running_loop()
                payload = await loop.run_in_executor(
                    None,
                    lambda: self.engine.generate(
                        prompt=prompt,
                        duration_seconds=duration_seconds,
                        seed=seed,
                    ),
                )

                if job.status == "cancelled":
                    return

                # 3. Decoding and retargeting complete
                job.status = "completed"
                job.progress = 1.0
                job.telemetry = payload.telemetry
                job.result = payload
                self._notify_listeners(job_id, job)

            except Exception as e:
                job.status = "failed"
                job.progress = 1.0
                job.error = str(e)
                self._notify_listeners(job_id, job)
            finally:
                self.active_job_count = max(0, self.active_job_count - 1)
