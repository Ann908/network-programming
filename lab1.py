from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

mode = "normal"

"""def menu(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Available commands:\n"
        "/menu - show menu\n"
        "/whisper - whisper mode\n"
        "/scream - scream mode\n"
    )"""

def whisper(update: Update, context: CallbackContext) -> None:
    global mode
    mode = "whisper"
    """update.message.reply_text("Whisper mode is on")"""
    update.callback_query.edit_message_text("Whisper mode is on", reply_markup=main_menu_keyboard())

def scream(update: Update, context: CallbackContext) -> None:
    global mode
    mode = "scream"
    """update.message.reply_text("Scream mode is on")"""
    update.callback_query.edit_message_text("Scream mode is on", reply_markup=main_menu_keyboard())

def echo(update: Update, context: CallbackContext) -> None:
    if mode == "whisper":
        text = update.message.text.lower()
    elif mode == "scream":
        text = update.message.text.upper()
    else:
        text = update.message.text
    update.message.reply_text(text)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(main_menu_message(), reply_markup=main_menu_keyboard())

def main_menu(update: Update, context: CallbackContext) -> None:
    global mode
    mode = "normal"
    update.callback_query.message.edit_text(main_menu_message(), reply_markup=main_menu_keyboard())

def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton("Menu", callback_data="m1")],
                [InlineKeyboardButton("Whisper", callback_data="m2")],
                [InlineKeyboardButton("Scream", callback_data="m3")]]
    return InlineKeyboardMarkup(keyboard)

def main_menu_message():
    return "Chose the option in the main menu:"

def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == "m1":
        main_menu(update, context)
    elif query.data == "m2":
        whisper(update, context)
    elif query.data == "m3":
        scream(update, context)

def unknown(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't recognized the command. Please, another one")

def main():
    updater = Updater("My_API_token")

    dispatcher = updater.dispatcher

    """dispatcher.add_handler(CommandHandler("menu", menu))
    dispatcher.add_handler(CommandHandler("whisper", whisper))
    dispatcher.add_handler(CommandHandler("scream", scream))"""

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()