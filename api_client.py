import aiohttp
import requests
import json

from config_reader import config

API_URL = 'https://bestsmmlike.ru/api/v2'


def call_api(action, params, api_key=None):
    """
    Выполняет запрос к API
    :param action: действие, которое нужно выполнить
    :param params: параметры запроса
    :param api_key: ключ API (необязательно)
    :return: ответ от API в формате JSON, либо None в случае ошибки
    """
    url = f"{API_URL}?action={action}"
    headers = {}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    response = requests.post(url, data=params, headers=headers)

    if response.status_code == 200:
        try:
            json_response = response.json()
            if json_response:  # Проверяем, что ответ не пустой после декодирования JSON
                return json_response
            else:
                print("Пустой ответ от сервера")
                return None
        except json.JSONDecodeError as e:
            print(f"Ошибка при декодировании JSON: {e}")
            return None
        except ValueError:
            # print(response.text)
            print("Неверный формат JSON")
            return None
    else:
        print(f"Ошибка: {response.status_code}")
        # print(response.text)
        return None


async def get_service_list(api_key):
    """
    Получает список услуг
    :param api_key: ключ API
    :return: список услуг или None, если запрос не удался
    """
    params = {
        'key': api_key,
        'action': 'services'  # Добавляем параметр 'action' к параметрам запроса
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params) as response:
                if response.status == 200:
                    service_list_data = await response.json()
                    return service_list_data
                else:
                    print(f"Ошибка при выполнении запроса: {response.status}")
                    return None
    except aiohttp.ClientError as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None


async def add_order_default(api_key, service_id, link, quantity, runs=None, interval=None):
    """
    Добавляет заказ
    :param api_key: ключ API
    :param service_id: идентификатор услуги
    :param link: ссылка на страницу
    :param quantity: необходимое количество
    :param runs: количество запусков для доставки (необязательный параметр)
    :param interval: интервал в минутах (необязательный параметр)
    :return: идентификатор заказа
    """
    action = 'add'
    params = {'key': api_key,
              'service': service_id,
              'link': link,
              'quantity': quantity}
    if runs is not None:
        params['runs'] = runs
    if interval is not None:
        params['interval'] = interval

    return call_api(action, params)


async def add_order_package(api_key, service_id, link):
    """
    Добавляет заказ типа "Package"
    :param api_key: ключ API
    :param service_id: идентификатор услуги
    :param link: ссылка на страницу
    :return: идентификатор заказа
    """
    action = 'add'
    params = {'key': api_key,
              'service': service_id,
              'link': link}

    return call_api(action, params)


async def add_order_custom_comments(api_key, service_id, link, comments):
    """
    Добавляет заказ типа "Custom Comments"
    :param api_key: ключ API
    :param service_id: идентификатор услуги
    :param link: ссылка на страницу
    :param comments: список комментариев
    :return: идентификатор заказа
    """
    action = 'add'
    params = {'key': api_key,
              'service': service_id,
              'link': link,
              'comments': comments}

    return call_api(action, params)


async def add_order_mentions(api_key, service_id, link, quantity, usernames):
    """
    Добавляет заказ типа "Mentions"
    :param api_key: ключ API
    :param service_id: идентификатор услуги
    :param link: ссылка на страницу
    :param quantity: необходимое количество
    :param usernames: список пользователей
    :return: идентификатор заказа
    """
    action = 'add'
    params = {'key': api_key,
              'service': service_id,
              'link': link,
              'quantity': quantity,
              'usernames': usernames}

    return call_api(action, params)


async def add_order_mentions_with_hashtags(api_key, service_id, link, quantity, usernames, hashtags):
    """
    Добавляет заказ типа "Mentions with Hashtags"
    :param api_key: ключ API
    :param service_id: идентификатор услуги
    :param link: ссылка на страницу
    :param quantity: необходимое количество
    :param usernames: список пользователей
    :param hashtags: список хэштегов
    :return: идентификатор заказа
    """
    action = 'add'
    params = {'key': api_key,
              'service': service_id,
              'link': link,
              'quantity': quantity,
              'usernames': usernames,
              'hashtags': hashtags}

    return call_api(action, params)


async def add_order_mentions_custom_list(api_key, service_id, link, usernames):
    """
    Добавляет заказ типа "Mentions Custom List"
    :param api_key: ключ API
    :param service_id: идентификатор услуги
    :param link: ссылка на страницу
    :param usernames: список пользователей
    :return: идентификатор заказа
    """
    action = 'add'
    params = {'key': api_key,
              'service': service_id,
              'link': link,
              'usernames': usernames}

    return call_api(action, params)


async def add_order_mentions_hashtag(api_key, service_id, link, quantity, hashtag):
    """
    Добавляет заказ типа "Mentions Hashtag"
    :param api_key: ключ API
    :param service_id: идентификатор услуги
    :param link: ссылка на страницу
    :param quantity: необходимое количество
    :param hashtag: хэштег
    :return: идентификатор заказа
    """
    action = 'add'
    params = {'key': api_key,
              'service': service_id,
              'link': link,
              'quantity': quantity,
              'hashtag': hashtag}

    return call_api(action, params)


async def add_order_mentions_user_followers(api_key, service_id, link, quantity, username):
    """
    Добавляет заказ типа "Mentions User Followers"
    :param api_key: ключ API
    :param service_id: идентификатор услуги
    :param link: ссылка на страницу
    :param quantity: необходимое количество
    :param username: имя пользователя
    :return: идентификатор заказа
    """
    action = 'add'
    params = {'key': api_key,
              'service': service_id,
              'link': link,
              'quantity': quantity,
              'username': username}

    return call_api(action, params)


async def add_order_mentions_media_likers(api_key, service_id, link, quantity, media):
    """
    Добавляет заказ типа "Mentions Media Likers"
    :param api_key: ключ API
    :param service_id: идентификатор услуги
    :param link: ссылка на страницу
    :param quantity: необходимое количество
    :param media: ссылка на медиа
    :return: идентификатор заказа
    """
    action = 'add'
    params = {'key': api_key,
              'service': service_id,
              'link': link,
              'quantity': quantity,
              'media': media}

    return call_api(action, params)


async def add_order_custom_comments_package(api_key, service_id, link, comments):
    """
    Добавляет заказ типа "Custom Comments Package"
    :param api_key: ключ API
    :param service_id: идентификатор услуги
    :param link: ссылка на страницу
    :param comments: список комментариев
    :return: идентификатор заказа
    """
    action = 'add'
    params = {'key': api_key,
              'service': service_id,
              'link': link,
              'comments': comments}

    return call_api(action, params)


async def add_order_comment_likes(api_key, service_id, link, quantity, username):
    """
    Добавляет заказ типа "Comment Likes"
    :param api_key: ключ API
    :param service_id: идентификатор услуги
    :param link: ссылка на страницу
    :param quantity: необходимое количество
    :param username: имя пользователя, чей комментарий нужно лайкнуть
    :return: идентификатор заказа
    """
    action = 'add'
    params = {'key': api_key,
              'service': service_id,
              'link': link,
              'quantity': quantity,
              'username': username}

    return call_api(action, params)


async def add_order_poll(api_key, service_id, link, quantity, answer_number):
    """
    Добавляет заказ типа "Poll"
    :param api_key: ключ API
    :param service_id: идентификатор услуги
    :param link: ссылка на страницу с опросом
    :param quantity: необходимое количество голосов
    :param answer_number: номер ответа в опросе
    :return: идентификатор заказа
    """
    action = 'add'
    params = {'key': api_key,
              'service': service_id,
              'link': link,
              'quantity': quantity,
              'answer_number': answer_number}

    return call_api(action, params)


async def add_order_invites_from_groups(api_key, service_id, link, quantity, groups):
    """
    Добавляет заказ типа "Invites from Groups"
    :param api_key: ключ API
    :param service_id: идентификатор услуги
    :param link: ссылка на страницу
    :param quantity: необходимое количество
    :param groups: список групп
    :return: идентификатор заказа
    """
    action = 'add'
    params = {'key': api_key,
              'service': service_id,
              'link': link,
              'quantity': quantity,
              'groups': groups}

    return call_api(action, params)


async def add_order_subscriptions(api_key, service_id, username, min_quantity, max_quantity,
                                  posts=None, old_posts=None, delay=None, expiry=None):
    """
    Добавляет заказ типа "Subscriptions"
    :param api_key: ключ API
    :param service_id: идентификатор услуги
    :param username: имя пользователя
    :param min_quantity: минимальное количество
    :param max_quantity: максимальное количество
    :param posts: количество будущих постов для создания заказов
    :param old_posts: количество существующих постов для создания заказов
    :param delay: задержка в минутах
    :param expiry: дата истечения срока действия
    :return: идентификатор заказа
    """
    action = 'add'
    params = {'key': api_key,
              'service': service_id,
              'username': username,
              'min': min_quantity,
              'max': max_quantity}
    if posts is not None:
        params['posts'] = posts
    if old_posts is not None:
        params['old_posts'] = old_posts
    if delay is not None:
        params['delay'] = delay
    if expiry is not None:
        params['expiry'] = expiry

    return call_api(action, params)


async def get_order_status(api_key, order_id):
    """
    Получает статус заказа
    :param api_key: ключ API
    :param order_id: идентификатор заказа
    :return: информация о статусе заказа
    """
    action = 'status'
    params = {'key': api_key, 'order': order_id}

    return call_api(action, params)


def get_multiple_orders_status(api_key, order_ids):
    """
    Получает статус нескольких заказов
    :param api_key: ключ API
    :param order_ids: идентификаторы заказов (разделенные запятыми, до 100 IDs)
    :return: информация о статусах заказов
    """
    action = 'status'
    params = {'key': api_key, 'orders': order_ids}

    return call_api(action, params)


def create_refill(api_key, order_id):
    """
    Создает пополнение
    :param api_key: ключ API
    :param order_id: идентификатор заказа
    :return: идентификатор пополнения
    """
    action = 'refill'
    params = {'key': api_key, 'order': order_id}

    return call_api(action, params)


def create_multiple_refills(api_key, order_ids):
    """
    Создает несколько пополнений
    :param api_key: ключ API
    :param order_ids: идентификаторы заказов (разделенные запятыми, до 100 IDs)
    :return: информация о созданных пополнениях
    """
    action = 'refill'
    params = {'key': api_key, 'orders': order_ids}

    return call_api(action, params)


def get_refill_status(api_key, refill_id):
    """
    Получает статус пополнения
    :param api_key: ключ API
    :param refill_id: идентификатор пополнения
    :return: информация о статусе пополнения
    """
    action = 'refill_status'
    params = {'key': api_key, 'refill': refill_id}

    return call_api(action, params)


def get_multiple_refill_status(api_key, refill_ids):
    """
    Получает статус нескольких пополнений
    :param api_key: ключ API
    :param refill_ids: идентификаторы пополнений (разделенные запятыми, до 100 IDs)
    :return: информация о статусах пополнений
    """
    action = 'refill_status'
    params = {'key': api_key, 'refills': refill_ids}

    return call_api(action, params)


def create_cancel(api_key, order_ids):
    """
    Создает отмену заказов
    :param api_key: ключ API
    :param order_ids: идентификаторы заказов (разделенные запятыми, до 100 IDs)
    :return: информация о созданных отменах
    """
    action = 'cancel'
    params = {'key': api_key, 'orders': order_ids}

    return call_api(action, params)


def get_user_balance(api_key):
    """
    Получает баланс пользователя
    :param api_key: ключ API
    :return: информация о балансе пользователя
    """
    action = 'balance'
    params = {'key': api_key}

    return call_api(action, params)


user_api_key = config.user_api_key.get_secret_value()
service_list = get_service_list(user_api_key)
