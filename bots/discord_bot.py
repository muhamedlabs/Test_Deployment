import sys
import io
from pathlib import Path
import time
import platform
import disnake
from disnake.ext import commands

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from BANNED_FILES.config import DISCORD_TOKEN, BOT_NAME, BOT_VERSION, BOT_AUTHOR

EMBED_COLOR = disnake.Color.from_rgb(88, 101, 242) 
START_TIME = time.time()


def _uptime_str() -> str:
    uptime_sec = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime_sec, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}г {minutes}хв {seconds}с"


def _build_bot() -> commands.InteractionBot:

    intents = disnake.Intents.default()
    intents.members = True
    intents.message_content = True  

    bot = commands.InteractionBot(intents=intents)

    @bot.event
    async def on_ready():
        print(f"[DISCORD] Бот {bot.user} запущений і готовий до роботи")

    @bot.slash_command(name="start", description="Показати статус та статистику бота")
    async def start_slash(inter: disnake.ApplicationCommandInteraction):
        t0 = time.time()
        await inter.response.defer(ephemeral=False)
        latency_ms = round((time.time() - t0) * 1000)

        total_members = sum(g.member_count or 0 for g in bot.guilds)

        embed = disnake.Embed(
            title=f"{BOT_NAME} — статус",
            description="Бот активний та готовий до роботи",
            color=EMBED_COLOR,
            timestamp=disnake.utils.utcnow(),
        )
        embed.add_field(name="Відклик", value=f"`{latency_ms} мс`", inline=True)
        embed.add_field(name="WebSocket", value=f"`{round(bot.latency * 1000)} мс`", inline=True)
        embed.add_field(name="Аптайм", value=f"`{_uptime_str()}`", inline=True)
        embed.add_field(name="Серверів", value=f"`{len(bot.guilds)}`", inline=True)
        embed.add_field(name="Користувачів", value=f"`{total_members}`", inline=True)
        embed.add_field(name="Версія", value=f"`{BOT_VERSION}`", inline=True)
        embed.add_field(name="Python", value=f"`{platform.python_version()}`", inline=True)
        embed.add_field(name="ОС", value=f"`{platform.system()} {platform.release()}`", inline=True)
        embed.set_footer(text=f"Автор: {BOT_AUTHOR} • Запит від {inter.author}")

        await inter.edit_original_response(embed=embed)

    @bot.slash_command(name="serverinfo", description="Інформація про поточний сервер")
    async def serverinfo_slash(inter: disnake.ApplicationCommandInteraction):
        guild = inter.guild
        if guild is None:
            await inter.response.send_message("Команда доступна лише на сервері.", ephemeral=True)
            return

        embed = disnake.Embed(
            title=f"Інформація про сервер: {guild.name}",
            color=EMBED_COLOR,
            timestamp=disnake.utils.utcnow(),
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="ID", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="Власник", value=f"<@{guild.owner_id}>", inline=True)
        embed.add_field(name="Учасників", value=f"`{guild.member_count}`", inline=True)
        embed.add_field(name="Каналів", value=f"`{len(guild.channels)}`", inline=True)
        embed.add_field(name="Ролей", value=f"`{len(guild.roles)}`", inline=True)
        embed.add_field(
            name="Створено",
            value=f"<t:{int(guild.created_at.timestamp())}:R>",
            inline=True,
        )
        embed.set_footer(text=f"Запит від {inter.author}")

        await inter.response.send_message(embed=embed)

    @bot.slash_command(name="userinfo", description="Інформація про користувача")
    async def userinfo_slash(
        inter: disnake.ApplicationCommandInteraction,
        користувач: disnake.Member = commands.Param(
            default=None, description="Кого перевірити (за замовчуванням — ви)"
        ),
    ):
        member = користувач or inter.author

        embed = disnake.Embed(
            title=f"Інформація про {member.display_name}",
            color=EMBED_COLOR,
            timestamp=disnake.utils.utcnow(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="ID", value=f"`{member.id}`", inline=True)
        embed.add_field(name="Бот", value="Так" if member.bot else "Ні", inline=True)
        embed.add_field(
            name="На сервері з",
            value=f"<t:{int(member.joined_at.timestamp())}:R>" if member.joined_at else "—",
            inline=True,
        )
        embed.add_field(
            name="Зареєстрований",
            value=f"<t:{int(member.created_at.timestamp())}:R>",
            inline=True,
        )
        top_role = member.top_role.mention if member.top_role else "—"
        embed.add_field(name="Найвища роль", value=top_role, inline=True)
        embed.add_field(name="Ролей", value=f"`{len(member.roles) - 1}`", inline=True)
        embed.set_footer(text=f"Запит від {inter.author}")

        await inter.response.send_message(embed=embed)

    @bot.slash_command(name="avatar", description="Показати аватар користувача")
    async def avatar_slash(
        inter: disnake.ApplicationCommandInteraction,
        користувач: disnake.Member = commands.Param(
            default=None, description="Чий аватар показати (за замовчуванням — ваш)"
        ),
    ):
        member = користувач or inter.author

        embed = disnake.Embed(
            title=f"Аватар {member.display_name}",
            color=EMBED_COLOR,
            timestamp=disnake.utils.utcnow(),
        )
        embed.set_image(url=member.display_avatar.url)
        embed.set_footer(text=f"Запит від {inter.author}")

        await inter.response.send_message(embed=embed)

    @bot.slash_command(name="help", description="Список усіх команд бота")
    async def help_slash(inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title=f"Команди {BOT_NAME}",
            color=EMBED_COLOR,
            timestamp=disnake.utils.utcnow(),
        )
        embed.add_field(name="/start", value="Статус та статистика бота", inline=False)
        embed.add_field(name="/serverinfo", value="Інформація про поточний сервер", inline=False)
        embed.add_field(name="/userinfo", value="Інформація про користувача", inline=False)
        embed.add_field(name="/avatar", value="Аватар користувача", inline=False)
        embed.add_field(name="/help", value="Цей список команд", inline=False)
        embed.set_footer(text=f"Автор: {BOT_AUTHOR}")

        await inter.response.send_message(embed=embed, ephemeral=True)

    return bot


async def run_discord():
    bot = _build_bot()
    await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    _build_bot().run(DISCORD_TOKEN)