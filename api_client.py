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
        except ValueError:
            # print(response.text)
            print("Неверный формат JSON")
            return None
        except json.JSONDecodeError as e:
            print(f"Ошибка при декодировании JSON: {e}")
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


def add_order(api_key, service_id, link, quantity, runs=None, interval=None):
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
    params = {'key': api_key, 'service': service_id, 'link': link, 'quantity': quantity}
    if runs is not None:
        params['runs'] = runs
    if interval is not None:
        params['interval'] = interval

    return call_api(action, params)


def get_order_status(api_key, order_id):
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


api_key = config.api_key.get_secret_value()
service_list = get_service_list(api_key)
