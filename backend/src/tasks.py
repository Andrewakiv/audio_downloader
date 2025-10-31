import os, requests, uuid

from celery import Celery
from sqlalchemy import select

from common.settings import config
from models.audio import AudioJob
from task_session import TaskFactory
from yt_util import download_audio

app = Celery(
    'tasks',
    backend=config.celery_backend_url,
    broker=config.broker_url
)

@app.task(bind=True, base=TaskFactory, autoretry_for=(Exception,), retry_backoff=10, retry_kwargs={"max_retries": 3})
def process_audio(self: TaskFactory, job_id: str, link: str) -> dict:
    query = select(AudioJob).where(AudioJob.id == uuid.UUID(job_id))
    query_result = self.session.execute(query)
    job = query_result.scalar()
    audio_meta = download_audio(link)

    job.filepath = audio_meta['filepath']
    return {"job_id": job_id, "audio_meta": audio_meta, "link": link}

@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_kwargs={"max_retries": 3})
def upload_audio(self, payload: dict, chat_id: str) -> dict:
    job_id = payload["job_id"]
    filepath = payload['audio_meta']["filepath"]
    title = payload['audio_meta']['title']
    channel = payload['audio_meta']['channel']

    with open(filepath, "rb") as f:
        resp = requests.post(
            f"https://api.telegram.org/bot{config.bot_token.get_secret_value()}/sendAudio",
                data={
                    "chat_id": chat_id,
                    'title': title,
                    'performer': channel,
                    'caption': '🦦 @teleimggbot'
                },
                files={"audio": f}, timeout=600
            )

    return {"job_id": job_id}