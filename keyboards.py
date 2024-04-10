import logging

from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from collections import defaultdict


from keyboa import Keyboa


# Определение клавиатур
# Клавиатура пагинации
class Pagination(CallbackData, prefix="pag"):
    action: str
    page: int


# Функции создания клавиатур
# Клавиатура основного меню
def create_main_menu_keyboard():
    # Создаем кнопки для каждого пункта меню
    button_service_list = KeyboardButton(text="💼 Перечень услуг накрутки")
    button_support_chat = KeyboardButton(text="🧑‍💻 Чат с поддержкой")
    button_my_profile = KeyboardButton(text="👤 Мой профиль")
    button_my_orders = KeyboardButton(text="📑 Мои заказы")
    button_balance_recharge = KeyboardButton(text="💰 Пополнить баланс")
    # Создаем разметку клавиатуры
    menu_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button_service_list, button_support_chat],
            [button_my_profile, button_my_orders],
            [button_balance_recharge]
        ],
        resize_keyboard=True
    )
    return menu_keyboard


# Клавиатуры 1 уровня - сервисы накрутки
def create_service_list_keyboard(service_list_data):
    try:
        # print("Начало создания клавиатуры")
        keyboard_list = []
        social_networks = set()
        # Получаем список социальных сетей из данных о сервисах
        for service_data in service_list_data:
            category = service_data.get('category')
            social_network = category.split('-')[0].strip().capitalize()
            # Исключаем добавление названий соцсетей с флагами стран
            if ord(social_network[0]) >= 127397:  # Проверяем, является ли первый символ символом флага страны
                social_network = social_network[2:].strip().capitalize()  # Удаляем символы флага страны
            social_networks.add(social_network)
        # Сортируем социальные сети по алфавиту
        sorted_networks = sorted(social_networks)
        max_buttons_per_chunk = 30  # Максимальное количество кнопок в каждом чанке
        chunks = [sorted_networks[i:i + max_buttons_per_chunk] for i in
                  range(0, len(sorted_networks), max_buttons_per_chunk)]
        # print(f"Количество клавиатур: {len(chunks)}")
        for i, chunk in enumerate(chunks):
            keyboard_buttons = []
            for network in chunk:
                button = InlineKeyboardButton(text=network, callback_data=f"network_{network.lower()}_firstkb")
                keyboard_buttons.append(button)
            keyboard_markup = InlineKeyboardBuilder()
            keyboard_markup.add(*keyboard_buttons)
            keyboard_markup.adjust(3)
            # Создаем кнопки пагинации
            pagination = paginator(page=i)  # Создаем пагинатор для текущей страницы
            # Добавляем кнопки пагинации к клавиатуре
            keyboard_markup.attach(pagination)
            # Теперь добавляем готовую клавиатуру в список
            keyboard_list.append(keyboard_markup)
        return keyboard_list
    except Exception as e:
        logging.error(f"Ошибка при создании клавиатуры: {e}")
        return None


# Клавиатуры 2 уровня - разделение сервисов накрутки по странам
def create_social_network_keyboards(service_list_data, received_callback):
    print('create_social_network_keyboards called')
    social_network_set = set()
    # Получаем список социальных сетей из данных о сервисах
    for service_data in service_list_data:
        category = service_data.get('category')
        social_network = category.split('-')[0].strip().capitalize()
        # Проверяем, содержит ли социальная сеть флаг страны
        if ord(social_network[0]) >= 127397:  # Проверяем, является ли первый символ символом флага страны
            social_network_set.add(social_network)
    # Собираем словарь с key - название соцсети, values - разделение по странам
    social_network_with_flags = list(social_network_set)
    social_network_dict = {}
    # Проходим по списку social_network_with_flags
    for network_with_flag in social_network_with_flags:
        # Получаем название социальной сети
        social_network = network_with_flag.split()[1]
        # Добавляем элемент в словарь
        if social_network not in social_network_dict:
            social_network_dict[social_network] = [network_with_flag]
        else:
            social_network_dict[social_network].append(network_with_flag)
    # Создаем клавиатуры второго уровня для каждой социальной сети
    second_level_keyboards = {}
    for social_network, values in social_network_dict.items():
        keyboard_items = []
        for value in values:
            # country_flag = value.split()[0]  # Получаем символ флага страны
            callback_data = f"&network={value}&{received_callback}"
            # print(callback_data)
            keyboard_items.append({
                'text': value,  # Просто используем значение как текст для кнопки
                'callback_data': callback_data
            })
        second_level_keyboards[social_network.lower()] = Keyboa(items=keyboard_items, front_marker="&secondkb=",
                                                                back_marker="$")
    return second_level_keyboards


# Клавиатуры 3 уровня - разделение по категориям
def create_third_level_keyboards(service_list_data):
    print('create_third_level_keyboards called')
    try:
        third_level_keyboards = {}

        # Собираем уникальные социальные сети и категории для каждой социальной сети

        social_network_categories = set()
        for service_data in service_list_data:
            category = service_data.get('category')
            social_network_categories.add(category)
        social_network_categories = sorted(social_network_categories)
        # print(social_network_categories)
        buttons_dict = defaultdict(list)
        for elements in social_network_categories:
            parts = elements.split(" - ")
            if len(parts) > 1:
                network_name = parts[0].strip().capitalize()
                network_category = parts[1].strip().capitalize()
                buttons_dict[network_name].append(network_category)
            else:
                network_name = parts[0]
                network_category = 'Услуги'
                buttons_dict[network_name].append(network_category)
        # print(buttons_dict)

        for social_network, categories in buttons_dict.items():
            keyboard_items = []
            for category in categories:
                callback_data = f"&nw={social_network.lower()}&cat={category.lower().strip()}"
                keyboard_items.append({
                    'text': category,
                    'callback_data': callback_data
                })
            third_level_keyboards[social_network.lower()] = Keyboa(items=keyboard_items,
                                                                   front_marker="&thirdkb=", back_marker="$")
        return third_level_keyboards
    except Exception as e:
        logging.error(f"Ошибка при создании клавиатур третьего уровня: {e}")
        return {}


# Клавиатуры 4 уровня - перечень услуг
async def create_fourth_level_keyboard(service_list_data, current_page=0):
    print("create_fourth_level_keyboard called")
    print("Current page:", current_page)

    max_item_per_page = 3  # Максимальное количество элементов на странице

    # Разделение списка услуг на страницы
    start_index = current_page * max_item_per_page
    end_index = start_index + max_item_per_page
    services_on_page = service_list_data[start_index:end_index]

    print("Services on page:", services_on_page)

    # Формирование текстового сообщения с информацией об услугах
    messages_and_keyboards = {}
    for service in services_on_page:
        print("Processing service:", service)
        category = service.get('category')
        if category not in messages_and_keyboards:
            messages_and_keyboards[category] = ("", InlineKeyboardBuilder())

        message_text = f"🔥 {service['name']} ❤️\n"
        message_text += f"🆔 ID услуги: {service['service']}\n"
        message_text += f"⬇️ Минимум для заказа: {service['min']}\n"
        message_text += f"⬆️ Максимум для заказа: {service['max']}\n"
        message_text += f"💸 Цена за 1к: {service['rate']}₽\n"
        message_text += f"📝 Описание: {service['name']}\n"

        messages_and_keyboards[category][0] += message_text + "\n\n"

    print("Messages and keyboards:", messages_and_keyboards)

    # Создание кнопок пагинации
    pagination_buttons = []
    if current_page > 0:
        pagination_buttons.append(
            InlineKeyboardButton(text="⬅️ Previous", callback_data=Pagination.new(action="prev", page=current_page))
        )
    if end_index < len(service_list_data):
        pagination_buttons.append(
            InlineKeyboardButton(text="Next ➡️", callback_data=Pagination.new(action="next", page=current_page))
        )

    # Создание кнопки "Назад"
    back_button = InlineKeyboardButton(text="Главное меню", callback_data="&button=prev")

    # Создание клавиатуры
    keyboard = InlineKeyboardBuilder()
    keyboard.add(back_button)
    keyboard.row(*pagination_buttons)
    keyboard.adjust(3)

    for _, data in messages_and_keyboards.items():
        data[1] = keyboard

    return messages_and_keyboards


# Вспомогательные функции

# Пагинатор
def paginator(page: int = 0):
    pagination_keyboard = InlineKeyboardBuilder()
    pagination_keyboard.add(
        InlineKeyboardButton(text="⬅ Previous", callback_data=Pagination(action="prev", page=page).pack()),
        InlineKeyboardButton(text="Next ➡", callback_data=Pagination(action="next", page=page).pack())
    )
    return pagination_keyboard