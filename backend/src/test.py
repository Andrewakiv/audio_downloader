import asyncio
import logging
import sys
import os

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

import tasks
from common.settings import config


RUN_MODE = os.getenv("RUN_MODE")

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def yt_link_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    # # Send a copy of the received message
    # document = FSInputFile("./data/The_Drums-Money_sped_up.mp3")
    # # await bot.send_document(chat_id, document=document, caption="Here is your document!")
    # await message.reply_audio(document)
    tasks.process_audio.delay(4, 4, message.text)
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
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__" and RUN_MODE == "poller":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
