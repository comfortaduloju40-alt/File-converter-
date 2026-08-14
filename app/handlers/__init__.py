
"""
Registers every command/message handler on the Application.
This is the ONLY place that should import from both start.py and convert.py,
so there's no risk of a circular import between handler modules.
"""

from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from app.handlers.convert import handle_conversion_callback, handle_document
from app.handlers.start import help_command, start_command


def register_handlers(app: Application) -> None:
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(handle_conversion_callback, pattern=r"^conv:"))
