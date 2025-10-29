import time

from celery import Celery
from yt_util import download_audio

app = Celery(
    'tasks',
    backend='db+postgresql://postgres:tgload-pass@tgload-db/tgload',
    broker='amqp://rmquser:rmqpass@tgload-rabbitmq:5672//'
)

@app.task
def process_audio(chat_id: int, job_id: int, link: str):
    download_audio(link)
    notify.delay('qweqwewqe')

@app.task
def notify(word):
    print('word')
    return word
