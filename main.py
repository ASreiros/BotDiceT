import os
import random
# pip install python-telegram-bot
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

print('Starting up bot...')

TOKEN = os.environ.get("BOT_TOKEN")
BOT_USERNAME = '@DiceRollerD20_bot'

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Lets roll some dices. Type /roll, /help or /list for full list of commands')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Try typing /roll (/r) or /rolls (/s) and I will provide keyboard for rolling. You can also try writing something similar to 3d8. Or d and dd for d20. For full list of commands try /list')

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    list_commands = "Below is the list of my commands: \n \n"
    command_data = {
        "/start": "Gives greetings",
        "/help": "gives description of bot functionality",
        "/list": "Gives list of commands",
        "/d": "Rolls 1d20",
        "/roll": "Gives keyboard with availible dices. For example 1d8",
        "/r": "Short for /roll",
        "/rolls": "Gives keyboard with multiple dices. For example 5d4",
        "/s": "Short for /rolls",
        "d": "Rolls 1d20",
        "dd": "Rolls 2d20",
        "other": "You also can just type number of valid dices to roll and I will roll if i will understand you. For example 3d12"
    }
    for key, value in command_data.items():
        list_commands += f"{key}: {value} \n"
    await update.message.reply_text(list_commands)

async def d_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = roll_dice([1, 20])
    await update.message.reply_text(text)

def roll_dice(values):
    result = ""
    number_of_dices = int(values[0])
    rolls = []
    text = f"You rolled {values[0]}d{values[1]}. "

    if int(values[0]) == 0 or int(values[1]) == 0:
        text += "I'm polite, so I wont tell you how you should use that 0. But try to figure it out yourself."
        return text
    if int(values[0]) > 100:
        text += "I wont roll more then 100 dices. You do it."
        return text

    for n in range(number_of_dices):
        roll = random.randint(1, int(values[1]))
        rolls.append(roll)
    rolls.sort(reverse=True)
    for number in rolls:
        result += f"{number}  "
    text += f" Your result is: {result} \n"
    if int(values[1]) == 20:
        text += f"Best roll is {rolls[0]}, worst roll is {rolls[-1]}"
    else:
        text += f"Total is: {sum(rolls)}"
    return text

async def roll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("1d3", callback_data="1 3"),
            InlineKeyboardButton("1d4", callback_data="1 4"),
        ],
        [
            InlineKeyboardButton("1d6", callback_data="1 6"),
            InlineKeyboardButton("1d8", callback_data="1 8"),
        ],
        [
            InlineKeyboardButton("1d10", callback_data="1 10"),
            InlineKeyboardButton("1d12", callback_data="1 12"),
        ],
        [InlineKeyboardButton("1d20", callback_data="1 20")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)


async def rolls_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dices = [4, 6, 8, 10, 12, 20]
    keyboard = []
    for d in dices:
        line = []
        for n in range(1, 9):
            dice_button = InlineKeyboardButton(f"{n}d{d}", callback_data=f"{n} {d}")
            line.append(dice_button)
        keyboard.append(line)

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    await query.edit_message_text(text=roll_dice(query.data.split(" ")))


def handle_response(text: str) -> str:
    # Create your own response logic
    processed: str = text.lower()
    if processed == "d":
        return roll_dice([1, 20])
    if processed == "dd":
        return roll_dice([2, 20])

    if 'd' in processed:
        parts = processed.split("d")
        if not len(parts) == 2:
            return None
        if parts[0] == "":
            parts[0] = "1"
        if parts[1].isdigit() and parts[0].isdigit():
            return roll_dice(parts)
        else:
            return None
    else:
        return None



async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get basic info of the incoming message
    message_type: str = update.message.chat.type
    text: str = update.message.text

    response: str = handle_response(text)
    if response:
        await update.message.reply_text(response)
    else:
        return


# Log errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# Run the program
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('list', list_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('roll', roll_command))
    app.add_handler(CommandHandler('r', roll_command))
    app.add_handler(CommandHandler('rolls', rolls_command))
    app.add_handler(CommandHandler('s', rolls_command))
    app.add_handler(CommandHandler('d', d_command))
    app.add_handler(CallbackQueryHandler(button))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Log all errors
    app.add_error_handler(error)

    print('Polling...')
    # Run the bot
    app.run_polling(poll_interval=1)
