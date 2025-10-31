import os, requests, uuid

from celery import Celery
from sqlalchemy import select

from common.settings import config
from models.audio import AudioJob
from task_session import TaskFactory
from yt_util import download_audio

app = Celery(
    'tasks',
    backend='db+postgresql://postgres:tgload-pass@tgload-db/tgload',
    broker='amqp://rmquser:rmqpass@tgload-rabbitmq:5672//'
)

@app.task(bind=True, base=TaskFactory, autoretry_for=(Exception,), retry_backoff=10, retry_kwargs={"max_retries": 3})
def process_audio(self: TaskFactory, job_id: str, link: str) -> dict:
    query = select(AudioJob).where(AudioJob.id == uuid.UUID(job_id))
    query_result = self.session.execute(query)
    job = query_result.scalar()
    filepath = download_audio(link)

    job.filepath = filepath
    # self.session.commit()
    return {"job_id": job_id, "filepath": filepath, "link": link}

@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_kwargs={"max_retries": 3})
def upload_audio(self, payload: dict, chat_id: str) -> dict:
    job_id = payload["job_id"]
    filepath = payload["filepath"]

    with open(filepath, "rb") as f:
        resp = requests.post(
            f"https://api.telegram.org/bot{config.bot_token.get_secret_value()}/sendAudio",
                data={"chat_id": chat_id},
                files={"audio": f}, timeout=600
            )

    return {"job_id": job_id}