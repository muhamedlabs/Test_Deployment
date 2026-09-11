import sys
import io
from pathlib import Path
import time
import asyncio
import platform
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatType
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from BANNED_FILES.config import TELEGRAM_TOKEN, BOT_NAME, BOT_VERSION, BOT_AUTHOR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("telegram_bot")

START_TIME = time.time()


def _uptime_str() -> str:
    uptime_sec = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime_sec, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}г {minutes}хв {seconds}с"


async def cmd_start(message: Message, bot: Bot):
    """Команда /start — статус та статистика."""
    t0 = time.time()
    me = await bot.get_me()
    latency_ms = round((time.time() - t0) * 1000)

    text = (
        f"<b>{BOT_NAME}</b> — статус\n\n"
        f"Затримка відклику: <code>{latency_ms} мс</code>\n"
        f"Аптайм: <code>{_uptime_str()}</code>\n"
        f"Bot ID: <code>{me.id}</code>\n"
        f"Username: @{me.username}\n"
        f"Версія: <code>{BOT_VERSION}</code>\n"
        f"Python: <code>{platform.python_version()}</code>\n"
        f"ОС: <code>{platform.system()} {platform.release()}</code>\n"
        f"Автор: {BOT_AUTHOR}\n"
    )

    await message.answer(text)


async def cmd_chatinfo(message: Message):
    """Команда /chatinfo — інформація про поточний чат."""
    chat = message.chat

    text = (
        f"<b>Інформація про чат</b>\n\n"
        f"ID: <code>{chat.id}</code>\n"
        f"Тип: <code>{chat.type}</code>\n"
        f"Назва: {chat.title or chat.full_name or '—'}\n"
    )

    if chat.type != ChatType.PRIVATE:
        try:
            members_count = await message.bot.get_chat_member_count(chat.id)
            text += f"Учасників: <code>{members_count}</code>\n"
        except Exception:
            pass

    await message.answer(text)


async def cmd_userinfo(message: Message):
    """Команда /userinfo — інформація про користувача, що написав команду."""
    user = message.from_user

    text = (
        f"<b>Інформація про {user.full_name}</b>\n\n"
        f"ID: <code>{user.id}</code>\n"
        f"Username: {'@' + user.username if user.username else '—'}\n"
        f"Бот: {'Так' if user.is_bot else 'Ні'}\n"
        f"Мова клієнта: {user.language_code or '—'}\n"
    )

    await message.answer(text)


async def cmd_avatar(message: Message, bot: Bot):
    """Команда /avatar — показати аватар користувача."""
    user = message.from_user
    photos = await bot.get_user_profile_photos(user.id, limit=1)

    if photos.total_count == 0:
        await message.answer("У вас немає встановленого аватара.")
        return

    file_id = photos.photos[0][-1].file_id
    await message.answer_photo(file_id, caption=f"Аватар {user.full_name}")


async def cmd_help(message: Message):
    text = (
        "<b>Доступні команди</b>\n\n"
        "/start — статус та статистика бота\n"
        "/chatinfo — інформація про поточний чат\n"
        "/userinfo — інформація про вас\n"
        "/avatar — ваш аватар\n"
        "/help — ця довідка\n"
    )
    await message.answer(text)


async def run_telegram():
    bot = Bot(
        token=TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_chatinfo, Command("chatinfo"))
    dp.message.register(cmd_userinfo, Command("userinfo"))
    dp.message.register(cmd_avatar, Command("avatar"))
    dp.message.register(cmd_help, Command("help"))

    me = await bot.get_me()
    print(f"[TELEGRAM] Бот {me.full_name} (@{me.username}) запущений і готовий до роботи")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(run_telegram())
    except (KeyboardInterrupt, SystemExit):
        print("[TELEGRAM] Бот зупинений.")