from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
import settings
from services import finnhub_connection
import json
import time
import logging

PERIOD = ['Year', 'Month', 'Week', 'Day']


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def error_handler(update, context):
    logger.warning(context.error)


def start_conversation(update, context):
    replies = [PERIOD]
    update.message.reply_text('Choose period for which you want to see earnings reports.',
                              reply_markup=ReplyKeyboardMarkup(replies, one_time_keyboard=True))
    return 'TICKER'


def ticker(update, context):
    context.user_data[update.message.from_user.id] = {'period': settings.PERIODS[update.message.text.upper()]}
    update.message.reply_text('Enter ticker. Or send /skip if you dont want to set up ticker.',
                              reply_markup=ReplyKeyboardRemove())
    return 'PROCESSING'


def skip_ticker(update, context):
    return 'PROCESSING'


def parse_reply_item(reply_item):
    reply_string = f"Date: {reply_item['date']} Ticker: {reply_item['symbol']}"
    return reply_string


def processing(update, context):
    if update.message.text != '/skip':
        context.user_data[update.message.from_user.id].update({'ticker': update.message.text})

    update.message.reply_text('Start processing. Wait for a while.')
    reply = json.loads(finnhub_connection(
        period=context.user_data[update.message.from_user.id]['period'],
        ticker=context.user_data[update.message.from_user.id].get('ticker')
    ))['earningsCalendar']

    if len(reply) != 0:
        for item in reply:
            update.message.reply_text(parse_reply_item(item))
            time.sleep(0.1)

    update.message.reply_text(f'Your report is ready. {len(reply)} items.')
    return ConversationHandler.END


def stop(update, context):
    update.message.reply_text('Conversation end. If you want to start new conversation send /start',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END