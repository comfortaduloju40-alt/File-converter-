import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
import replicate

# Setup logging
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me any low-res or blurry photo, and I'll enhance it with AI!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("⏳ Enhancing your image... Please wait.")
    
    try:
        # Get the highest resolution version of the user's uploaded photo
        photo_file = await update.message.photo[-1].get_file()
        photo_url = photo_file.file_path

        # Run AI model via Replicate API
        output = replicate.run(
            "nightmareai/real-esrgan:42fed1c49c551407b4d65942155fb41200734a173f081ce711e2eebe36435c2b",
            input={"image": photo_url, "scale": 2, "face_enhance": True}
        )

        # Send the enhanced photo back to the user
        await update.message.reply_photo(photo=str(output), caption="✨ Here is your enhanced photo!")
        await status_msg.delete()

    except Exception as e:
        logging.error(f"Error processing image: {e}")
        await status_msg.edit_text("❌ Failed to enhance the image. Please try again.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Run bot using polling mode
    app.run_polling()
