import discord
from discord.ext import commands
import aiohttp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GrokBot")

GROQ_API = "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"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


@bot.event
async def on_ready():
    logger.info(f"البوت شغال: {bot.user}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if not message.guild:
        return

    if bot.user.mentioned_in(message) and not message.mention_everyone:
        user_msg = message.content
        user_msg = user_msg.replace(f"<@{bot.user.id}>", "")
        user_msg = user_msg.replace(f"<@!{bot.user.id}>", "")
        user_msg = user_msg.strip()

        if not user_msg:
            await message.reply("منشنتني ليش؟ اكتب شيء")
            return

        async with message.channel.typing():
            response = await call_groq_api(user_msg)
            await message.reply(response)

    await bot.process_commands(message)


async def call_groq_api(user_msg: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",  # ← الموديل الجديد
        "messages": [
            {"role": "system", "content": "أنت بوت عربي ساخر وكوميدي، ردودك ذكية ولاذعة ومضحكة."},
            {"role": "user", "content": user_msg}
        ],
        "temperature": 0.9,
        "max_tokens": 600
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status != 200:
                    error_data = await resp.json()
                    logger.error(f"API Error: {error_data}")
                    return f"خطأ (كود: {resp.status})"
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Error: {e}")
        return "صار خطأ، جرب مرة ثانية"


@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"🏓 البنق: **{round(bot.latency * 1000)}ms**")


bot.run("MTQ3MTEwMTI1NTk0OTYxOTM1Mw.GH1c-v.JxtC1xBx4POKSsl9cuDJedC12Xfbti0raZDxPU")
