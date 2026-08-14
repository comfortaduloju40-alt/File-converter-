"""
/start and /help command handlers.
"""

from telegram import Update
from telegram.ext import ContextTypes

from app.converters.office import EXTENSION_TARGETS
from app.logger import get_logger

logger = get_logger(__name__)

_HELP_TEXT = (
    "👋 Send me a document and I'll convert it for you.\n\n"
    "*Supported conversions:*\n"
    "• PDF → Word, Excel, PowerPoint\n"
    "• Word → PDF\n"
    "• Excel → PDF\n"
    "• PowerPoint → PDF\n\n"
    "Just upload a file as a *document* (not compressed as a photo) "
    "and I'll show you the available target formats."
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("New /start from %s", update.effective_user.id if update.effective_user else "unknown")
    await update.message.reply_text(_HELP_TEXT, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(_HELP_TEXT, parse_mode="Markdown")
