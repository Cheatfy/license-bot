import json
import os
from datetime import datetime
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# === BOT CONFIGURATION ===
BOT_TOKEN = os.getenv("8404505015:AAFy76LCWxvfIdx0Ka9R9D659kIXJyh-qaI")
ADMIN_ID = int(os.getenv("ADMIN_ID", "5244201431"))  # default to your ID if env var missing

DB_FILE = "keys_data.json"

# === LOAD / SAVE KEYS DATABASE ===
def load_keys():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    else:
        # default sample key
        return {
            "P012PP012": {"license": "XPP012MKLA", "game": "XYZ", "duration": "24H", "used": False},
        }

def save_keys(keys):
    with open(DB_FILE, "w") as f:
        json.dump(keys, f, indent=4)

KEYS = load_keys()

# === COMMAND: /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🎟️ Get Keys!"), KeyboardButton("ℹ️ How To Use")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "👋 Welcome to the License Bot!\nChoose an option below 👇",
        reply_markup=reply_markup,
    )

# === ADMIN COMMAND: /addkey ===
async def add_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    try:
        args = context.args
        if len(args) < 4:
            await update.message.reply_text("⚠️ Usage: /addkey <customer_key> <license_key> <game> <duration>")
            return

        customer_key, license_key, game, duration = args[0], args[1], args[2], args[3]
        KEYS[customer_key] = {
            "license": license_key,
            "game": game,
            "duration": duration,
            "used": False,
        }
        save_keys(KEYS)
        await update.message.reply_text(f"✅ Key added:\n{customer_key} → {license_key} ({game}, {duration})")

    except Exception as e:
        await update.message.reply_text(f"❌ Error adding key: {e}")

# === HANDLE BUTTONS & KEYS ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    now = datetime.now()
    date = now.strftime("%Y/%m/%d")
    time = now.strftime("%I:%M %p")

    # Handle main menu buttons
    if text == "🎟️ Get Keys!":
        await update.message.reply_text("🔑 Please send your customer key below to get your license.")
        return

    if text == "ℹ️ How To Use":
        await update.message.reply_text(
            "📘 *How To Use*\n\n"
            "1️⃣ Tap '🎟️ Get Keys!'\n"
            "2️⃣ Send your provided customer key (e.g., `P012PP012`)\n"
            "3️⃣ Receive your license key instantly!\n\n"
            "Each key can be used only once.",
            parse_mode="Markdown",
        )
        return

    # Handle key verification
    if text in KEYS:
        key_info = KEYS[text]
        if not key_info["used"]:
            response = (
                f"Game : {key_info['game']} / Key Duration {key_info['duration']}\n"
                f"License KEY : {key_info['license']}\n"
                f"Available for 1 Devices\n"
                f"Duration will start when license login.\n\n"
                f"Date {date}\nTime {time}"
            )
            key_info["used"] = True
            save_keys(KEYS)
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("❌ This key has already been used.")
    else:
        await update.message.reply_text("❗ Invalid key. Please check and try again.")

# === MAIN ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addkey", add_key))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 License Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
