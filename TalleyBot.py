import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import json

# Define states for the conversation
ASK_NAME, CHOOSE_SPECIALTY = range(2)

def save_user_data(user_id, name, username, specialty):
    os.makedirs('data', exist_ok=True)
    file_path = 'data/user_data.json'

    try:
        with open(file_path, 'r') as file:
            users = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        users = []

    users.append({"user_id": user_id, "name": name, "username": username, "specialty": specialty})
    with open(file_path, 'w') as file:
        json.dump(users, file, indent=4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Welcome! What's your name?")
    return ASK_NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text
    context.user_data['name'] = name
    reply_keyboard = [['Neurology', 'Cardiology', 'Pediatrics'], ['Cancel']]
    await update.message.reply_text("Choose a specialty:", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return CHOOSE_SPECIALTY

async def choose_specialty(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    specialty = update.message.text
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    save_user_data(user_id, context.user_data['name'], username, specialty)
    await update.message.reply_text(f"Specialty {specialty} saved!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

def main():
    bot_token = 7248777740:AAFm2tNqMibOeXz48I4ICyE8OEJgWt5v_9s  # Use environment variable for the bot token
    application = Application.builder().token(bot_token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            CHOOSE_SPECIALTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_specialty)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    port = os.getenv('PORT', 5000)  # Use the PORT environment variable, default to 5000
    application.run_polling(allowed_updates=Update.ALL_TYPES, port=int(port))

if __name__ == '__main__':
    main()
