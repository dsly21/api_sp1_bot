from dotenv import load_dotenv
import logging
import os
import requests
import telegram
import time

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

PRACTICUM_API_URL = 'https://praktikum.yandex.ru/api/user_api/{}'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if (homework_name is None) or (homework_status is None):
        return 'invalid server response'

    elif homework_status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = (
                    'Ревьюеру всё понравилось,'
                    ' можно приступать к следующему уроку.')

    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    url = PRACTICUM_API_URL.format('homework_statuses/')
    if current_timestamp is None:
        current_timestamp = time.time()
    params = {'from_date': current_timestamp}

    try:
        homework_statuses = requests.get(
                                        url,
                                        headers=HEADERS,
                                        params=params)
        return homework_statuses.json()
    except requests.exceptions.RequestException as err:
        logging.exception(err, "Exception occurred")
        return {}


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                            parse_homework_status
                            (new_homework.get('homeworks')[0]))

            current_timestamp = new_homework.get('current_date')
            time.sleep(300)
        except Exception as e:
            logging.exception(e, "Exception occurred")
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
