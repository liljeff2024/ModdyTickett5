from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
import json
import asyncio
import traceback

# ============================================
#   CARGAR ENV
# ============================================
load_dotenv()

# Forzar a discord.py a NO usar aiohttp
discord.http._set_default_http_client("httpx")

# TOKEN desde entorno
TOKEN = os.getenv("TOKEN")

# ============================================
#   CARGAR CONFIG
# ============================================
with open("data/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# TOKEN desde Render (sobrescribe el del config.json)
TOKEN = os.getenv("TOKEN") or config["TOKEN"]

# ============================================
#   INTENTS Y BOT
# ============================================
intents = discord.Intents.all()

class TicketBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=";",
            intents=intents
        )
        self.remove_command("help")

    async def setup_hook(self):
        cogs = [
            "cogs.tickets",
            "cogs.panels",
            "cogs.logs",
            "cogs.config"
        ]

        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"📦 COG cargado: {cog}")
            except Exception:
                print(f"\n❌ ERROR cargando {cog}:")
                traceback.print_exc()

        # Registrar vistas persistentes
        try:
            from cogs.tickets import VistaCierreFinal
            self.add_view(VistaCierreFinal())
            print("🔗 VistaCierreFinal registrada.")
        except Exception:
            print("❌ Error registrando VistaCierreFinal:")
            traceback.print_exc()

        try:
            from cogs.panels import cargar_paneles, VistaPanel
            data = cargar_paneles()

            for guild_id, guild_panels in data.items():
                for panel_id, panel in guild_panels.items():
                    self.add_view(VistaPanel(panel_id, panel))

            print("🔗 Vistas persistentes de paneles registradas.")
        except Exception:
            print("❌ Error registrando vistas de paneles:")
            traceback.print_exc()

        # Sincronizar comandos
        try:
            synced = await self.tree.sync()
            print(f"🔧 {len(synced)} comandos sincronizados.")
        except Exception:
            print("❌ Error sincronizando comandos:")
            traceback.print_exc()


bot = TicketBot()

# ============================================
#   EVENTO ON_READY
# ============================================
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

# ============================================
#   SISTEMA DE ERRORES
# ============================================
@bot.event
async def on_command_error(ctx, error):
    print("\n❌ ERROR EN COMANDO:")
    traceback.print_exc()
    try:
        await ctx.reply("❌ Ocurrió un error ejecutando este comando.")
    except:
        pass

@bot.tree.error
async def on_app_command_error(interaction, error):
    print("\n❌ ERROR EN SLASH COMMAND:")
    traceback.print_exc()
    try:
        await interaction.response.send_message(
            "❌ Ocurrió un error ejecutando este comando.",
            ephemeral=True
        )
    except:
        pass

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"\n❌ ERROR EN EVENTO: {event}")

    if args:
        interaction = args[0]
        if isinstance(interaction, discord.Interaction):
            print("🔍 Tipo: Error en botón / select / modal")
            print(f"Usuario: {interaction.user}")
            print(f"Datos: {interaction.data}")

    traceback.print_exc()

# ============================================
#   MAIN
# ============================================
async def main():
    try:
        async with bot:
            await bot.start(TOKEN)
    except Exception:
        print("\n❌ ERROR AL INICIAR EL BOT:")
        traceback.print_exc()

# ============================================
#   EJECUTAR BOT
# ============================================
asyncio.run(main())
