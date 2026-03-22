"""
Slash command handlers — /ask, /image, /help, /summarize.
"""

from __future__ import annotations
import logging
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from utils.history import Interaction

logger = logging.getLogger(__name__)

# Maximum Discord message length
MAX_MSG_LEN = 2000


def _truncate(text: str, limit: int = MAX_MSG_LEN) -> str:
    """Truncate text to fit Discord's message limit."""
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


class SlashCommands(commands.Cog):
    """Discord slash commands for the GenAI bot."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── /help ────────────────────────────────────────────────────────────
    @app_commands.command(name="help", description="Show usage instructions")
    async def help_command(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="🤖 GenAI Bot — Help",
            description="I'm a hybrid AI assistant with **RAG** and **Vision** capabilities!",
            color=0x5865F2,
        )
        embed.add_field(
            name="📚 `/ask <query>`",
            value=(
                "Ask a question and I'll search my knowledge base to find the answer.\n"
                "**Example:** `/ask How do I reset my password?`"
            ),
            inline=False,
        )
        embed.add_field(
            name="🖼️ `/image`",
            value=(
                "Upload an image and I'll generate a caption and tags.\n"
                "**Usage:** `/image` then attach an image file."
            ),
            inline=False,
        )
        embed.add_field(
            name="📝 `/summarize`",
            value="Summarize your last interaction with me.",
            inline=False,
        )
        embed.add_field(
            name="ℹ️ `/help`",
            value="Show this help message.",
            inline=False,
        )
        embed.set_footer(
            text="Powered by Gemini + sentence-transformers | "
                 "Knowledge base: 5 docs"
        )
        await interaction.response.send_message(embed=embed)

    # ── /ask ─────────────────────────────────────────────────────────────
    @app_commands.command(name="ask",
                          description="Ask a question (RAG-powered)")
    @app_commands.describe(query="Your question")
    async def ask_command(self, interaction: discord.Interaction,
                          query: str) -> None:
        await interaction.response.defer(thinking=True)

        try:
            # Get conversation context
            conv_context = self.bot.history.format_for_prompt(
                interaction.user.id
            )

            # Run RAG pipeline
            answer, sources = await self.bot.retriever.query(
                query, conversation_context=conv_context
            )

            # Build response embed
            embed = discord.Embed(
                title="📚 Answer",
                description=_truncate(answer, 4096),
                color=0x57F287,
            )
            embed.set_author(
                name=f"Q: {query[:100]}",
                icon_url=interaction.user.display_avatar.url,
            )

            # Add source snippets
            if sources:
                source_text = "\n".join(
                    f"• **{s.source_file}** (relevance: {s.score:.0%})"
                    for s in sources
                )
                embed.add_field(
                    name="📄 Sources",
                    value=_truncate(source_text, 1024),
                    inline=False,
                )

            embed.set_footer(text="Powered by RAG | Gemini")

            await interaction.followup.send(embed=embed)

            # Save to history
            self.bot.history.add(
                interaction.user.id,
                Interaction(
                    query=query,
                    response=answer,
                    interaction_type="text",
                ),
            )

        except Exception as e:
            logger.error("Error in /ask: %s", e, exc_info=True)
            await interaction.followup.send(
                f"⚠️ Something went wrong: {e}"
            )

    # ── /image ───────────────────────────────────────────────────────────
    @app_commands.command(name="image",
                          description="Upload an image for captioning & tagging")
    @app_commands.describe(image="The image to analyse")
    async def image_command(self, interaction: discord.Interaction,
                            image: discord.Attachment) -> None:
        # Validate attachment
        if not image.content_type or not image.content_type.startswith("image/"):
            await interaction.response.send_message(
                "❌ Please attach a valid image file (PNG, JPG, WEBP).",
                ephemeral=True,
            )
            return

        await interaction.response.defer(thinking=True)

        try:
            # Download the image
            async with aiohttp.ClientSession() as session:
                async with session.get(image.url) as resp:
                    if resp.status != 200:
                        await interaction.followup.send(
                            "❌ Failed to download the image."
                        )
                        return
                    image_bytes = await resp.read()

            # Analyse
            result = await self.bot.vision.analyze_image(image_bytes)

            # Build response embed
            embed = discord.Embed(
                title="🖼️ Image Analysis",
                color=0xEB459E,
            )
            embed.set_thumbnail(url=image.url)
            embed.add_field(
                name="📝 Caption",
                value=result.caption,
                inline=False,
            )
            embed.add_field(
                name="🏷️ Tags",
                value=" • ".join(f"`{tag}`" for tag in result.tags),
                inline=False,
            )
            embed.set_footer(text="Powered by Gemini Vision")

            await interaction.followup.send(embed=embed)

            # Save to history
            self.bot.history.add(
                interaction.user.id,
                Interaction(
                    query="[Image uploaded]",
                    response=f"Caption: {result.caption} | Tags: {', '.join(result.tags)}",
                    interaction_type="image",
                    image_url=image.url,
                ),
            )

        except Exception as e:
            logger.error("Error in /image: %s", e, exc_info=True)
            await interaction.followup.send(
                f"⚠️ Something went wrong: {e}"
            )

    # ── /summarize ───────────────────────────────────────────────────────
    @app_commands.command(name="summarize",
                          description="Summarize your last interaction")
    async def summarize_command(self, interaction: discord.Interaction) -> None:
        last = self.bot.history.get_last(interaction.user.id)
        if not last:
            await interaction.response.send_message(
                "ℹ️ No previous interactions to summarize. "
                "Try `/ask` or `/image` first!",
                ephemeral=True,
            )
            return

        await interaction.response.defer(thinking=True)

        try:
            content = f"Query: {last.query}\nResponse: {last.response}"
            summary = await self.bot.llm.summarize(content)

            embed = discord.Embed(
                title="📝 Summary of Last Interaction",
                description=summary,
                color=0xFEE75C,
            )
            embed.add_field(
                name="Type",
                value=f"`{last.interaction_type}`",
                inline=True,
            )
            if last.interaction_type == "text":
                embed.add_field(
                    name="Original Query",
                    value=_truncate(last.query, 256),
                    inline=True,
                )
            embed.set_footer(text="Powered by Gemini")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error("Error in /summarize: %s", e, exc_info=True)
            await interaction.followup.send(
                f"⚠️ Something went wrong: {e}"
            )
