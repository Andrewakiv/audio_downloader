import asyncio
import logging
import sys
import os
import uuid

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from celery import chain
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

import tasks
from common.settings import config
from middlewares.session import DbSessionMiddleware
from models.audio import AudioJob, JobStatus

RUN_MODE = os.getenv("RUN_MODE")

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def yt_link_handler(message: Message, session: AsyncSession) -> None:
    job = AudioJob(
        chat_id=str(message.chat.id),
        user_id=str(message.from_user.id),
        link=message.text
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    ch = chain(
        tasks.process_audio.s(str(job.id), message.text),
        tasks.upload_audio.s(chat_id=str(message.chat.id)),
    )
    async_res = ch.apply_async()

    # query = select(AudioJob).where(AudioJob.celery_task_id == uuid.UUID(str(job.id)))
    # query_result = await session.execute(query)
    # job = query_result.scalar()
    # job.celery_task_id = async_res.id
    # await session.commit()
    # tasks.process_audio.delay('2', message.text)
    await message.answer("✅ Processing your audio...")
    # try:
        # Send a copy of the received message
        # document  = FSInputFile("IVOXYGEN-acid_blue.mp3")
        # await bot.send_document(chat_id, document=document, caption="Here is your document!")
        # await message.reply_document(document)
        # tasks.process_audio.delay(4, 4, message)
    # except Exception:
    #     # But not all the types is supported to be copied so need to handle it
    #     await message.answer("something went wrong with downloading")


async def main() -> None:
    engine = create_async_engine(url=config.db_url, echo=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__" and RUN_MODE == "poller":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
