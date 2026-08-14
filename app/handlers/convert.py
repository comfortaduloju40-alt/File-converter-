"""
Handles incoming documents: shows target-format buttons, then performs
the actual conversion when a button is tapped.
"""

import shutil
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.config import settings
from app.converters.office import ConversionError, convert_file, get_targets_for, make_job_dir
from app.logger import get_logger

logger = get_logger(__name__)

_PENDING_JOBS: dict[str, Path] = {}


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    doc = update.message.document
    if doc is None:
        return

    if doc.file_size and doc.file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        await update.message.reply_text(
            f"That file is too large. Max size is {settings.MAX_FILE_SIZE_MB} MB."
        )
        return

    extension = (doc.file_name or "").rsplit(".", 1)[-1].lower() if "." in (doc.file_name or "") else ""
    targets = get_targets_for(extension)
    if not targets:
        await update.message.reply_text(
            f"Sorry, I don't support converting `.{extension}` files yet.",
            parse_mode="Markdown",
        )
        return

    job_dir = make_job_dir()
    job_id = job_dir.name
    local_path = job_dir / doc.file_name

    tg_file = await doc.get_file()
    await tg_file.download_to_drive(custom_path=str(local_path))
    _PENDING_JOBS[job_id] = local_path

    buttons = [
        InlineKeyboardButton(fmt.upper(), callback_data=f"conv:{job_id}:{fmt}")
        for fmt in targets
    ]
    rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]

    await update.message.reply_text(
        "Convert to:",
        reply_markup=InlineKeyboardMarkup(rows),
    )


async def handle_conversion_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    try:
        _, job_id, target_format = query.data.split(":")
    except ValueError:
        await query.edit_message_text("Something went wrong with that request.")
        return

    source_path = _PENDING_JOBS.get(job_id)
    if source_path is None or not source_path.exists():
        await query.edit_message_text("This conversion request has expired. Please resend the file.")
        return

    await query.edit_message_text(f"Converting to {target_format.upper()}…")

    try:
        output_path = convert_file(source_path, target_format)
        with open(output_path, "rb") as f:
            await context.bot.send_document(chat_id=query.message.chat_id, document=f, filename=output_path.name)
    except ConversionError as exc:
        logger.exception("Conversion failed")
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"⚠️ {exc}")
    finally:
        _PENDING_JOBS.pop(job_id, None)
        shutil.rmtree(source_path.parent, ignore_errors=True)
