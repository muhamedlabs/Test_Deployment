import sys
import io
import asyncio

from bots.discord_bot import run_discord
from bots.telegram_bot import run_telegram


async def main():
    print("[MAIN] Запуск ботів...")
    await asyncio.gather(
        run_discord(),
        run_telegram(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("[MAIN] Боти зупинені.")