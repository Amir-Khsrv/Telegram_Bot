import json
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

# Define states for the conversation
ASK_NAME, CHOOSE_SPECIALTY = range(2)

# Function to save user data to a custom folder (e.g., data/)
def save_user_data(user_id, name, username, specialty):
    # Ensure the 'data' folder exists
    os.makedirs('data', exist_ok=True)
    
    # Define the path to the JSON file
    file_path = 'data/user_data.json'

    data = {
        "user_id": user_id,
        "name": name,
        "username": username,  # Save the username
        "specialty": specialty
    }
    
    # Load existing data from the file (if any)
    try:
        with open(file_path, 'r') as file:
            users = json.load(file)
    except FileNotFoundError:
        users = []

    # Append new data
    users.append(data)
    
    # Save back to the file
    with open(file_path, 'w') as file:
        json.dump(users, file, indent=4)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Cool welcome message with emojis
    welcome_message = """
    🎉 Welcome to **TalleyBot**! 🎉

    I'm your personal assistant 🤖, here to help you explore medical specialties! 🩺

    Please tell me your name so we can get started. 😊
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')
    return ASK_NAME

# Name input handler
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_name = update.message.text
    context.user_data['name'] = user_name
    
    # Creating a more detailed list of specialties
    specialty_list = [
        'Internal Medicine', 'Neurology', 'Cardiology', 'Pediatrics', 'Orthopedics', 
        'Dermatology', 'Psychiatry', 'General Surgery', 'Obstetrics and Gynecology',
        'Radiology', 'Pathology', 'Emergency Medicine', 'Anesthesia', 'Physical Examination'
    ]
    
    reply_keyboard = [specialty_list[i:i + 3] for i in range(0, len(specialty_list), 3)]  # Split into rows of 3 specialties each
    await update.message.reply_text(
        f"Hi {user_name}! Please choose a specialty from the list below: 👇",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CHOOSE_SPECIALTY

# Specialty selection handler
async def choose_specialty(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    specialty = update.message.text
    user_name = context.user_data.get('name', 'User')
    username = update.message.from_user.username  # Get the Telegram username
    context.user_data['specialty'] = specialty
    
    # Save user data to a JSON file
    save_user_data(update.message.from_user.id, user_name, username, specialty)
    
    # Sending a confirmation message
    await update.message.reply_text(f"Thank you, {user_name}! 🎉 You chose **{specialty}** as your specialty! 🩺")

    return ConversationHandler.END

# Cancel command handler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Goodbye! 👋 Stay healthy! 🩺")
    return ConversationHandler.END

def main() -> None:
    application = Application.builder().token("7248777740:AAFm2tNqMibOeXz48I4ICyE8OEJgWt5v_9s").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            CHOOSE_SPECIALTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_specialty)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    # Use polling instead of webhook
    application.run_polling()

if __name__ == '__main__':
    main()

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Default to port 5000 if PORT is not set
    app.run(host='0.0.0.0', port=port)
