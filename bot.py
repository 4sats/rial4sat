#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""Simple inline keyboard bot with multiple CallbackQueryHandlers.

This Bot uses the Application class to handle the bot.
First, a few callback functions are defined as callback query handler. Then, those functions are
passed to the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot that uses inline keyboard that has multiple CallbackQueryHandlers arranged in a
ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line to stop the bot.
"""
import logging, config, requests, aiohttp

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Stages
START_ROUTES, LIGHTNING, ONCHAIN, CARD = range(4)
# Callback data
ONE, TWO, THREE, FOUR = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    keyboard = [
        [
            InlineKeyboardButton("آنچین", callback_data="onchain")
            
        ],
        [
            InlineKeyboardButton("لایتنینگ⚡️", callback_data="lightning1")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    await update.message.reply_text("سلام با بات ما میتونی بیتکوینتو درجا به ریال تبدیل کنی بدون نیاز به احراز هویت\n برای شروع آنچین یا لایتنینگ رو انتخاب کنید", reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return START_ROUTES


async def lightning1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="لطف کنید میزان ساتوشی واریزیتونو برام بفرستین:(مثال: 1000)"
    )
    return LIGHTNING


async def lightning2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    amount = update.message.text
    data = {"out": False, "amount": int(amount), "memo": str(update.effective_user.id)}
    #x = requests.post("https://legend.lnbits.com/api/v1/payments", data='{"out": false, "amount": '+str(amount)+', "memo": "'+str(update.effective_user.id)+'"}', headers = {"X-Api-Key": config.READ_KEY, "Content-type": "application/json"})
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post("https://legend.lnbits.com/api/v1/payments", data='{"out": false, "amount": '+str(amount)+', "memo": "'+str(update.effective_user.id)+'"}', headers = {"X-Api-Key": config.READ_KEY, "Content-type": "application/json"}) as x:
            print(x.text)
            keyboard = [
                [
                    InlineKeyboardButton("پرداخت کردم", callback_data=str("ln"+x.json()["payment_hash"])),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(x.json()["payment_request"],reply_markup=reply_markup)
    return LIGHTNING

async def lightning3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="پرداخت انجام شد! حالا لطف کنید شماره کارت مد نظر را برای ما بفرستید:"
    )
    return CARD


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(lightning1, pattern="lightning1"),
            ],
            LIGHTNING: [
                MessageHandler(filters=filters.Regex("^\d+$"), callback=lightning2),
                CallbackQueryHandler(lightning3, pattern="^ln"),
            ],
            CARD: [
                
            ]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()