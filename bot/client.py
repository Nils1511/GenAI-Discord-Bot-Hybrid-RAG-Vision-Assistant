"""
Discord bot client — sets up the bot, loads commands, and manages lifecycle.
"""

from __future__ import annotations
import logging
import discord
from discord.ext import commands

from rag.embedder import Embedder
from rag.vector_store import VectorStore
from rag.retriever import Retriever
from llm.generator import LLMGenerator
from vision.handler import VisionHandler
from utils.cache import QueryCache
from utils.history import HistoryManager
from config import DISCORD_TOKEN

logger = logging.getLogger(__name__)


class GenAIBot(commands.Bot):
    """Custom Discord bot with RAG + Vision capabilities."""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

        # ── Services ─────────────────────────────────────────────────────
        self.embedder = Embedder()
        self.vector_store = VectorStore()
        self.llm = LLMGenerator()
        self.vision = VisionHandler()
        self.cache = QueryCache()
        self.history = HistoryManager()

        self.retriever = Retriever(
            embedder=self.embedder,
            store=self.vector_store,
            llm=self.llm,
            cache=self.cache,
        )

    async def setup_hook(self) -> None:
        """Called when the bot is starting up — load cogs and index KB."""
        # Load slash commands
        from bot.commands import SlashCommands
        await self.add_cog(SlashCommands(self))

        # Index knowledge base
        count = self.retriever.index_knowledge_base()
        logger.info("Knowledge base ready with %d chunks.", count)

        # Sync slash commands with Discord
        synced = await self.tree.sync()
        logger.info("Synced %d slash commands.", len(synced))

    async def on_ready(self) -> None:
        logger.info("Bot is online as %s (ID: %s)", self.user, self.user.id)
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="/help for commands",
        )
        await self.change_presence(activity=activity)


def run_bot() -> None:
    """Entry point to start the bot."""
    if not DISCORD_TOKEN:
        raise RuntimeError(
            "DISCORD_TOKEN not set. Copy .env.example to .env and fill in your token."
        )
    bot = GenAIBot()
    bot.run(DISCORD_TOKEN, log_level=logging.INFO)
