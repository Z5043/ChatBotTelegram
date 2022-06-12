import logging
import requests
import telegram
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, Dispatcher,
                          InlineQueryHandler,
                          CallbackContext)

# Включить ведение журнала
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

reply_keyboard = [['Confirm', 'Restart']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

TOKEN = '5553718305:AAH9UGesym0CJXvz1gB7ZzEaQxkJsNlEEP0'
bot = telegram.Bot(token=TOKEN)

chat_id = '626302191'
chat_name = 'clothersfor'

LOCATION, PHOTO, GENDER, season, TIME, CONFIRMATION = range(6)


def facts_to_str(user_data):
    facts = list()
    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))
    return "\n".join(facts).join(['\n', '\n'])


def start(update, context):
    mess = f'Привет, {update.message.chat["first_name"]} {update.message.chat["last_name"]}!' \
           f' Я ваш помощник по размещению объявлений, который поможет пристроить ваши вещи нуждающимся. ' \
           f' Для начала, пожалуйста, введите ваш город.'
    update.message.reply_text(mess)
    return LOCATION


def location(update, context):
    user = update.message.from_user
    user_data = context.user_data
    category = 'Location'
    logger.info("Location of %s: %s", user.first_name, update.message.text)
    text = update.message.text
    user_data[category] = text
    update.message.reply_text(
        'Я записал. Теперь пришлите пожалуйста фото ваших вещей, это поможет быстрей найти им новых хозяев./skip')
    return PHOTO


def photo(update, context):
    user = update.message.from_user
    user_data = context.user_data
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    category = 'Photo Provided'
    user_data[category] = 'Yes'
    reply_keyboard_gender = [['Женские', 'Мужские']]
    markup_gender = ReplyKeyboardMarkup(reply_keyboard_gender, resize_keyboard=True, one_time_keyboard=True)
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Отлично! Теперь давайте опишем ваши вещи.Вещи женские или мужские?', reply_markup=markup_gender)
    return GENDER


def skip_photo(update, context):
    user = update.message.from_user
    user_data = context.user_data
    category = 'Photo Provided'
    user_data[category] = 'No'
    reply_keyboard_gender = [['Женские', 'Мужские']]
    markup_gender = ReplyKeyboardMarkup(reply_keyboard_gender, resize_keyboard=True, one_time_keyboard=True)
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text('Ну ни чего.Теперь давайте опишем ваши вещи.Вещи женские или мужские?',
                              reply_markup=markup_gender)

    return GENDER


def gender(update, context):
    user = update.message.from_user
    user_data = context.user_data
    category = 'Gender'
    reply_keyboard_season = [['Лето', 'Осень', 'Зима', 'Весна']]
    markup_season = ReplyKeyboardMarkup(reply_keyboard_season, resize_keyboard=True, one_time_keyboard=True)
    text = update.message.text
    user_data[category] = text
    logger.info("Gender: %s", update.message.text)
    update.message.reply_text('Ваши вещи на какой сезон?', reply_markup=markup_season)
    return season


def season(update, context):
    user = update.message.from_user
    user_data = context.user_data
    category = 'Season'
    text = update.message.text
    user_data[category] = text
    logger.info("Season: %s", update.message.text)
    update.message.reply_text('Во сколько можно приезжать за вещами?')
    return TIME


def time(update, context):
    user = update.message.from_user
    user_data = context.user_data
    category = 'Time to Take'
    text = update.message.text
    user_data[category] = text
    logger.info("Time to Take: %s", update.message.text)
    update.message.reply_text(
        "Спасибо вам за предоставленную информацию! Пожалуйста, проверьте правильность предоставленной информации:"
        "{}".format(facts_to_str(user_data)), reply_markup=markup)

    return CONFIRMATION


def confirmation(update, context):
    user_data = context.user_data
    user = update.message.from_user
    geocode_result = (user_data['Location'])
    headers = {"Accept-Language": "ru"}
    address = requests.get(
        f'https://eu1.locationiq.com/v1/search.php?key=pk.358e32b88ccc771b2e94265f80f8c3a1&q={geocode_result}&format=json',
        headers=headers).json()
    latitude = address[0]['lat']
    longitude = address[0]['lon']
    update.message.reply_text("Спасибо! Я буду размещать информацию на канале @" + chat_name + ".",
                              reply_markup=ReplyKeyboardRemove())
    if (user_data['Photo Provided'] == 'Yes'):
        del user_data['Photo Provided']
        bot.send_photo(chat_id=chat_id, photo=open('user_photo.jpg', 'rb'),
                       caption="<b>Есть вещи!</b> Информация: \n {}".format(
                           facts_to_str(user_data)) +
                               "\n Подробно от, {}".format(user.name),
                       parse_mode=telegram.ParseMode.HTML)
        bot.send_location(chat_id=chat_id, latitude=latitude, longitude=longitude)
    else:
        del user_data['Photo Provided']
        bot.sendMessage(chat_id=chat_id,
                        text="<b>Есть вещи!</b> Информация:  \n {}".format(
                            facts_to_str(user_data)) +
                             "\n Подробно от,  {}".format(user.name),
                        parse_mode=telegram.ParseMode.HTML)
        bot.send_location(chat_id=chat_id, latitude=latitude, longitude=longitude)
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Пока! Надеюсь увидеть вас снова.',
                              reply_markup=ReplyKeyboardRemove())


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={

            LOCATION: [CommandHandler('start', start), MessageHandler(Filters.text, location)],

            PHOTO: [CommandHandler('start', start), MessageHandler(Filters.photo, photo),
                    CommandHandler('skip', skip_photo)],

            GENDER: [CommandHandler('start', start), MessageHandler(Filters.text, gender)],

            season: [CommandHandler('start', start), MessageHandler(Filters.text, season)],

            TIME: [CommandHandler('start', start), MessageHandler(Filters.text, time)],

            CONFIRMATION: [MessageHandler(Filters.regex('^Confirm$'),
                                          confirmation),
                           MessageHandler(Filters.regex('^Restart$'),
                                          start)]
        }
        ,
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    # лог всех ошибок
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
