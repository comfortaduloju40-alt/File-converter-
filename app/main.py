"""
Bot entrypoint. Builds the Telegram Application, registers all handlers,
and starts polling (or a webhook, if WEBHOOK_URL is set).
"""

from telegram.ext import Application

from app.config import settings
from app.handlers import register_handlers
from app.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    app = Application.builder().token(settings.BOT_TOKEN).build()
    register_handlers(app)

    if settings.WEBHOOK_URL:
        logger.info("Starting bot in webhook mode at %s", settings.WEBHOOK_URL)
        app.run_webhook(
            listen="0.0.0.0",
            port=settings.PORT,
            url_path=settings.BOT_TOKEN,
            webhook_url=f"{settings.WEBHOOK_URL}/{settings.BOT_TOKEN}",
        )
    else:
        logger.info("Starting bot in polling mode")
        app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
